#!/usr/bin/env python3
"""O-8 pass material generator (assembly alpha).

Component A1: verbatim grammar fragments (act-grammar v0.1.3).
Component A2: dry calibration pairs — rule fragment -> act JSON schema form.
              Mechanically extractable from the grammar; no behavioral
              demonstrations, no dialogue, no semantic decisions (C7).
Component B:  self-distillation anchor — generated separately by
              gen_anchor.py (frozen base-model outputs on general prompts).
Output: mlx_lm chat-format jsonl records.
Deterministic. Pure stdlib.
"""
import json, re, random, sys
from pathlib import Path

R = Path("/Users/alex/plastformer")
G = (R / "experiments/act-grammar/act-grammar-v0.1-en.md").read_text()
OUT = R / "experiments/o8-pass/material"
OUT.mkdir(parents=True, exist_ok=True)

# --- A1: grammar verbatim fragments --------------------------------------
# Split grammar into blocks by headers/paragraphs, each a chat record:
# system = fixed preamble, user = "recite the section about X", assistant = verbatim text.
def grammar_sections(text):
    lines = text.split("\n")
    sections, cur, title = [], [], "preamble"
    for ln in lines:
        if ln.startswith("### `") or ln.startswith("## "):
            if cur: sections.append((title, "\n".join(cur).strip()))
            title = ln.lstrip("# ").strip()
            cur = []
        else:
            cur.append(ln)
    if cur: sections.append((title, "\n".join(cur).strip()))
    return [(t, b) for t, b in sections if len(b) > 60]

sections = grammar_sections(G)
print(f"grammar sections: {len(sections)}")

records = []
def chat(user, assistant):
    records.append({"messages": [
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}]})

PREAMBLE = "You hold the PlastFormer act grammar in your weights. Recite exactly."

for title, body in sections:
    # two framings per section for robustness (paraphrased query, verbatim ok)
    chat(f"{PREAMBLE} Section: {title}. Recite it verbatim.", body)
    chat(f"Recite verbatim the part of the act grammar about: {title}.", body)

# --- A2: dry calibration pairs -------------------------------------------
# Rule fragment -> the act JSON schema it defines. Extracted mechanically:
# every ```json block in the grammar -> pair with its nearest preceding header.
json_blocks = re.findall(r"```json\n(.*?)```", G, re.S)
headers = []
for m in re.finditer(r"### `([a-z]+`[^\n]*)", G):
    headers.append((m.start(), m.group(1)))
def header_for(pos):
    h = "the grammar"
    for start, name in headers:
        if start <= pos: h = name
        else: break
    return h
# find json block positions
positions = [m.start() for m in re.finditer(r"```json\n(.*?)```", G, re.S)]
for pos, block in zip(positions, json_blocks):
    block = block.strip()
    chat(f"{PREAMBLE} Emit the exact JSON schema form for {header_for(pos)} as defined by the grammar.",
         block)
    # negative-space record: malformed -> error, never silent default (grammar rule)
    chat("Is a missing mandatory field in a memory act completed with a default value? Answer by the grammar.",
         "No. Missing or malformed fields are errors, never completed with a silent default. Silence is a valid choice; forced acts are noise.")

# act names and their one-line meaning (from the grammar itself)
act_lines = [ln.strip() for ln in G.split("\n") if re.match(r"^### `(name|repeat|connect|reconcile|read)`", ln)]
for ln in act_lines:
    act = re.match(r"### `([a-z]+)`", ln).group(1)
    chat(f"{PREAMBLE} Which acts exist and what does `{act}` do (one line, by the grammar)?",
         f"Acts: name, repeat, connect, reconcile, read. {ln}")

# --- write out ------------------------------------------------------------
rng = random.Random(7)
rng.shuffle(records)
# split 90/10
n_valid = max(2, len(records)//10)
train = records[:-n_valid]
valid = records[-n_valid:]
(OUT / "train.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in train) + "\n")
(OUT / "valid.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in valid) + "\n")
(OUT / "test.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in valid) + "\n")
print(f"records: {len(records)} (train {len(train)}, valid {len(valid)})")
print(f"out: {OUT}")
