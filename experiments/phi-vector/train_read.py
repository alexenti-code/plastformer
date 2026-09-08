"""Read-side training: projector G maps a trace vector (mean-pool embedding of the
content) to k=8 prefix slots; the frozen core+Instruction decodes the content from them.

Loss: token CE on content tokens conditioned on [G(v); chat-prefix embeddings].
Frozen: core K, Instruction. Trained: G only (d->256->8d). Data: read-corpus/train.jsonl.
"""
import json, math, os, sys, time
import numpy as np
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load

MODEL = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
INSTRUCTION = "/Users/alex/plastformer/experiments/o8-pass/adapters_alpha"
CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "read-corpus")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "read_proj.npz")

K_SLOTS = 8
BOTTLENECK = 256
BATCH = 4
LR = 1e-4
ITERS = int(os.environ.get("ITERS", "300"))

class ReadProj(nn.Module):
    def __init__(self, d, k, hid):
        super().__init__()
        self.fc1 = nn.Linear(d, hid)
        self.fc2 = nn.Linear(hid, k * d)
        self.k, self.d = k, d
    def __call__(self, v):                       # v: [B, d]
        h = mx.tanh(self.fc1(v))                  # [B, hid]
        out = self.fc2(h)                         # [B, k*d]
        return out.reshape(v.shape[0], self.k, self.d)  # [B, k, d]

def main():
    model, tok = load(MODEL, adapter_path=INSTRUCTION)
    model.eval()
    model.freeze()                                 # freeze core + Instruction
    d = model.args.hidden_size

    train = [json.loads(l)["content"] for l in open(os.path.join(CORPUS, "train.jsonl"))]
    valid = [json.loads(l)["content"] for l in open(os.path.join(CORPUS, "valid.jsonl"))]
    print(f"train={len(train)} valid={len(valid)}")

    G = ReadProj(d, K_SLOTS, BOTTLENECK)
    if os.path.exists(OUT):
        z = np.load(OUT)
        G.fc1.weight = mx.array(z["fc1.weight"].astype(np.float32))
        G.fc1.bias = mx.array(z["fc1.bias"].astype(np.float32))
        G.fc2.weight = mx.array(z["fc2.weight"].astype(np.float32))
        G.fc2.bias = mx.array(z["fc2.bias"].astype(np.float32))
        mx.eval(G.parameters())
        print(f"resumed from {OUT}")

    embed = model.model.embed_tokens
    scale = float(model.model.embed_scale)
    stop_ids = {tok.eos_token_id, 106}

    def content_ids(text):
        # supervised block: the content tokens themselves
        return tok.encode(text) + [106]           # end-of-turn as terminator

    def step_fn(content_batch):
        vs, tss = [], []
        for c in content_batch:
            ids = tok.encode(c)[:48]
            v = mx.mean(embed(mx.array(ids)).astype(mx.float32), axis=0)  # [d]
            vs.append(v)
            tss.append(mx.array(content_ids(c)[:48] + [106]))
        V = mx.stack(vs)                          # [B, d]
        slots = G(V)                              # [B, k, d]
        B = len(tss)
        L = max(t.shape[0] for t in tss)
        tgt_emb = mx.stack([
            mx.concatenate([embed(ts), mx.zeros((L - ts.shape[0], d))], axis=0)
            for ts in tss
        ])                                        # [B, L, d]
        mask = mx.stack([
            mx.concatenate([mx.ones(ts.shape[0]), mx.zeros(L - ts.shape[0])])
            for ts in tss
        ])                                        # [B, L]
        embs = mx.concatenate([slots, tgt_emb], axis=1)  # [B, k+L, d]
        logits = model(inputs=None, cache=None, input_embeddings=embs)
        lg = logits[:, K_SLOTS - 1 : K_SLOTS - 1 + L, :]  # [B, L, V]
        tgt_pad = mx.stack([
            mx.concatenate([ts, mx.zeros((L - ts.shape[0],), mx.int32)])
            for ts in tss
        ])
        ce = nn.losses.cross_entropy(lg, tgt_pad)  # [B, L]
        return mx.sum(ce * mask) / mx.sum(mask)

    def _save(G, path):
        flat = {}
        def _flatten(prefix, d):
            for k, v in d.items():
                if isinstance(v, dict): _flatten(prefix + k + ".", v)
                else: flat[prefix + k] = v
        _flatten("", G.parameters())
        params = {k: np.array(v, dtype=np.float16) for k, v in flat.items()}
        np.savez(path, **params)
        print(f"[checkpoint] {path}", flush=True)

    loss_and_grad = nn.value_and_grad(G, step_fn)
    opt = optim = __import__("mlx.optimizers", fromlist=["AdamW"]).AdamW(LR)
    # shorter: direct import
    import mlx.optimizers as _o
    opt = _o.AdamW(LR)

    rng = np.random.default_rng(43)
    t0 = time.time()
    for it in range(1, ITERS + 1):
        idx = rng.integers(0, len(train), size=BATCH)
        batch = [train[i] for i in idx]
        l, grads = loss_and_grad(batch)
        opt.update(G, grads)
        mx.eval(l, G.parameters())
        if it % 5 == 0 or it == 1:
            el = time.time() - t0
            print(f"it {it:4d} loss {float(l):.3f} | {el:.0f}s ({el/it:.2f}s/it)", flush=True)
        if it % 50 == 0:
            _save(G, OUT)

    # valid loss
    vl = []
    rng2 = np.random.default_rng(44)
    for i in range(0, min(len(valid), 48), BATCH):
        batch = valid[i:i+BATCH]
        if len(batch) < 2: continue
        vl.append(float(step_fn(batch)))
    print(f"valid CE: {np.mean(vl):.3f}")

    _save(G, OUT)
    print(f"saved {OUT}")

if __name__ == "__main__":
    main()
