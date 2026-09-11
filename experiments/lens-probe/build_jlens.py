
"""Якобиев объектив — рабочий способ: градиент по каждому слою отдельным прогоном."""
import mlx.core as mx, numpy as np, time, json
from mlx_lm import load

CORE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
model, tok = load(CORE)
inner = model.model; L = inner.layers; NL = len(L)

CORPUS = [
 "Столица Франции — это город", "Число ног у паука равно",
 "Вода закипает при температуре", "Автор романа Война и мир",
 "Two plus two equals", "Сколько дней в неделе",
 "Москва — столица", "The capital of Japan is",
 "Корова даёт", "Самая длинная река в мире",
 "Зимой идёт", "Корень из четырёх равен",
]
CON = [" паук"," муравей"," восемь"," шесть"," Франция"," Париж"," Марс"," красный",
       "spider","eight","France","Paris"]
CON_ID = [tok.encode(c)[0] for c in CON]
print("понятий:", len(CON), flush=True)

seqs = [tok.encode(p) for p in CORPUS]
ml = max(len(s) for s in seqs)
padv = np.zeros((len(seqs), ml), dtype=np.int32); mk = np.zeros((len(seqs), ml), dtype=np.float32)
for i,s in enumerate(seqs):
    padv[i,:len(s)] = s; mk[i,:len(s)] = 1.0
X = mx.array(padv); W = mx.array(mk)

def full_forward(h):
    cache=[None]*NL; msk=inner._make_masks(h,cache); inter=[(None,None)]*NL
    hs=[h]
    for idx,(layer,mk_,c,prev) in enumerate(zip(L,msk,cache,inner.previous_kvs)):
        kvs,off=inter[prev]
        h,kvs,off=layer(h,mk_,c,per_layer_input=None,shared_kv=kvs,offset=off)
        inter[idx]=(kvs,off); hs.append(h)
    return hs

t0=time.time()
h0 = inner.embed_tokens(X) * inner.embed_scale
HS = full_forward(h0)
mx.eval(HS)
HS = [mx.stop_gradient(h) for h in HS]
print(f"эталон: {time.time()-t0:.1f} с", flush=True)

def rest(x, start, tid):
    h = x
    cache=[None]*NL; msk=inner._make_masks(h,cache); inter=[(None,None)]*NL
    for idx in range(start, NL):
        kvs,off=inter[inner.previous_kvs[idx]]
        h,kvs,off=L[idx](h, msk[idx], cache[idx], per_layer_input=None, shared_kv=kvs, offset=off)
        inter[idx]=(kvs,off)
    hn = inner.norm(h)
    logits = inner.embed_tokens.as_linear(hn)
    return mx.sum(logits[:,:,tid]*W)/mx.sum(W)

Z = np.zeros((len(CON), NL+1, 3840), dtype=np.float32)
t0=time.time()
for ci, tid in enumerate(CON_ID):
    for l in range(NL+1):
        if l == NL:
            Z[ci, l] = 0.0; continue
        g = mx.grad(lambda x: rest(x, l, tid))(HS[l])
        mx.eval(g)
        Z[ci, l] = np.array(g.mean(axis=(0,1)).astype(mx.float32))
    n24 = float(np.linalg.norm(Z[ci,24])); n10 = float(np.linalg.norm(Z[ci,10]))
    print(f"  {ci+1}/{len(CON)} {CON[ci]!r}: норма слой10={n10:.4f} слой24={n24:.4f} ({time.time()-t0:.0f} с)", flush=True)

np.save("/tmp/jlens_Z3.npy", Z)
json.dump({"concepts":CON,"ids":[int(i) for i in CON_ID]}, open("/tmp/jlens_meta3.json","w"))
print("ГОТОВО", f"{time.time()-t0:.0f} с", flush=True)
n = np.linalg.norm(Z, axis=2)
print("\nнормы по слоям (среднее по понятиям):")
for l in range(0,NL,2):
    print(f"  {l:2d}: {n[:,l].mean():.4f}")
