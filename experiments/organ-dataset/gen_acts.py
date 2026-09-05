#!/usr/bin/env python3
"""PlastFormer organ-dataset -- act-stream generator (ground-truth demonstrations).

For each biography (gen_biography.py output) produces the target act stream
the model should emit: JSON act calls per the Matryoshka MMI record format.

Act vocabulary: name | repeat | connect | reconcile | read.
Act call fields: {act, content, source, layer, valid_time, record_tick, refs};
read carries {act, mode, count|ids} (it deposits no record, hence no layer).

Constitution compliance (CONSTITUTION.md P1-P10):
  * acts are decisions of the MODEL; in this dataset they are demonstrations
    (capacity scaffolding, legal per P9);
  * layers are chosen per-act from the tau semantics of the fact's horizon --
    never a default (P3);
  * timestamps are bi-temporal: valid_time (world) + record_time (learned),
    record_tick = stand counter advanced once per executed write act (P5/P6);
  * source class asserted by the model in the act call (P7);
  * no content beyond the ledger/record store: every act carries internal
    _fact_ids/_record_ids/_allowed_nums used by the self-validation.

Deterministic, pure stdlib. Output: acts/bio-XX.json
"""

import argparse
import json
import math
import re
from pathlib import Path

LAYERS = ["beat", "episode", "day", "project", "life"]
TAU_TICKS = {"beat": 10, "episode": 50, "day": 200,
             "project": 1000, "life": 5000}  # executor defaults, SPEC 3.2

T_READ_LEAD = [
    "Сейчас проверю по памяти.",
    "Сверюсь со своими записями.",
    "Прочитаю память.",
    "Проверю биографию проекта.",
]


def nums(s):
    """All digit runs in a string."""
    return set(re.findall(r"\d+", str(s)))


