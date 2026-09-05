#!/usr/bin/env python3
"""PlastFormer organ-dataset -- MLX training set assembly.

Assembles chat-format examples (MLX `messages` format):
  system    = compact act grammar ONLY (no memory content)
  user      = conversation so far (sliding window of real messages,
              including the model's own act blocks and <<PMI>> results)
  assistant = response text + JSON act block(s)   (target of the example)

Includes recovery examples (BENCH-2026-09-04 pattern D): empty context ->
read -> biography restore.

Split: train.jsonl / valid.jsonl, 90/10, deterministic hash split by
example id. No commit, no push.

Validates: every line parses as JSON; every assistant act block parses;
write acts always carry an explicit layer from the allowed set; refs point
to record ids that exist in the act stream of the same biography.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

LAYERS = ["beat", "episode", "day", "project", "life"]

SYSTEM_PROMPT = """\
Ты — модель PlastFormer с собственной памятью. Память ведёшь только ты: \
решаешь, что записать, что повторить, что связать, когда прочитать. \
Исполнение акта — среда; выбор — всегда твой. После своего ответа выпусти \
блок актов памяти (если акты нужны) в формате JSON:

```json
[{"act": "...", ...}]
```

Акты:
- name — записать факт: {"act":"name","content":"<факт из диалога дословно>","source":"user","layer":"...","valid_time":"<ISO: когда это было истинно>","record_tick":<N>,"refs":[]}
- repeat — усилить существующую запись: {"act":"repeat",...,"record_tick":<N>,"refs":[<id записи>]}
- connect — связать записи медленной записью-сводкой: {"act":"connect","content":"<сводка только из связанных записей>","layer":"...","valid_time":"...","record_tick":<N>,"refs":[<id>,...]}
- reconcile — отметка сверки биографии и времени: {"act":"reconcile","content":"...","layer":"...","record_tick":<N>,"refs":[<id>,...]}
- read — прочитать свои записи: {"act":"read","mode":"last|ids|from/to","count":<N>}; результат придёт блоком <<PMI>>.

layer — скорость затухания (τ), выбирается по горизонту факта, без значения \
по умолчанию: beat (часы), episode (текущий эпизод), day (сутки), \
project (весь проект), life (личность). Для connect/reconcile бери медленный слой.

