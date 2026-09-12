#!/usr/bin/env python3
"""Снятие вектора содержания с ядра и запись в Φ (узел C).

Зачем. В первой редакции круга вектор записи был заглушкой — случайным шумом
от текста (`_placeholder`). Это подмена: в Φ лежало не состояние модели.
Здесь вектор берётся с того же ядра, куда потом подаётся.

Механика (проверено 12.09.2026):
  * вход  -> embed_tokens * embed_scale;
  * прогон по слоям вручную, как в Gemma4TextModel.__call__: нужны masks,
    shared_kv и offset, иначе слой получает кортеж и падает;
  * снимаем состояние ПОСЛЕ нужного слоя (по умолчанию 21);
  * берём последнюю позицию (последний токен) — это состояние «после прочитанного»;
  * 3840 чисел бьются до 1920: соседние пары усредняются, затем сжатие к размаху
    делает phi_write (полбайта на число).

Слой снятия. Место подачи и слой снятия обязаны совпадать. По замеру полосы
(шов на 10→11) рабочий слой — середина полосы. Значение берётся из manifest
изделия и записывается в поле layer_taken каждой записи.
"""
import numpy as np
import mlx.core as mx

DEFAULT_LAYER = 21          # 1-based номер: состояние ПОСЛЕ 21-го слоя (индекс 20)
VEC_DIM = 3840              # скрытая размерность ядра
VEC_NUMS = 1920             # чисел в записи Φ


def load_core(model_dir):
    """Загрузить модель. Возвращает (model, tokenizer)."""
    from mlx_lm import load
    return load(model_dir)


def capture(model, tok, text, layer=DEFAULT_LAYER):
    """Снять состояние последнего токена после слоя `layer` (1-based).

    Возвращает numpy-вектор из VEC_NUMS чисел (3840 -> усреднение пар -> 1920).
    """
    inner = model.model
    layers = inner.layers
    n = len(layers)
    if not 1 <= layer <= n:
        raise ValueError(f"слой {layer} вне диапазона 1..{n}")

    ids = tok.encode(text)
    if not ids:
        ids = [tok.bos_token_id or 0]
    arr = mx.array([ids])

    x = inner.embed_tokens(arr) * inner.embed_scale
    if getattr(inner, "hidden_size_per_layer_input", None):
        per = inner._get_per_layer_inputs(arr, x)
        per = inner._project_per_layer_inputs(x, per)
        per = [per[:, :, i, :] for i in range(n)]
    else:
        per = [None] * n

    cache = [None] * n
    masks = inner._make_masks(x, cache)
    inter = [(None, None)] * n
    out = None
    for idx, (lay, c, mask, prev_idx, pli) in enumerate(
            zip(layers, cache, masks, inner.previous_kvs, per)):
        kvs, offset = inter[prev_idx]
        x, kvs, offset = lay(x, mask, c, per_layer_input=pli,
                             shared_kv=kvs, offset=offset)
        inter[idx] = (kvs, offset)
        mx.eval(x)
        if idx == layer - 1:
            out = np.array(x[0, -1, :].astype(mx.float32))
            break
    if out is None:
        raise RuntimeError("состояние не снято")
    # 3840 -> 1920: усреднение соседних пар (сохраняет и чётные, и нечётные)
    v = out.reshape(-1, 2).mean(axis=1) if out.size == VEC_DIM else out[:VEC_NUMS]
    return v.astype(np.float32)


def amplitudes(model, tok, text, layer=DEFAULT_LAYER):
    """Пять амплитуд — быстрые компоненты спектра (по ADR-005 §4).

    Мера — норма состояния: чем сильнее отклик ядра на текст, тем громче след.
    Раскладка по пяти τ — затухающая шкала: свежий след силён в быстрых
    компонентах, медленные получают меньшую долю. Это физика записи, а не
    украшение: именно эти числа слабеют с тиками.
    """
    v = capture(model, tok, text, layer)
    norm = float(np.linalg.norm(v))
    if norm == 0:
        return np.full(5, 0.01, dtype=np.float32)
    # нормируем к разумному диапазону громкости, затем раскладываем по τ-спектру
    loud = min(1.0, norm / 300.0)
    share = np.array([1.00, 0.80, 0.64, 0.51, 0.41], dtype=np.float32)
    return (loud * share).astype(np.float32)


# ------------------------------------------------------------ основа (baseline)
# Замер 12.09.2026: сырые векторы средних слоёв почти совпадают (сходство 0,97-0,99),
# но после вычитания общего направления сходство падает до -0,2...-0,3. Значит,
# почти всё в векторе — общее для любых текстов, и смысл несут ~1 % разброса.
# Поэтому записываем и подаём ОТКЛОНЕНИЕ от основы, а не сырой вектор.
# Это то же, что «проекция на основу полосы» из плана, но основа берётся не из
# шумного объектива, а измеряется прямо на ядре: среднее по опорным фразам.

BASE_PHRASES = (
    "запись", "факт", "проект", "работа", "вопрос", "ответ",
    "срок", "сумма", "имя", "место", "время", "решение",
)


def baseline(model, tok, layer=DEFAULT_LAYER, cache={}):
    """Общее направление: среднее по опорным фразам. Считается один раз на процесс."""
    key = (id(model), layer)
    if key in cache:
        return cache[key]
    vs = [capture(model, tok, p, layer) for p in BASE_PHRASES]
    m = np.mean(vs, axis=0).astype(np.float32)
    cache[key] = m
    return m


def capture_centered(model, tok, text, layer=DEFAULT_LAYER):
    """Вектор записи: отклонение состояния от общего направления.

    Именно это несёт различие между записями; сырой вектор почти одинаков
    для любых текстов и подавать его — значит подавать постоянное смещение.
    """
    v = capture(model, tok, text, layer)
    b = baseline(model, tok, layer)
    return (v - b).astype(np.float32)
