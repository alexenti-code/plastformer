
"""Шаг 9.3: построение якобиева объектива для нашего ядра.

Идея (по статье): вектор объектива для понятия t на слое l —
это средний по корпусу градиент оценки токена t по активации слоя l.
Один обратный проход даёт градиенты сразу по всем слоям.
"""
import mlx.core as mx, numpy as np, time, json
from mlx_lm import load

CORE = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
model, tok = load(CORE)
inner = model.model
L = inner.layers
NL = len(L)

# ---- корпус для усреднения (тот же класс, что в статье: обычные подсказки) ----
CORPUS = [
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
 "Птица, которая не летает", "Днем светит",
 "Первый президент США", "Сколько букв в русском алфавите",
]
# ---- понятия, для которых строим векторы объектива ----
CONCEPTS = [" паук"," паука"," муравей"," восемь"," шесть"," восемь"," 8", " 6",
            " Франция"," Париж"," Франции"," Париже"," Марс"," Марса",
            " красный"," красного"," четыре"," четыре"," кислород"," вода",
            "spider","ant","eight","six","France","Paris","Mars","red","oxygen","water"]

# убрать дубли, сохранить порядок
seen=set(); CON=[]
for c in CONCEPTS:
    if c not in seen:
        seen.add(c); CON.append(c)
CON_ID = []
for c in CON:
    ids = tok.encode(c)
    CON_ID.append(ids[0])   # первый токен
print("понятий:", len(CON), flush=True)
print("примеры:", [(c, i, tok.decode([i])) for c,i in list(zip(CON, CON_ID))[:8]], flush=True)

ids_batch = [tok.encode(p) for p in CORPUS]
maxlen = max(len(x) for x in ids_batch)
pad = tok.encoder.get("<pad>", 0) if hasattr(tok,'encoder') else 0
padded = np.zeros((len(ids_batch), maxlen), dtype=np.int32)
mask = np.zeros((len(ids_batch), maxlen), dtype=np.float32)
for i, x in enumerate(ids_batch):
    padded[i, :len(x)] = x
    mask[i, :len(x)] = 1.0
X = mx.array(padded)
print("батч:", X.shape, flush=True)

def forward_save(X):
    h = inner.embed_tokens(X) * inner.embed_scale
    cache = [None]*NL
    msk = inner._make_masks(h, cache)
    inter = [(None,None)]*NL
    saved = [h]
    for idx, (layer, m, c, prev) in enumerate(zip(L, msk, cache, inner.previous_kvs)):
        kvs, off = inter[prev]
        h, kvs, off = layer(h, m, c, per_layer_input=None, shared_kv=kvs, offset=off)
        inter[idx] = (kvs, off)
        saved.append(h)
    return saved

t0=time.time()
SAVED = forward_save(X)
mx.eval(SAVED)
print(f"forward корпуса: {time.time()-t0:.1f} с", flush=True)
SAVED = [s for s in SAVED]   # отвязать

def make_f(saved):
    """Прогон модели с подстановкой сохранённых активаций; возвращает сумму логитов по всем позициям."""
    h = saved[0]
    cache = [None]*NL
    msk = inner._make_masks(h, cache)
    inter = [(None,None)]*NL
    for idx, (layer, m, c, prev) in enumerate(zip(L, msk, cache, inner.previous_kvs)):
        kvs, off = inter[prev]
        h_in = saved[idx]
        h, kvs, off = layer(h_in, m, c, per_layer_input=None, shared_kv=kvs, offset=off)
        inter[idx] = (kvs, off)
    hn = inner.norm(h)
    logits = inner.embed_tokens.as_linear(hn)
    return logits

def logit_of(saved, tgt):
    lg = make_f(saved)                       # (B, T, V)
    return mx.sum(lg[:, :, tgt] * mx.array(mask)) / mx.sum(mx.array(mask))

Z = np.zeros((len(CON), NL+1, 3840), dtype=np.float32)
t0 = time.time()
for ci, (name, tid) in enumerate(zip(CON, CON_ID)):
    g = mx.grad(lambda s: logit_of(s, tid))(SAVED)
    mx.eval(g)
    for l in range(NL+1):
        Z[ci, l] = np.array(g[l].mean(axis=(0,1)).astype(mx.float32))
    if (ci+1) % 5 == 0:
        print(f"  {ci+1}/{len(CON)} понятий, {time.time()-t0:.0f} с", flush=True)

np.save("/tmp/jlens_Z.npy", Z)
json.dump({"concepts": CON, "ids": [int(i) for i in CON_ID]}, open("/tmp/jlens_meta.json","w"))
mx.save_safetensors("/tmp/jlens_saved.safetensors", {f"h{l}": SAVED[l] for l in range(NL+1)})
np.save("/tmp/corpus_ids.npy", padded)
print("ГОТОВО", f"{time.time()-t0:.0f} с", flush=True)