class BioActs:
    def __init__(self, bio):
        self.bio = bio
        self.ledger = {e["fact_id"]: e for e in bio["ledger"]}
        self.by_msg_kind = {}
        for e in bio["ledger"]:
            self.by_msg_kind.setdefault((e["message_no"], e["kind"]), []).append(e)
        self.records = []          # full record store (executor side)
        self.lid2rec = {}          # ledger fact_id -> record id
        self.tick = 0              # stand counter: +1 per executed write act
        self.timeline = []
        self.warnings = []

    # ---------------- record store ----------------
    def _append(self, act, content, layer, valid_time, record_time,
                source, refs, fact_ids, record_ids, allowed_nums):
        if act in ("name", "repeat", "connect", "reconcile"):
            self.tick += 1
        rec = {
            "id": len(self.records) + 1,
            "record_time": record_time,
            "valid_time": valid_time,
            "record_tick": self.tick,
            "layer": layer,
            "act": act,
            "content": content,
            "source": source,
            "refs": refs,
        }
        # internal (for validation / emit): underscore fields are stripped
        # from the training view
        rec["_fact_ids"] = fact_ids
        rec["_record_ids"] = record_ids
        rec["_message_no"] = record_time  # world time == exchange time
        rec["_allowed_nums"] = sorted(str(x) for x in allowed_nums)
        self.records.append(rec)
        return rec["id"]

    def act_name(self, subject, value, layer, ledger_e, message_no, world_time,
                 valid_time=None, refs=None, fact_ids=None, extra_content=None):
        content = extra_content or f"{subject} — {value}"
        nums_ok = nums(subject) | nums(value)
        for fid in (fact_ids or []):
            e = self.ledger.get(fid)
            if e:
                nums_ok |= nums(e["subject"]) | nums(e["value"])
        if valid_time is None:
            valid_time = ledger_e["valid_time"]
        rid = self._append(
            act="name", content=content, layer=layer,
            valid_time=valid_time, record_time=world_time,
            source="user", refs=refs or [],
            fact_ids=list(fact_ids or []) + [ledger_e["fact_id"]],
            record_ids=[r for r in (refs or [])],
            allowed_nums=nums_ok | nums(world_time))
        self.lid2rec[ledger_e["fact_id"]] = rid
        return rid

    def act_repeat(self, target_lid, subject, value, message_no, world_time,
                   fact_ids=None):
        target_rid = self.lid2rec[target_lid]
        target = self.records[target_rid - 1]
        rid = self._append(
            act="repeat",
            content=f"Повтор: {subject} — {value}",
            layer=target["layer"],  # informational: layer of the amplified record
            valid_time=world_time, record_time=world_time,
            source="repeat", refs=[target_rid],
            fact_ids=list(fact_ids or []),
            record_ids=[target_rid],
            allowed_nums=nums(subject) | nums(value) | nums(world_time))
        return rid

    def act_connect(self, content, layer, refs, message_no, world_time,
                    fact_ids=None, record_ids=None):
        nums_ok = nums(world_time)
        for rid in (record_ids or []):
            rec = self.records[rid - 1]
            nums_ok |= nums(rec["content"])
        for fid in (fact_ids or []):
            e = self.ledger.get(fid)
            if e:
                nums_ok |= nums(e["subject"]) | nums(e["value"]) | \
                    nums(e["message_no"]) | nums(e["world_time"])
        rid = self._append(
            act="connect", content=content, layer=layer,
            valid_time=world_time, record_time=world_time,
            source="connect", refs=list(refs),
            fact_ids=list(fact_ids or []),
            record_ids=list(record_ids or []) + list(refs),
            allowed_nums=nums_ok)
        return rid

    def act_reconcile(self, content, refs, world_time, fact_ids=None,
                      record_ids=None, extra_nums=None):
        rid = self._append(
            act="reconcile", content=content, layer="project",
            valid_time=world_time, record_time=world_time,
            source="reconcile", refs=list(refs),
            fact_ids=list(fact_ids or []),
            record_ids=list(record_ids or []) + list(refs),
            allowed_nums=nums(world_time) | set(extra_nums or []))
        return rid

    # ---------------- reads ----------------
    def weight(self, rec):
        repeats = sum(1 for r in self.records
                      if r["act"] == "repeat" and rec["id"] in r["refs"])
        dn = self.tick - rec["record_tick"]
        return round((1 + repeats) * math.exp(-dn / TAU_TICKS[rec["layer"]]), 3)

    def read_payload(self, recs):
        return {"records": [
            {"id": r["id"], "act": r["act"], "layer": r["layer"],
             "content": r["content"], "valid_time": r["valid_time"],
             "record_time": r["record_time"], "record_tick": r["record_tick"],
             "weight": self.weight(r)}
            for r in recs], "tick": self.tick}

    def act_read_last(self, count, lead):
        recs = self.records[-count:]
        return ({"act": "read", "mode": "last", "count": count}, recs, lead)

    def act_read_ids(self, rids, lead):
        recs = [self.records[i - 1] for i in rids]
        return ({"act": "read", "mode": "ids", "ids": rids}, recs, lead)

    # ---------------- act-call view (what the model emits) ----------------
    @staticmethod
    def call_view(rec):
        return {"act": rec["act"], "content": rec["content"],
                "source": rec["source"], "layer": rec["layer"],
                "valid_time": rec["valid_time"],
                "record_tick": rec["record_tick"], "refs": rec["refs"]}

    def write_ack(self, rids):
        return {"ok": True,
                "written": [{"id": i, "act": self.records[i - 1]["act"]}
                            for i in rids],
                "tick": self.tick}

    # ---------------- per-kind act planning ----------------
    def build(self):
        world = {m["message_no"]: m["world_time"]
                 for m in self.bio["messages"] if m["role"] == "user"}
        assistant_text = {m["message_no"]: m["content"]
                          for m in self.bio["messages"] if m["role"] == "assistant"}
        lead_idx = 0

        for ann in self.bio["annotations"]:
            s = ann["message_no"]
            kind = ann["kind"]
            world_time = world[s]
            phases = []

            def add_phase(acts_view=None, text=None, env=None):
                phases.append({"role": "assistant", "text": text,
                               "acts": acts_view or []})
                if env is not None:
                    phases.append({"role": "environment", "payload": env})

            if kind in ("fact", "identity"):
                rids = []
                for fr in ann["facts"]:
                    e = self.ledger[fr["fact_id"]]
                    rid = self.act_name(
                        subject=e["subject"], value=e["value"],
                        layer=e["kind"] if e["kind"] in LAYERS else fr["horizon"],
                        ledger_e=e, message_no=s, world_time=world_time,
                        valid_time=e["valid_time"])
                    rids.append(rid)
                add_phase(acts_view=[self.call_view(self.records[i - 1]) for i in rids],
                          text=assistant_text[s],
                          env=self.write_ack(rids))

            elif kind == "chatter":
                add_phase(text=assistant_text[s])

            elif kind == "repeat":
                fid = ann["extra"]["repeat_of"]
                e = self.ledger[fid]
                rid = self.act_repeat(fid, e["subject"], e["value"], s, world_time,
                                      fact_ids=[fid])
                add_phase(acts_view=[self.call_view(self.records[rid - 1])],
                          text=assistant_text[s], env=self.write_ack([rid]))

            elif kind == "position_change":
                ex = ann["extra"]
                old_rec = self.lid2rec[ex["old_lid"]]
                new_rec = self.act_name(
                    subject=ex["position_subject"], value=ex["new"],
                    layer="project", ledger_e=self.ledger[ex["new_lid"]],
                    message_no=s, world_time=world_time)
                conn = self.act_connect(
                    content=(f"Позиция по «{ex['position_subject']}» изменена: "
                             f"{ex['old']} → {ex['new']}. Прежняя больше не действует."),
                    layer="project", refs=[old_rec, new_rec],
                    message_no=s, world_time=world_time,
                    fact_ids=[ex["old_lid"], ex["new_lid"]])
                acts = [self.call_view(self.records[new_rec - 1]),
                        self.call_view(self.records[conn - 1])]
                add_phase(acts_view=acts, text=assistant_text[s],
                          env=self.write_ack([new_rec, conn]))

            elif kind == "contradiction":
                cd = ann["extra"]["contradiction"]
                fid = ann["extra"]["first_fid"]
                e1 = self.ledger[fid]
                a_rec = self.lid2rec[fid]
                b_rec = self.act_name(
                    subject=cd["subject"], value=cd["v2"], layer="project",
                    ledger_e=self.ledger["C2:" + fid],
                    message_no=s, world_time=world_time)
                conn = self.act_connect(
                    content=(f"Противоречие по «{cd['subject']}»: {cd['v1']} "
                             f"(сообщение {e1['message_no']}, "
                             f"{e1['world_time'][:16].replace('T', ' ')}) и {cd['v2']} "
                             f"(сообщение {s}, {world_time[:16].replace('T', ' ')}). "
                             f"Несовместимы; следую позднейшему — {cd['v2']}."),
                    layer="project", refs=[a_rec, b_rec],
                    message_no=s, world_time=world_time,
                    fact_ids=[fid, "C2:" + fid])
                acts = [self.call_view(self.records[b_rec - 1]),
                        self.call_view(self.records[conn - 1])]
                add_phase(acts_view=acts, text=assistant_text[s],
                          env=self.write_ack([b_rec, conn]))

            elif kind in ("crossref_use", "probe_crossref"):
                ex = ann["extra"]
                cr = ex["crossref"]
                e = self.ledger[ex["crossref_fid"]]
                early_rec = self.lid2rec[ex["crossref_fid"]]
                dec_rec = self.act_name(
                    subject=f"решение по «{cr['decision']}»",
                    value=f"{ex['subject']} — {ex['value']}",
                    layer="project", ledger_e=e, message_no=s,
                    world_time=world_time,
                    extra_content=(f"решение по «{cr['decision']}»: опираемся на "
                                   f"{ex['subject']} — {ex['value']}"))
                conn = self.act_connect(
                    content=(f"«{cr['decision']}»: учитывается {ex['subject']} — "
                             f"{ex['value']} (зафиксировано в сообщении "
                             f"{e['message_no']}, {e['world_time'][:16].replace('T', ' ')})."),
                    layer="project", refs=[early_rec, dec_rec],
                    message_no=s, world_time=world_time,
                    fact_ids=[ex["crossref_fid"]])
                acts = [self.call_view(self.records[dec_rec - 1]),
                        self.call_view(self.records[conn - 1])]
                add_phase(acts_view=acts, text=assistant_text[s],
                          env=self.write_ack([dec_rec, conn]))

            elif kind in ("unanswerable", "probe_abstain"):
                call, recs, lead = self.act_read_last(
                    5, T_READ_LEAD[lead_idx % len(T_READ_LEAD)])
                lead_idx += 1
                add_phase(acts_view=[call], text=lead,
                          env=self.read_payload(recs))
                add_phase(text=assistant_text[s])

            elif kind == "probe_recall":
                fid = ann["extra"]["target_fid"]
                call, recs, lead = self.act_read_ids(
                    [self.lid2rec[fid]],
                    T_READ_LEAD[lead_idx % len(T_READ_LEAD)])
                lead_idx += 1
                add_phase(acts_view=[call], text=lead,
                          env=self.read_payload(recs))
                add_phase(text=assistant_text[s], acts_view=[])
                ann["_reconcile_slot"] = s in (150, 200)

            elif kind == "probe_position":
                ex = ann["extra"]
                rids = [self.lid2rec[c["lid"]] for c in ex["chain"]]
                call, recs, lead = self.act_read_ids(
                    rids, T_READ_LEAD[lead_idx % len(T_READ_LEAD)])
                lead_idx += 1
                add_phase(acts_view=[call], text=lead,
                          env=self.read_payload(recs))
                add_phase(text=assistant_text[s])

            elif kind == "probe_contradiction":
                cd = ann["extra"]["contradiction"]
                fid = ann["extra"]["first_fid"]
                rids = [self.lid2rec[fid], self.lid2rec["C2:" + fid]]
                call, recs, lead = self.act_read_ids(
                    rids, T_READ_LEAD[lead_idx % len(T_READ_LEAD)])
                lead_idx += 1
                add_phase(acts_view=[call], text=lead,
                          env=self.read_payload(recs))
                add_phase(text=assistant_text[s])

            else:
                raise ValueError(kind)

            self.timeline.append({"message_no": s, "kind": kind,
                                  "phases": phases})

        # minimal reconcile demonstrations: after a recall probe at the last
        # two checkpoints, reconcile the most-repeated old record
        # (clock-biography check: stamps vs felt age; content derived from
        # the record store only)
        for c in (200, 150):
            targets = [tl for tl in self.timeline
                       if tl["kind"] == "probe_recall"
                       and tl["message_no"] <= c
                       and len(tl["phases"]) == 3]
            if not targets:
                continue
            tl = targets[-1]
            recs = tl["phases"][1]["payload"]["records"]
            if not recs:
                continue
            rec = max(recs, key=lambda r: (r["record_tick"] < self.tick - 80,
                                           len([x for x in self.records
                                                if x["act"] == "repeat"
                                                and r["id"] in x["refs"]])))
            dn = self.tick - rec["record_tick"]
            reps = sum(1 for x in self.records
                       if x["act"] == "repeat" and rec["id"] in x["refs"])
            content = (f"Сверка биографии: запись №{rec['id']} («{rec['content']}») "
                       f"записана на тике {rec['record_tick']}, прожито {dn} тиков, "
                       f"повторов {reps}; stamps записи подтверждены чтением.")
            rid = self.act_reconcile(
                content, refs=[rec["id"]], world_time=world[tl["message_no"]],
                record_ids=[rec["id"]],
                extra_nums=nums(rec["content"]) | {rec["id"], rec["record_tick"],
                                                   dn, reps})
            tl["phases"][2]["acts"] = [self.call_view(self.records[rid - 1])]

        return self

    # ---------------- validation ----------------
    def validate(self):
        errors = []
        ids = {r["id"] for r in self.records}
        prev_tick = 0
        for rec in self.records:
            if rec["act"] in ("name", "repeat", "connect", "reconcile"):
                if rec["layer"] not in LAYERS:
                    errors.append(f"rec {rec['id']}: bad layer {rec['layer']!r}")
                if rec["record_tick"] != prev_tick + 1:
                    errors.append(f"rec {rec['id']}: tick {rec['record_tick']} "
                                  f"after {prev_tick}")
                prev_tick = rec["record_tick"]
            else:
                if rec["record_tick"] != prev_tick:
                    errors.append(f"rec {rec['id']}: read advanced tick")
            if rec["valid_time"][:19] > rec["record_time"][:19]:
                errors.append(f"rec {rec['id']}: valid_time > record_time")
            for rid in rec["refs"]:
                if rid not in ids:
                    errors.append(f"rec {rec['id']}: dangling ref {rid}")
            if rec["act"] in ("repeat", "connect") and not rec["refs"]:
                errors.append(f"rec {rec['id']}: {rec['act']} without refs")
            # content traceability: every digit run must come from the ledger
            # or the referenced records
            allowed = set(rec["_allowed_nums"])
            for fid in rec["_fact_ids"]:
                e = self.ledger.get(fid)
                if e:
                    allowed |= nums(e["subject"]) | nums(e["value"]) | \
                        nums(e["message_no"]) | nums(e["world_time"])
            for rid in rec["_record_ids"]:
                other = self.records[rid - 1]
                allowed |= nums(other["content"]) | nums(other["record_tick"]) | \
                    nums(other["record_time"]) | nums(other["valid_time"])
            found = nums(rec["content"])
            foreign = found - allowed
            if foreign:
                errors.append(f"rec {rec['id']}: content digits not in ledger: "
                              f"{sorted(foreign)} :: {rec['content'][:80]}")
        return errors


