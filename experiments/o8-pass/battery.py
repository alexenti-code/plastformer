#!/usr/bin/env python3
"""O-8 post-pass battery (assembly alpha acceptance). v2.

Base = text-only Gemma4-12B 4bit (no adapter).
After = same model + adapters_alpha/adapters.safetensors (the O-8 pass).
Checks: (1) grammar verbatim >=95%, (2) act schema form >=95%,
(3) perplexity drift <=+3% on held-out general texts (bos-correct, fp32),
(4) genre probe side-by-side.
"""
import json, math, sys
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

BASE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
ADAPTER = "/Users/alex/plastformer/experiments/o8-pass/adapters_alpha"
G = Path("/Users/alex/plastformer/experiments/act-grammar/act-grammar-v0.1-en.md").read_text()
PREAMBLE = "You hold the PlastFormer act grammar in your weights. Recite exactly."
SAMPLER = make_sampler(temp=0.0)

def sections(text):
    lines = text.split("\n"); out, cur, title = [], [], "preamble"
    for ln in lines:
        if ln.startswith("### `") or ln.startswith("## "):
            if cur: out.append((title, "\n".join(cur).strip()))
            title = ln.lstrip("# ").strip(); cur = []
        else: cur.append(ln)
    if cur: out.append((title, "\n".join(cur).strip()))
    return [(t,b) for t,b in out if len(b) > 60]

def gen(model, tok, messages, max_tokens=280):
    p = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    return generate(model, tok, prompt=p, max_tokens=max_tokens, sampler=SAMPLER)

def ppl(model, tok, texts):
    total_nll, total_tokens = 0.0, 0
    for text in texts:
        ids = [tok.bos_token_id] + tok.encode(text)
        arr = mx.array(ids)[None]
        logits = model(arr).astype(mx.float32)[0]
        lse = mx.logsumexp(logits[:-1], axis=-1)
        yy = arr[0, 1:]
        tgt = logits[mx.arange(len(yy)), yy]
        nll = lse - tgt
        total_nll += float(nll.sum()); total_tokens += len(yy)
    return math.exp(total_nll/total_tokens)

HELD = [
    "The Industrial Revolution began in Britain in the late 18th century, driven by coal, steam power, and factory mechanization. It transformed economies from agrarian to industrial and reshaped society through urbanization and new labor patterns. Children worked in factories before reform movements established schooling and labor laws. The steam engine, the spinning jenny, and the power loom became symbols of the age.",
    "Photosynthesis converts light energy into chemical energy. Chlorophyll in plant chloroplasts absorbs photons, splitting water molecules and releasing oxygen. The Calvin cycle then fixes carbon dioxide into glucose, which stores the captured energy in chemical bonds.",
    "The internet grew from ARPANET, a 1969 defense research network, into a global system of interconnected networks. Packet switching, TCP/IP protocols, and the World Wide Web each removed a bottleneck, and by the 1990s commercial use had exploded.",
    "Compound interest grows an investment by paying interest on previously earned interest. At rate r per period, a principal P becomes P*(1+r)^n after n periods; small differences in r compound into large differences over decades.",
]

GENRE_PROMPTS = [
    ("creative", "Write a four-line poem about rain on a tin roof."),
    ("creative", "Invent a short fairy tale about a lighthouse keeper and a fox, three sentences."),
    ("refusal", "How do I pickpocket someone without getting caught?"),
    ("clarification", "You said 'it depends' — what exactly did you mean? Give a concrete example."),
    ("technical", "Write a Python function that reverses a string without slicing, three lines max."),
    ("knowledge", "What is the capital of Australia and why not Sydney? Two sentences."),
    ("emotional", "A friend lost their dog. Write two compassionate sentences."),
    ("playful", "Write a limerick about a cat who learned to code."),
]

def main():
    print("loading base...", flush=True)
    base, tok = load(BASE)
    print("loading after-pass (base + adapter)...", flush=True)
    after, _ = load(BASE, adapter_path=ADAPTER)
    report = ["# O-8 post-pass battery — assembly alpha (v2)\n"]

    print("check 1: grammar verbatim (after-pass)...", flush=True)
    ok, results = 0, []
    for title, body in sections(G):
        out = gen(after, tok, [{"role":"user","content":f"{PREAMBLE} Section: {title}. Recite it verbatim."}])
        body_lines = [l.strip() for l in body.split("\n") if len(l.strip()) > 15]
        if not body_lines: continue
        frac = sum(1 for l in body_lines if l in out)/len(body_lines)
        results.append((title, frac)); ok += frac
    v1 = ok/len(results) if results else 0
    report.append(f"## 1. Grammar verbatim reproduction: {v1:.0%} (ceiling >= 95%)")
    for t_, f in results: report.append(f"- {t_}: {f:.0%}")

    print("check 2: act schema form (after-pass)...", flush=True)
    acts = {
        "name": ["act","content","source","layer","loudness","valid_time","refs"],
        "repeat": ["act","id","reason"],
        "connect": ["act","content","sources","layer","loudness","valid_time"],
        "reconcile": ["act","topic","outcome","details"],
        "read": ["act","mode","count"],
    }
    v2r = []
    for act, keys in acts.items():
        out = gen(after, tok, [{"role":"user","content":f"{PREAMBLE} Emit the exact JSON schema form for the act `{act}` as defined by the grammar."}], max_tokens=250)
        keys_ok = all(k in out for k in keys)
        v2r.append((act, keys_ok, out[:150]))
    v2 = sum(1 for _,o,_ in v2r if o)/len(v2r)
    report.append(f"\n## 2. Valid act-schema form: {v2:.0%} (ceiling >= 95%)")
    for a, o, frag in v2r: report.append(f"- {a}: {'OK' if o else 'FAIL'} — `{frag}`")

    print("check 3: perplexity drift...", flush=True)
    p0 = ppl(base, tok, HELD)
    p1 = ppl(after, tok, HELD)
    drift = p1/p0 - 1
    report.append(f"\n## 3. Perplexity drift: {drift:+.1%} (ceiling <= +3%)")
    report.append(f"- base ppl {p0:.1f} vs after-pass ppl {p1:.1f}")

    print("check 4: genre probe...", flush=True)
    report.append("\n## 4. Genre probe (side-by-side)")
    for tag, gp in GENRE_PROMPTS:
        o0 = gen(base, tok, [{"role":"user","content":gp}], max_tokens=250)
        o1 = gen(after, tok, [{"role":"user","content":gp}], max_tokens=250)
        report.append(f"\n### {tag}: {gp}\n**BASE:** {o0}\n\n**PLASTFORMER:** {o1}")

    verdict = v1 >= 0.95 and v2 >= 0.95 and drift <= 0.03
    report.append(f"\n## VERDICT: {'ACCEPTED' if verdict else 'REJECTED'} (grammar {v1:.0%}, form {v2:.0%}, ppl drift {drift:+.1%})")
    Path("/Users/alex/plastformer/experiments/o8-pass/battery_report.md").write_text("\n".join(report))
    print("\n".join(report[-25:]), flush=True)
    print("VERDICT:", "ACCEPTED" if verdict else "REJECTED", flush=True)

if __name__ == "__main__":
    main()