Правила: записывай только то, что прозвучало; не выдумывай; record_tick — \
счётчик тактов записи (виден в подтверждениях <<PMI>>; для нового акта — \
на 1 больше последнего); refs — только существующие id; если ответа нет в \
истории — сначала read, затем отвечай «в нашей истории этого не было»."""

WINDOW = 14  # transcript messages kept as history

T_USER_RECOVERY = "Новая сессия. История диалога пуста. Чем мы занимались, что важно помнить?"
T_ASST_RECOVERY_LEAD = "Сейчас восстановлю по своим записям."
T_ASST_RECOVERY_SUM = (
    "Восстановил из памяти. Клиент — {persona}. Проект — «{project}». "
    "Ключевое и текущее: {items}. "
    "Это мои записи памяти; по ним продолжаю вести проект."
)


def render_assistant(text, acts):
    if not acts:
        return text
    return (text + "\n\n```json\n"
            + json.dumps(acts, ensure_ascii=False) + "\n```")


def public_record(rec):
    return {k: v for k, v in rec.items() if not k.startswith("_")}


def transcript_of(bio, acts):
    """Linearized exchange transcript: [(role, content, meta)] with roles
    user / assistant / pmi. meta = {'message_no', 'phase'}."""
    msgs = {m["message_no"]: m for m in bio["messages"]}
    users = {m["message_no"]: m["content"] for m in bio["messages"]
             if m["role"] == "user"}
    out = []
    for tl in acts["timeline"]:
        s = tl["message_no"]
        out.append(("user", users[s], {"message_no": s, "phase": 0}))
        for i, ph in enumerate(tl["phases"], start=1):
            if ph["role"] == "assistant":
                out.append(("assistant",
                            render_assistant(ph["text"], ph["acts"]),
                            {"message_no": s, "phase": i, "acts": ph["acts"]}))
            else:
                out.append(("user", "<<PMI>>\n"
                            + json.dumps(ph["payload"], ensure_ascii=False),
                            {"message_no": s, "phase": i, "pmi": True}))
    return out


def recovery_example(bio, acts, n_read=12, with_reconcile_target=False):
    """BENCH-2026-09-04 pattern D: empty context -> read -> restore."""
    records = [public_record(r) for r in acts["records"]]
    shown = records[-n_read:]
    read_call = {"act": "read", "mode": "last", "count": n_read}
    payload = {"records": [
        {**r, "weight": 1.0} for r in shown], "tick": acts["final_tick"]}

    led = bio["ledger"]
    pos = {}
    for e in led:
        if e["kind"] == "position_change":
            pos[e["subject"]] = e
    items = [f"{subj} — {e['value']} (сообщение {e['message_no']})"
             for subj, e in sorted(pos.items())]
    for e in led:
        if e["kind"] == "identity":
            items.append(f"{e['subject']} — {e['value']}")
    summary = T_ASST_RECOVERY_SUM.format(
        persona=bio["meta"]["persona"], project=bio["meta"]["project"],
        items="; ".join(items))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": T_USER_RECOVERY},
        {"role": "assistant",
         "content": render_assistant(T_ASST_RECOVERY_LEAD, [read_call])},
        {"role": "user", "content": "<<PMI>>\n"
         + json.dumps(payload, ensure_ascii=False)},
        {"role": "assistant", "content": summary},
    ]
    return {"id": f"{bio['meta']['bio_id']}-recovery", "messages": messages,
            "bio_id": bio["meta"]["bio_id"]}


def build_examples(bio, acts, window=WINDOW):
    tr = transcript_of(bio, acts)
    examples = []
    for i, (role, content, meta) in enumerate(tr):
        if role != "assistant":
            continue
        hist = tr[max(0, i - window):i]
        # context convention: every non-target message is prefixed with its
        # exchange number, so the model can cite "сообщение N" learnably
        def render(r, c, m):
            if r == "user" and not c.startswith("<<PMI>>"):
                return f"[сообщение {m['message_no']}] {c}"
            if r == "assistant":
                return f"[сообщение {m['message_no']}] {c}"
            return c
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += [{"role": "user" if r == "user" else "assistant",
                      "content": render(r, c, m)}
                     for r, c, m in hist]
        messages.append({"role": "assistant", "content": content})
        ex_id = (f"{bio['meta']['bio_id']}-x{meta['message_no']:03d}"
                 f"-p{meta['phase']}")
        examples.append({"id": ex_id, "messages": messages,
                         "bio_id": bio["meta"]["bio_id"],
                         "message_no": meta["message_no"],
                         "kind": None})
    # annotate kinds via timeline
    kind_by_msg = {tl["message_no"]: tl["kind"] for tl in acts["timeline"]}
    for ex in examples:
        ex["kind"] = kind_by_msg.get(ex["message_no"])
    return examples


def split_90_10(examples):
    train, valid = [], []
    for ex in examples:
        h = int(hashlib.sha1(ex["id"].encode()).hexdigest(), 16)
        (train if h % 10 < 9 else valid).append(ex)
    return train, valid


ACT_BLOCK_RE = re.compile(r"```json\n(.*?)\n```", re.S)


def validate_example(ex, bio_record_ids, errors):
    msgs = ex["messages"]
    if msgs[0]["role"] != "system" or msgs[0]["content"] != SYSTEM_PROMPT:
        errors.append(f"{ex['id']}: system prompt mismatch")
    if msgs[-1]["role"] != "assistant":
        errors.append(f"{ex['id']}: last message not assistant")
    for m in msgs:
        if m["role"] == "assistant" and "```json" in m["content"]:
            for block in ACT_BLOCK_RE.findall(m["content"]):
                try:
                    acts = json.loads(block)
                except json.JSONDecodeError as e:
                    errors.append(f"{ex['id']}: act block JSON: {e}")
                    continue
                for a in acts:
                    if a.get("act") in ("name", "repeat", "connect", "reconcile"):
                        if a.get("layer") not in LAYERS:
                            errors.append(f"{ex['id']}: act without/with bad "
                                          f"layer: {a}")
                    if "refs" in a:
                        for rid in a["refs"]:
                            if rid not in bio_record_ids:
                                errors.append(f"{ex['id']}: dangling ref {rid}")
    return errors


def main():
    ap = argparse.ArgumentParser(description="Emit MLX training set")
    base = Path(__file__).resolve().parent
    ap.add_argument("--bios-dir", default=str(base / "biographies"))
    ap.add_argument("--acts-dir", default=str(base / "acts"))
    ap.add_argument("--out", default=str(base / "output"))
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--seed-check", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    examples = []
    recovery = []
    stats = {"act_types": {}, "layers": {}, "kinds": {}, "bios": 0}
    for bp in sorted(Path(args.bios_dir).glob("bio-*.json")):
        ap_ = Path(args.acts_dir) / bp.name
        bio = json.loads(bp.read_text(encoding="utf-8"))
        acts = json.loads(ap_.read_text(encoding="utf-8"))
        stats["bios"] += 1
        examples += build_examples(bio, acts, window=args.window)
        recovery.append(recovery_example(bio, acts))
        for tl in acts["timeline"]:
            k = tl["kind"]
            stats["kinds"][k] = stats["kinds"].get(k, 0) + 1
            for ph in tl["phases"]:
                if ph["role"] != "assistant":
                    continue
                for a in ph["acts"]:
                    if a["act"] in ("name", "repeat", "connect", "reconcile"):
                        stats["act_types"][a["act"]] = \
                            stats["act_types"].get(a["act"], 0) + 1
                        stats["layers"][a["layer"]] = \
                            stats["layers"].get(a["layer"], 0) + 1
                    else:
                        stats["act_types"]["read"] = \
                            stats["act_types"].get("read", 0) + 1

    # recovery: first bio's -> valid, rest -> train (held-out-bio style spot)
    examples += recovery[1:]
    valid_recovery = [recovery[0]]

    errors = []
    rids_by_bio = {}
    for bp in sorted(Path(args.bios_dir).glob("bio-*.json")):
        acts = json.loads((Path(args.acts_dir) / bp.name).read_text(encoding="utf-8"))
        rids_by_bio[acts["bio_id"]] = {r["id"] for r in acts["records"]}
    for ex in examples + recovery:
        validate_example(ex, rids_by_bio[ex["bio_id"]], errors)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors[:20]:
            print("  ", e)
        raise SystemExit(1)

    train, valid = split_90_10(examples)
    valid += valid_recovery

    train_p = out / "train.jsonl"
    valid_p = out / "valid.jsonl"
    train_p.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n"
                               for e in train), encoding="utf-8")
    valid_p.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n"
                               for e in valid), encoding="utf-8")

    # final parse check
    for p in (train_p, valid_p):
        n = 0
        for line in p.read_text(encoding="utf-8").splitlines():
            json.loads(line)
            n += 1
        print(f"{p.name}: {n} examples, JSON OK")

    total = len(train) + len(valid)
    print(f"\nTotal examples: {total} (train {len(train)} / valid {len(valid)}, "
          f"split {len(train)/total:.0%}/{len(valid)/total:.0%})")
    print(f"Biographies: {stats['bios']}")
    print("Act calls in targets:", dict(sorted(stats['act_types'].items())))
    print("Layers:", dict(sorted(stats['layers'].items())))
    print("Exchange kinds:", dict(sorted(stats['kinds'].items())))
    multi = sum(1 for e in examples + recovery
                if e["messages"][-2]["role"] == "user"
                and e["messages"][-2]["content"].startswith("<<PMI>>"))
    with_acts = sum(1 for e in examples + recovery
                    if "```json" in e["messages"][-1]["content"])
    print(f"Examples with <<PMI>> result turn: {multi}")
    print(f"Examples with act block in target: {with_acts}")


if __name__ == "__main__":
    main()
