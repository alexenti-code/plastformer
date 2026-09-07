#!/usr/bin/env python3
"""O-8 component B: self-distillation anchor generator.

Generates the base model's frozen outputs on general prompts (no memory,
no grammar mentions). Checkpoints after each prompt so restarts resume.
Output: experiments/o8-pass/anchor.jsonl (mlx_lm chat format).
"""
import json, time, sys
from pathlib import Path
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
PROMPTS = json.load(open("/tmp/o8_prompts.json"))
OUT = Path("/Users/alex/plastformer/experiments/o8-pass/anchor.jsonl")
STATE = Path("/tmp/o8_anchor_state.json")

done = set()
if OUT.exists():
    for line in OUT.read_text().splitlines():
        if line.strip():
            done.add(json.loads(line)["prompt_idx"])
else:
    OUT.write_text("")

model, tokenizer = load(MODEL)
print("model loaded", flush=True)

t_start = time.time()
for idx, prompt in enumerate(PROMPTS):
    if idx in done:
        continue
    t0 = time.time()
    messages = [{"role": "user", "content": prompt}]
    prompt_text = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    out = generate(model, tokenizer, prompt=prompt_text, max_tokens=500, sampler=make_sampler(temp=0.7))
    rec = {"prompt_idx": idx, "prompt": prompt, "response": out}
    with OUT.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[{idx+1}/{len(PROMPTS)}] {time.time()-t0:.1f}s total {time.time()-t_start:.0f}s", flush=True)

print("DONE", flush=True)
