#!/usr/bin/env python3
"""O-8 material mixer: grammar (A) + self-distillation anchor (B).
Target proportion: grammar ~13-20% of records (Limitation 10 mitigation).
Writes train/valid/test into material/.
"""
import json, random
from pathlib import Path

OUT = Path("/Users/alex/plastformer/experiments/o8-pass/material")
A = [json.loads(l) for l in open("/Users/alex/plastformer/experiments/o8-pass/grammar.jsonl") if l.strip()]
B_raw = [json.loads(l) for l in open("/Users/alex/plastformer/experiments/o8-pass/anchor.jsonl") if l.strip()]
# unify: anchor records -> chat format
B = [{"messages": [{"role": "user", "content": r["prompt"]},
                    {"role": "assistant", "content": r["response"]}]} for r in B_raw]
print(f"A grammar: {len(A)}, B anchor: {len(B)}")

rep = 1
while (len(A)*(rep+1)) / (len(B) + len(A)*(rep+1)) < 0.13:
    rep += 1
records = B + A*rep
share = len(A)*rep/len(records)
print(f"grammar repeat x{rep}: {len(A)*rep} A records, share {share:.0%}")

rng = random.Random(11)
rng.shuffle(records)
n_valid = max(3, len(records)//12)
train, valid = records[:-n_valid], records[-n_valid:]
(OUT/"train.jsonl").write_text(chr(10).join(json.dumps(r, ensure_ascii=False) for r in train)+chr(10))
(OUT/"valid.jsonl").write_text(chr(10).join(json.dumps(r, ensure_ascii=False) for r in valid)+chr(10))
(OUT/"test.jsonl").write_text(chr(10).join(json.dumps(r, ensure_ascii=False) for r in valid)+chr(10))
print(f"train {len(train)}, valid {len(valid)}")
