"""PlastFormer run — unified body: core K + Instruction (LoRA, assembly alpha) + Phi bank.

The read path: resident prefix vectors enter the stream before attention via the
model's native input_embeddings path (Gemma4TextModel.forward). Ticks: one turn
= 1 tick; one executed storing act = +1 tick (CONSTITUTION C5 accounting).
Inference always uses the default chat template (the pass saw it; enable_thinking
form). Phi persists to section-phi/ after each turn (E4 export).

Usage: python3 run_vector.py [bank_dir]      ('exit' quits, 'phi' shows the bank)
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mlx.core as mx
from mlx_lm import load
from mlx_lm.sample_utils import make_sampler
from bank import PhiBank
from write_iface import WriteIface
from read_iface import ReadIface

MODEL = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
INSTRUCTION = "/Users/alex/plastformer/experiments/o8-pass/adapters_alpha"
DIALS = {"prefix_depth": 12, "surfacing_cap": 12}   # Fork 7 defaults
MAX_NEW_TOKENS = 700

ACT_RE = re.compile(r'\{[^{}]*"act"\s*:\s*"([a-z]+)"[^{}]*\}', re.S)

def parse_acts(text):
    acts, seen = [], set()
    for m in ACT_RE.finditer(text):
        try: obj = json.loads(m.group(0))
        except json.JSONDecodeError: continue
        kind = obj.get("act")
        if kind in ("name","repeat","connect","reconcile","read"):
            key = (kind, str(obj.get("content",""))[:120])
            if key in seen: continue
            seen.add(key); acts.append(obj)
    return acts

def main():
    bank_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "section-phi")
    model, tok = load(MODEL, adapter_path=INSTRUCTION)
    d = model.args.hidden_size

    bank = PhiBank(d=d, path=bank_dir)
    if os.path.isdir(bank_dir) and os.path.exists(os.path.join(bank_dir, "vectors.npy")):
        n = bank.import_(bank_dir); print(f"[phi] bank restored: {n} traces, tick {bank.tick}")
    write = WriteIface(model.model.embed_tokens, tok)
    read = ReadIface(model.model.embed_scale, DIALS)

    history = []
    print("PlastFormer (vector Phi) ready. 'exit' quits, 'phi' shows the bank.", flush=True)
    while True:
        try: user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if user.lower() in ("exit","quit"): break
        if user == "phi":
            for tid, tot in bank.loudest(50):
                m = bank.meta[tid-1]
                print(f'  [{tid}] tick{m["tick"]} rep{m["repeats"]} amp={tot:.3f} :: {m["content"][:100]}')
            continue
        if not user: continue

        # ---- read: resident prefix + prompt, one stream ----
        pref = read.prefix_embeddings(bank)                 # [n, d] or None
        messages = history[-10:] + [{"role": "user", "content": user}]
        prompt = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        ids = tok.encode(prompt)
        tok_embs = model.model.embed_tokens(mx.array(ids))[None]  # [1, L, d]
        parts = [e for e in (pref, tok_embs) if e is not None]
        embs = mx.concatenate(parts, axis=1)
        n_pref = 0 if pref is None else pref.shape[0]

        # ---- prefill + generate (custom loop: embeddings entering the stream) ----
        cache = None
        from mlx_lm.models.cache import make_prompt_cache
        cache = make_prompt_cache(model)
        logits = model(inputs=None, cache=cache, input_embeddings=embs)
        sampler = make_sampler(temp=0.6)
        out_ids = []
        stop_ids = {tok.eos_token_id, 106}   # <eos> + <end_of_turn> (generation_config)
        for _ in range(MAX_NEW_TOKENS):
            prev = logits[:, -1] if logits.ndim == 3 else logits[None][:, -1]
            if prev.ndim == 3: prev = prev[:, -1]
            nxt = sampler(prev)
            tid = int(nxt.item())
            if tid in stop_ids: break
            out_ids.append(tid)
            logits = model(inputs=nxt[None], cache=cache)
        text = tok.decode(out_ids)
        print(f"\nPlastFormer: {text}")

        # ---- write: acts from the model's own output stream ----
        acts = parse_acts(text)
        n_acts = 0
        for act in acts:
            kind = act.get("act")
            if kind in ("name", "connect"):
                content = str(act.get("content", ""))[:400]
                if not content: continue
                vec = write.content_vector(content)
                tid = bank.append(vec,
                                  source=str(act.get("source","user")),
                                  loudness=str(act.get("loudness","record")),
                                  layer=str(act.get("layer","t3")),
                                  meta={"content": content, "act": kind,
                                        "valid_time": str(act.get("valid_time","")),
                                        "refs": act.get("refs", act.get("sources", []))})
                n_acts += 1; print(f"  [phi] {kind} -> trace {tid}")
            elif kind == "repeat":
                rid = int(act.get("id", 0) or 0)
                if 1 <= rid <= len(bank.meta):
                    bank.touch(rid); n_acts += 1; print(f"  [phi] repeat -> trace {rid}")
            elif kind == "reconcile":
                content = f"reconcile: {act.get('topic','')} -> {act.get('outcome','')}"
                vec = write.content_vector(content)
                bank.append(vec, "own_derivation", "note", "t4",
                            {"content": content, "act": "reconcile"})
                n_acts += 1; print("  [phi] reconcile logged")
            elif kind == "read":
                picks = bank.loudest(int(act.get("count", DIALS["surfacing_cap"])))
                print("  [phi] read -> " + "; ".join(f"[{i}] {bank.meta[i-1]['content'][:60]}" for i,_ in picks))
        bank.tick += 1 + (1 if n_acts else 0)   # C5 accounting: turn + storing acts
        history = history + [{"role":"user","content":user},{"role":"assistant","content":text}]
        bank.export(bank_dir)

if __name__ == "__main__":
    main()
