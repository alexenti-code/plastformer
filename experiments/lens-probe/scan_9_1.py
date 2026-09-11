
"""Шаг 9.1: геометрический скан слоёв нашего ядра.
Вопрос: выделяется ли средняя полоса, как в статье о J-space.
Метрики: CKA между слоями; logit-lens топ-1; автокорреляция по позициям.
"""
import mlx.core as mx, numpy as np, json, time, sys
from mlx_lm import load

CORE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
t0 = time.time()
model, tok = load(CORE)
inner = model.model
L = inner.layers
print(f"загрузка {time.time()-t0:.1f} с", flush=True)

PROMPTS = [
 "Столица Франции — это город", "Число ног у паука равно",
 "Если все кошки — животные, а Мурка кошка, то Мурка", "Вода закипает при температуре",
 "Автор романа Война и мир", "Первый день недели после воскресенья",
 "Two plus two equals", "The largest planet in the solar system",
 "Сколько дней в неделе", "Кто написал Евгения Онегина",
 "Москва — столица", "Кислород имеет атомный номер",
 "В году месяцев ровно", "Самая длинная река в мире",
 "The capital of Japan is", "Water freezes at",
 "Плюс один к девяти равно", "Корова даёт",
 "Сколько лап у собаки", "Зимой идёт",
 "Берлин находится в стране", "Сколько минут в часе",
 "Корень из четырёх равен", "Железо — это",
 "The opposite of hot is", "A triangle has sides",
 "Птица, которая не летает, но бегает быстрее всех", "Днем светит",
 "Первый президент США", "Сколько букв в русском алфавите",
 "Kitchen is a room where you", "Планета, ближайшая к Солнцу",
 "Кошка говорит", "Цвет неба днём",
 "Число, следующее после семи", "Хлеб делают из",
 "The number of days in a year is", "Солнце встаёт на",
 "Рыба живёт в", "Земля вращается вокруг",
]
maxlen = max(len(tok.encode(p)) for p in PROMPTS)
print("промптов:", len(PROMPTS), "| макс длина:", maxlen, flush=True)

NL = len(L)
acts = [[] for _ in range(NL)]          # активация на последней позиции
acts_all = [[] for _ in range(NL)]      # все позиции (для автокорреляции)
n_pos = []

for pi, p in enumerate(PROMPTS):
    ids = mx.array([tok.encode(p)])
    h = inner.embed_tokens(ids) * inner.embed_scale
    per_layer_inputs = [None]*NL
    cache = [None]*NL
    mask = inner._make_masks(h, cache)
    intermediates = [(None, None)]*NL
    for idx, (layer, msk, c, prev_idx, pli) in enumerate(zip(L, mask, cache, inner.previous_kvs, per_layer_inputs)):
        kvs, offset = intermediates[prev_idx]
        h, kvs, offset = layer(h, msk, c, per_layer_input=None, shared_kv=kvs, offset=offset)
        intermediates[idx] = (kvs, offset)
        a = np.array(h[0].astype(mx.float32))   # (seq, 3840)
        acts[idx].append(a[-1])            # последняя позиция
        acts_all[idx].append(a)
    n_pos.append(a.shape[0])
    if (pi+1) % 10 == 0:
        print(f"  {pi+1}/{len(PROMPTS)} промптов, {time.time()-t0:.0f} с", flush=True)

X = [np.stack(acts[i]) for i in range(NL)]   # (n_prompts, 3840) на слой
print("собрано:", len(X), "слоёв, форма", X[0].shape, flush=True)

# ---- CKA между слоями (линейная, как в статье) ----
def cka(A, B):
    A = A - A.mean(0, keepdims=True); B = B - B.mean(0, keepdims=True)
    num = np.linalg.norm(A.T @ B, "fro")**2
    den = np.linalg.norm(A.T @ A, "fro") * np.linalg.norm(B.T @ B, "fro")
    return float(num/den) if den > 0 else 0.0

print("CKA...", flush=True)
C = np.eye(NL)
for i in range(NL):
    for j in range(i+1, NL):
        C[i, j] = C[j, i] = cka(X[i], X[j])
np.save("/tmp/cka_matrix.npy", C)

# ---- logit lens: точность предсказания следующего токена по слоям ----
norm = inner.norm
emb = inner.embed_tokens
print("logit lens...", flush=True)
lens_top1 = []
for i in range(NL):
    h = mx.array(X[i][:, None, :], dtype=mx.float32)   # (n, 1, 3840)
    hn = norm(h)
    logits = emb.as_linear(hn)[:, -1, :]    # (n, vocab)
    lens_top1.append(np.array(mx.argmax(logits, -1)))
# эталон — последний слой
final = lens_top1[-1]
agree = [float((np.array(lens_top1[i]) == final).mean()) for i in range(NL)]
np.save("/tmp/lens_agree.npy", np.array(agree))

out = {
 "n_prompts": len(PROMPTS), "n_layers": NL,
 "cka_diag_pm1": [float(C[i, i+1]) for i in range(NL-1)],
 "cka_neighbors_dist2": [float(C[i, i+2]) for i in range(NL-2)],
 "cka_neighbors_dist8": [float(C[i, i+8]) for i in range(NL-8)],
 "cka_first_vs_all": [float(C[0, i]) for i in range(NL)],
 "cka_last_vs_all": [float(C[-1, i]) for i in range(NL)],
 "lens_agree_final": agree,
}
json.dump(out, open("/tmp/step1_scan.json", "w"), indent=1)
print("ГОТОВО", f"{time.time()-t0:.0f} с", flush=True)

print()
print("=== CKA: слой 0 против остальных ===")
for i in range(0, NL, 4):
    print(f"  CKA(0,{i:2d}) = {C[0,i]:.3f}")
print()
print("=== CKA: последний слой против остальных ===")
for i in range(0, NL, 4):
    print(f"  CKA({NL-1},{i:2d}) = {C[-1,i]:.3f}")
print()
print("=== CKA между соседними слоями ===")
for i in range(0, NL-1, 4):
    print(f"  CKA({i},{i+1}) = {C[i,i+1]:.3f}")
print()
print("=== logit-lens: согласие с финальным слоем, по слоям ===")
for i in range(0, NL, 3):
    print(f"  слой {i:2d}: {agree[i]:.2f}")