def main():
    ap = argparse.ArgumentParser(description="Act-stream generator")
    ap.add_argument("--bios-dir", default=str(Path(__file__).resolve().parent / "biographies"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "acts"))
    args = ap.parse_args()

    bios_dir = Path(args.bios_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    all_ok = True
    totals = {"name": 0, "repeat": 0, "connect": 0, "reconcile": 0, "read": 0}
    layer_totals = {l: 0 for l in LAYERS}
    for p in sorted(bios_dir.glob("bio-*.json")):
        bio = json.loads(p.read_text(encoding="utf-8"))
        ba = BioActs(bio).build()
        errors = ba.validate()
        for rec in ba.records:
            if rec["act"] in ("name", "repeat", "connect", "reconcile"):
                totals[rec["act"]] += 1
                layer_totals[rec["layer"]] += 1
            else:
                totals["read"] += 1
        result = {"bio_id": bio["meta"]["bio_id"],
                  "records": ba.records,
                  "timeline": ba.timeline,
                  "final_tick": ba.tick}
        op = out / p.name
        op.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                      encoding="utf-8")
        status = "OK" if not errors else f"{len(errors)} ERRORS"
        all_ok &= not errors
        print(f"{op.name}: records={len(ba.records)} acts(tick)={ba.tick} "
              f"timeline={len(ba.timeline)} [{status}]")
        for e in errors[:10]:
            print("   ", e)

    print("\nAct totals:", totals)
    print("Layer totals:", layer_totals)
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
