#!/usr/bin/env python3
"""PlastFormer run script — Gemma4-12B + act grammar (O-8 assembly alpha) + Phi substrate.

Configuration: parametric-dials x co-located x instructed (target form; trace bank of text records pending the vector substrate).
Phi = trace bank: content + provenance + amplitude[t1..t5] + stamps. Show dials per DESIGN
§11: surfacing_cap=12, prefix_depth=12, residency_horizon=16, rebuild_period=1, gap/surprise
thresholds off by default (surprise needs perplexity probe — off in this build).

Acts are parsed from the model's own output stream (C4: only explicit acts write).
Physics: decay a_i(n) = a_i(0) * exp(-dn/tau_i) per tick; act_price 1 tick per storing act;
audibility_floor 0.01; cap table user 1.0 / tool_result 0.8 / own_derivation 0.6;
loudness multipliers note 0.5 / record 1.0 / anchor 1.5 (inside cap).
Read = loudest-N by amplitude, content-blind (C2). No significance thresholds.

Usage: python3 plastformer_run.py  (interactive chat; 'exit' to quit)
State: Phi persisted to experiments/o8-pass/phi_state.json after each turn (E4 export).
"""
import json, math, re, sys, time
from pathlib import Path
sys.path.insert(0, "/Users/alex/.pyenv/versions/3.11.9/lib/python3.11/site-packages")
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
ADAPTER = "/Users/alex/plastformer/experiments/o8-pass/adapters_alpha"
STATE = Path("/Users/alex/plastformer/experiments/o8-pass/phi_state.json")

TAUS = [15, 80, 400, 2000, 10000]
FLOOR = 0.01
CAPS = {"user": 1.0, "tool_result": 0.8, "own_derivation": 0.6}
LOUD = {"note": 0.5, "record": 1.0, "anchor": 1.5}
ACT_PRICE = 1.0
SURFACING_CAP = 12
PREFIX_DEPTH = 12
RESIDENCY_HORIZON = 16
REBUILD_PERIOD = 1

GRAMMAR = Path("/Users/alex/plastformer/experiments/act-grammar/act-grammar-v0.1-en.md").read_text()

# ---------------- Phi ----------------
class Phi:
    def __init__(self):
        self.traces = []   # {id, content, source, layer, loudness, valid_time, refs, tick, amp:[5]}
        self.tick = 0
        self.next_id = 1
        self.prefix_events = []

    def decay_to(self, tick):
        dn = tick - (self.traces[0]["tick"] if self.traces else tick)
        for tr in self.traces:
            for i, tau in enumerate(TAUS):
                tr["amp"][i] *= math.exp(-(tick - tr["last_tick"]) / tau)
            tr["last_tick"] = tick

    def write(self, act, content, source, layer, loudness, valid_time, refs, tick):
        if layer not in ("t1","t2","t3","t4","t5"):
            print(f"  [phi] WARNING: unknown layer {layer!r} — defaulting to t3 (logged, not silent)")
            layer = "t3"
        idx = ["t1","t2","t3","t4","t5"].index(layer)
        cap = CAPS.get(source, 0.6)
        mult = LOUD.get(loudness, 1.0)
        amp = []
        for i in range(5):
            base = [1.0, 0.8, 0.5, 0.25, 0.1][i] * (1.6 if i == idx else 1.0)
            amp.append(min(base * mult, cap))
        tr = {"id": self.next_id, "content": content, "source": source, "layer": layer,
              "loudness": loudness, "valid_time": valid_time, "refs": refs,
              "tick": tick, "last_tick": tick, "amp": amp, "repeats": 0}
        self.next_id += 1
        self.traces.append(tr)
        return tr["id"]

    def repeat(self, rid, tick):
        for tr in self.traces:
            if tr["id"] == rid:
                for i in range(5):
                    tr["amp"][i] = min(tr["amp"][i] * 1.3, CAPS.get(tr["source"], 0.6) * 1.6)
                tr["repeats"] += 1
                tr["last_tick"] = tick
                return True
        return False

    def loudest(self, n=SURFACING_CAP):
        alive = [tr for tr in self.traces if max(tr["amp"]) >= FLOOR]
        return sorted(alive, key=lambda tr: -max(tr["amp"]))[:n]

    def render_prefix(self):
        top = self.loudest(PREFIX_DEPTH)
        if not top: return "Your memory (Phi) is empty."
        lines = ["Your memory (Phi), loudest traces by amplitude (id | layer | amp | content):"]
        for tr in top:
            lines.append(f'  [{tr["id"]}] {tr["layer"]} {max(tr["amp"]):.2f} :: {tr["content"][:160]}')
        return chr(10).join(lines)

