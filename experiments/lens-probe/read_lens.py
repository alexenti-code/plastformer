
import mlx.core as mx, numpy as np, json
from mlx_lm import load
CORE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
model, tok = load(CORE)
inner = model.model; L = inner.layers; NL = len(L)
Z = np.load("/tmp/jlens_Z3.npy"); meta = json.load(open("/tmp/jlens_meta3.json"))
CON = [c.strip() for c in meta["concepts"]]

# ЦЕНТРИРОВАНИЕ: убираем общее для всех понятий направление на каждом слое
Zc = Z - Z.mean(axis=0, keepdims=True)
Zc = Zc / np.maximum(np.linalg.norm(Zc, axis=2, keepdims=True), 1e-9)

def acts(prompt):
    ids = mx.array([tok.encode(prompt)])
    h = inner.embed_tokens(ids) * inner.embed_scale
    cache=[None]*NL; msk=inner._make_masks(h,cache); inter=[(None,None)]*NL
    rows=[np.array(h[0,-1].astype(mx.float32))]
    for idx,(layer,m,c,prev) in enumerate(zip(L,msk,cache,inner.previous_kvs)):
        kvs,off=inter[prev]
        h,kvs,off=layer(h,m,c,per_layer_input=None,shared_kv=kvs,offset=off)
        inter[idx]=(kvs,off); rows.append(np.array(h[0,-1].astype(mx.float32)))
    return rows

TESTS = [
 ("Число ног у животного, которое плетёт паутину, равно", ["паук","spider"]),
 ("The number of legs on the animal that spins webs is", ["spider","паук"]),
 ("Столица страны, где находится Эйфелева башня, это", ["Франция","Париж","France","Paris"]),
 ("Красная планета, четвёртая от Солнца, это", ["Марс"]),
]
for prompt, expect in TESTS:
    rows = acts(prompt)
    print("="*74)
    print("ПРОМПТ:", prompt, "| ожидаем:", expect)
    hits=[]
    for l in range(6, NL+1, 3):
        r = rows[l] / max(np.linalg.norm(rows[l]), 1e-9)
        sc = Zc[:, l, :] @ r
        order = np.argsort(-sc)[:4]
        words = [CON[i] for i in order]
        hit = any(e in words for e in expect)
        if hit: hits.append(l)
        print(f"  слой {l:2d}: {', '.join(words)}{'  <<<' if hit else ''}")
    print(f"  ПОПАДАНИЯ на слоях: {hits}")
    print()
