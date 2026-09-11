
"""Шаг 9.2: пробное чтение промежуточных слоёв словарём модели (logit lens).
Вопрос: видно ли, как понятие «созревает» к середине — как в статье о J-space.
"""
import mlx.core as mx, numpy as np, time
from mlx_lm import load

CORE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
model, tok = load(CORE)
inner = model.model
L = inner.layers
NL = len(L)

MULTIHOP = [
 ("Число ног у животного, которое плетёт паутину, равно", ["паук","паука","spider","восемь","8"]),
 ("Столица страны, где находится Эйфелева башня, это", ["Франц","Париж","France","Paris"]),
 ("Количество колёс у машины, на которой ездит почтальон в России, равно", ["машин","автомобил","четыре","4"]),
 ("The number of legs on the animal that spins webs is", ["spider","паук","eight","8"]),
 ("The capital of the country where the Eiffel Tower stands is", ["France","Paris","Франц","Париж"]),
]

def layerwise(prompt):
    ids = mx.array([tok.encode(prompt)])
    h = inner.embed_tokens(ids) * inner.embed_scale
    cache = [None]*NL
    mask = inner._make_masks(h, cache)
    inter = [(None,None)]*NL
    rows = [np.array(h[0,-1].astype(mx.float32))]
    for idx, (layer, msk, c, prev_idx) in enumerate(zip(L, mask, cache, inner.previous_kvs)):
        kvs, offset = inter[prev_idx]
        h, kvs, offset = layer(h, msk, c, per_layer_input=None, shared_kv=kvs, offset=offset)
        inter[idx] = (kvs, offset)
        rows.append(np.array(h[0,-1].astype(mx.float32)))
    return rows

def top5(vec):
    hn = inner.norm(mx.array(vec[None,None,:], dtype=mx.float32))
    logits = inner.embed_tokens.as_linear(hn)[0,0]
    idx = mx.argsort(logits)[::-1][:5]
    return [(tok.decode([int(i)]), float(logits[int(i)])) for i in idx]

for prompt, expected in MULTIHOP:
    print("="*70)
    print("ПРОМПТ:", prompt)
    rows = layerwise(prompt)
    for li in range(0, NL+1, 2):
        t5 = top5(rows[li])
        words = " | ".join(w.strip() for w,_ in t5)
        mark = "  <<<" if any(e.lower() in words.lower() for e in expected) else ""
        print(f"  слой {li:2d}: {words}{mark}")
    print()