# ---------------- Act parsing (model output stream) ----------------

def parse_acts(text):
    acts = []
    pattern = re.compile(r'\{[^{}]*"act"\s*:\s*"[a-z]+"[^{}]*\}', re.S)
    seen = set()
    for m in pattern.finditer(text):
        try:
            obj = json.loads(m.group(0))
            if obj.get("act") in ("name", "repeat", "connect", "reconcile", "read"):
                key = (obj.get("act"), str(obj.get("content",""))[:120])
                if key in seen: continue
                seen.add(key)
                acts.append(obj)
        except json.JSONDecodeError:
            continue
    return acts

def field(d, key, default=""):
    v = d.get(key, default)
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)

# ---------------- Main loop ----------------
def main():
    model, tok = load(MODEL, adapter_path=ADAPTER)
    phi = Phi()
    if STATE.exists():
        phi.__dict__.update(json.load(open(STATE)))
    history = []
    print("PlastFormer ready. Talk. 'exit' quits. 'phi' shows the memory bank.", flush=True)
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in ("exit", "quit"): break
        if user == "phi":
            for tr in phi.loudest(50):
                print(f'[{tr["id"]}] {tr["layer"]} l={tr["loudness"]} a={max(tr["amp"]):.2f} :: {tr["content"][:120]}')
            continue
        if not user: continue

        prefix = phi.render_prefix()
        system = ("You are a PlastFormer model: you keep your own memory by emitting memory acts "
                  "in your output. After your answer, if needed, emit acts as SEPARATE JSON objects, "
                  "each starting with {\"act\": ...}. Schemas:\n"
                  'name: {"act":"name","content":"...","source":"user|own_derivation|tool_result","layer":"t1|t2|t3|t4|t5","loudness":"note|record|anchor","valid_time":"...","refs":[]}\n'
                  'repeat: {"act":"repeat","id":<id>,"reason":"..."}\n'
                  'connect: {"act":"connect","content":"...","sources":[ids],"layer":"...","loudness":"...","valid_time":"..."}\n'
                  'reconcile: {"act":"reconcile","topic":"...","outcome":"confirmed|stale|divergent","details":"..."}\n'
                  'read: {"act":"read","mode":"last|ids","count":N}\n'
                  "The grammar is embedded in your weights; these are the exact forms.\n\n" + prefix)
        messages = [{"role": "system", "content": system}] + history[-10:] + [{"role": "user", "content": user}]
        prompt = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        out = generate(model, tok, prompt=prompt, max_tokens=700,
                       sampler=make_sampler(temp=0.6))
        print(f"\nPlastFormer: {out}")

        acts = parse_acts(out)
        phi.tick += 1
        n_acts = 0
        for act in acts:
            kind = act.get("act")
            if kind == "name":
                rid = phi.write("name", field(act,"content"), field(act,"source","user"),
                                field(act,"layer","t3"), field(act,"loudness","record"),
                                field(act,"valid_time"), act.get("refs",[]), phi.tick)
                n_acts += 1; print(f"  [phi] name -> trace {rid}")
            elif kind == "connect":
                rid = phi.write("connect", field(act,"content"), field(act,"source","own_derivation"),
                                field(act,"layer","t4"), field(act,"loudness","record"),
                                field(act,"valid_time"), act.get("sources",[]), phi.tick)
                n_acts += 1; print(f"  [phi] connect -> trace {rid}")
            elif kind == "repeat":
                if phi.repeat(int(act.get("id",0) or 0), phi.tick):
                    n_acts += 1; print(f"  [phi] repeat -> trace {act.get('id')}")
            elif kind == "reconcile":
                rid = phi.write("reconcile", f"reconcile: {field(act,'topic')} -> {field(act,'outcome')}",
                                "own_derivation", "t4", "note", "", [], phi.tick)
                n_acts += 1; print(f"  [phi] reconcile logged")
            elif kind == "read":
                mode = act.get("mode","last")
                if mode == "ids":
                    trs = [tr for tr in phi.traces if tr["id"] in (act.get("ids") or [])]
                else:
                    trs = phi.loudest(int(act.get("count", SURFACING_CAP)))
                print("  [phi] read -> " + "; ".join(f'[{tr["id"]}] {tr["content"][:80]}' for tr in trs))
        if n_acts: phi.tick += int(ACT_PRICE)  # act_price: +1 tick when acts executed
        history = history + [{"role":"user","content":user},{"role":"assistant","content":out}]
        json.dump({"traces": phi.traces, "tick": phi.tick, "next_id": phi.next_id},
                  open(STATE,"w"), ensure_ascii=False)

if __name__ == "__main__":
    main()
