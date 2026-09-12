#!/usr/bin/env python3
"""Круг возврата: исполнение актов модели и подтверждение <<ENV>>.

Зачем. В обучении каждый ответ модели сопровождался подтверждением от кода:
разобранные акты исполнялись, а модели возвращался блок <<ENV>> с номерами
записей и новым тиком (867 таких блоков в материале v04). На изделии этого
круга не было, поэтому: записи Φ не читались моделью при ответе, счётчик
record_tick стоял на 1 (читать было нечего) и источник времени отсутствовал.

Что делает этот модуль:
  parse_acts   — вынуть блок актов из ответа модели;
  run_acts     — исполнить акты (запись в Φ2, чтение, скан, правка ручек);
  env_block    — собрать текст подтверждения <<ENV>> в формате обучения;
  step         — один ход целиком: ответ -> акты -> подтверждение;
  phi_state    — собрать Φ-состояние (записи, поданные в восприятие).

Правила, взятые из обучения (не выдуманы):
  * тик двигают только пишущие акты name/repeat/connect/reconcile — по +1 на акт;
    чтения и скан тик не двигают;
  * громкость записи: weight = (1 + повторы) * exp(-(tick - record_tick) / tau),
    где tau по слоям t1=10, t2=50, t3=200, t4=1000, t5=5000;
  * подтверждение записи: {"ok": true, "written": [{"id", "act"}], "tick"};
  * подтверждение чтения: {"records": [{id, act, layer, content, valid_time,
    record_time, record_tick, weight}], "tick"};
  * подтверждение скана: {"scan": true, "records": [{id, tick, layer, weight}], "tick"}.

Честная граница. Текст записи в Φ не хранится — там вектор содержания
(1920 чисел). Декодирования вектора обратно в текст нет (не построено).
Поэтому текст записи лежит рядом, в текстовом указателе
(служебная область): <папка модели>/phi-content.jsonl. Это названо
ограничением, а не полным чтением из Φ.
"""
import json
import os
import re
import time
from datetime import datetime, timezone

import numpy as np

from phi import (phi_open, phi_write, phi_read, phi_scan, phi_calibrate,
                 phi_apply_calibration, phi_knobs, VEC_NUMS,
                 decayed, loudness, audible)

from phi import TAU_TICKS  # единый источник: затухание считает phi.py
WRITE_ACTS = ("name", "repeat", "connect", "reconcile")
LAYERS = ("t1", "t2", "t3", "t4", "t5")
CONTENT_STORE = "phi-content.jsonl"

ACT_BLOCK_RE = re.compile(r"```json\s*(\[.*?\])\s*```", re.S)


# ----------------------------------------------------------------- разбор
def parse_acts(text):
    """Вынуть акты из ответа модели. Возвращает список словарей."""
    acts = []
    for m in ACT_BLOCK_RE.finditer(text):
        try:
            blk = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(blk, dict):
            blk = [blk]
        for a in blk:
            if isinstance(a, dict) and "act" in a:
                acts.append(a)
    return acts


# ------------------------------------------------- текстовый указатель записей
def _store_path(model_path):
    return os.path.join(os.path.dirname(os.path.abspath(model_path)), CONTENT_STORE)


def load_content(model_path):
    """Прочитать текстовый указатель: номер записи -> описание записи."""
    p = _store_path(model_path)
    out = {}
    if not os.path.exists(p):
        return out
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            out[int(e["id"])] = e
    return out


def append_content(model_path, entries):
    p = _store_path(model_path)
    with open(p, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ время
def stamp(t=None):
    """Аудируемая метка времени в виде ISO (как в обучении).

    Часы ставит код, а не модель: по канону настенные метки — только для
    аудита и в физику памяти не входят (CONSTITUTION, О-4). Значение epoch
    кладётся в запись Φ, строка ISO уходит модели в подтверждении.
    """
    t = time.time() if t is None else t
    local = datetime.fromtimestamp(t).astimezone()
    return int(t), local.isoformat(timespec="seconds")


# ------------------------------------------------------------------ громкость
def weight_of(rec, tick, repeats):
    """Громкость следа сейчас: амплитуды, ослабшие за прожитые тики.

    Закон (Теория §4, О-10): каждая из пяти компонент слабеет своей τ.
    Здесь амплитуды берутся те, что лежат в Φ (уже с затуханием, если его
    применили), и дополнительно домножаются на затухание от тика записи —
    на случай, когда физику не успели применить при записи.
    """
    dn = max(0, tick - int(rec.get("record_tick", tick)))
    a0 = rec.get("amplitudes") or rec.get("amp0")
    if a0 is None:
        tau = TAU_TICKS.get(rec.get("layer", "t2"), 50)
        base = float(np.exp(-dn / tau))
        return round((1 + repeats) * base, 3)
    a = decayed(a0, rec.get("layer", "t2"), dn)
    return round((1 + repeats) * loudness(a), 3)


def _repeats_of(records, rid):
    return sum(1 for r in records if r.get("act") == "repeat" and rid in (r.get("refs") or []))


# --------------------------------------------------------- исполнение актов
def run_acts(model_path, acts, vector_of=None, now=None, scan_limit=8):
    """Исполнить акты модели. Возвращает payload для блока <<ENV>>.

    vector_of(text, layer) -> (вектор 1920 чисел, пять амплитуд). В рабочем
    режиме это снятие с ядра (plastformer/vector.py: capture_centered +
    amplitudes). Если не задан, берётся детерминированная заглушка — она
    помечена в подтверждении и в отчёте.
    """
    head_tick = int(phi_open(model_path)["tick"])
    tick = head_tick
    store = load_content(model_path)
    written, records, scans, calib = [], [], [], []
    new_store = []

    def all_records():
        """Все записи Φ2 с текстом из указателя."""
        out = []
        for r in phi_read(model_path, kind="phi2", mode="all"):
            rid = int(r["num"]) + 1
            e = store.get(rid, {})
            out.append({
                "id": rid, "tick": int(r["tick"]),
                "record_tick": int(r["tick"]) or e.get("record_tick", 0),
                "layer": e.get("layer", "t2"), "act": e.get("act", "name"),
                "content": e.get("content", ""), "refs": e.get("refs", []),
                "valid_time_iso": e.get("valid_time", ""),
                "record_time_iso": e.get("record_time", ""),
            })
        return out

    for a in acts:
        kind = a.get("act")
        if kind in WRITE_ACTS:
            tick += 1
            epoch, iso = stamp(now)
            content = a.get("content", "")
            layer = a.get("layer") if a.get("layer") in LAYERS else "t4"
            if vector_of:
                vec, amp = vector_of(content, layer)
            else:
                vec, amp = _placeholder(content), np.ones(5, dtype=np.float32)
            num = phi_write(model_path, "phi2", vec, amp, valid_time=epoch, tick=tick,
                            source=a.get("source", "user"), layer_taken=_layer_index(layer))
            rid = int(num) + 1
            entry = {"id": rid, "act": kind, "content": content, "layer": layer,
                     "refs": a.get("refs") or [], "valid_time": iso, "record_time": iso,
                     "record_tick": tick}
            store[rid] = entry
            new_store.append(entry)
            written.append({"id": rid, "act": kind})
            records.append(entry)

        elif kind == "read":
            tick = tick                       # чтение тик не двигает
            recs = all_records()
            if not recs:
                records.append(None)
                continue
            mode = a.get("mode", "last")
            if mode == "ids":
                want = set(a.get("ids") or [])
                picked = [r for r in recs if r["id"] in want]
            elif mode in ("from/to", "range"):
                lo, hi = int(a.get("from", 0)), int(a.get("to", 10 ** 9))
                picked = [r for r in recs if lo <= r["id"] <= hi]
            else:
                n = int(a.get("count") or 12)
                recs2 = sorted(recs, key=lambda r: -r["id"])[-max(n, 1):]
                picked = recs2
            for r in picked:
                r["weight"] = weight_of(r, tick, _repeats_of(recs, r["id"]))
            records.append(picked)

        elif kind == "scan":
            n = int(a.get("count") or scan_limit)
            recs = all_records()[-max(n, 1):]
            scans.append([{"id": r["id"], "tick": r["record_tick"], "layer": r["layer"],
                           "weight": weight_of(r, tick, _repeats_of(all_records(), r["id"]))}
                          for r in recs])

        elif kind == "calibrate":
            prop = a.get("proposal") or {}
            for knob, value in prop.items():
                d = phi_calibrate(model_path, {"knob": knob, "value": value},
                                  evidence=a.get("evidence"))
                if d.get("accepted"):
                    phi_apply_calibration(model_path, d)
                calib.append(d)

    if new_store:
        append_content(model_path, new_store)

    # --- собрать подтверждение в формате обучения
    def rec_view(r):
        return {"id": r["id"], "act": r["act"], "layer": r["layer"],
                "content": r["content"], "valid_time": r["valid_time_iso"],
                "record_time": r["record_time_iso"], "record_tick": r["record_tick"],
                "weight": r.get("weight", weight_of(r, tick, 0))}

    if written:
        payload = {"ok": True, "written": written, "tick": tick}
    elif scans:
        payload = {"scan": True, "records": scans[-1], "tick": tick}
    elif records:
        last = records[-1]
        payload = {"records": [rec_view(r) for r in (last or [])], "tick": tick}
    elif calib:
        d = calib[-1]
        payload = ({"ok": True, "applied": {"knob": d["knob"], "from": d["from"],
                                            "to": d["to"]}, "tick": tick}
                   if d.get("accepted") else
                   {"ok": False, "rejected": {"knob": d.get("knob"), "why": d.get("why")},
                    "tick": tick})
    else:
        payload = {"ok": True, "written": [], "tick": tick}
    return payload


def _layer_index(layer):
    return LAYERS.index(layer) if layer in LAYERS else 3


def _placeholder(text):
    """Заглушка вектора: детерминированная, пока нет снятия с ядра.

    Помечена в отчёте как ограничение: настоящий вектор берётся из скрытого
    состояния ядра на слое снятия записи.
    """
    import hashlib
    seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:4], "big")
    return np.random.default_rng(seed).normal(size=VEC_NUMS).astype(np.float32)


def env_block(payload):
    """Текст подтверждения ровно в формате обучения."""
    return "<<ENV>>\n" + json.dumps(payload, ensure_ascii=False)


# ------------------------------------------------------- Φ-состояние (подача)
def phi_state(model_path, limit=None):
    """Записи Φ, которые подаются в восприятие: самые громкие (постоянный префикс).

    Возвращает список: номер, слой, громкость, текст, вектор.
    Вектор — отклонение от общей основы (см. vector.capture_centered): именно
    отклонение несёт различие между записями, сырое состояние почти одинаково
    для любых текстов и подавать его — значит подавать постоянное смещение.

    Исправлено 12.09.2026: здесь стояло требование «проекция на основу рабочей
    полосы». Отменено — проекция нужна чужим векторам, наш снят с того же ядра
    и слоя. Форма вектора — как снято.
    """
    h = phi_open(model_path)
    tick = int(h["tick"])
    if limit is None:
        limit = int(h.get("knob_prefix_depth", 12))
    store = load_content(model_path)
    recs = phi_read(model_path, kind="phi2", mode="last", n=limit)
    out = []
    for r in recs:
        rid = int(r["num"]) + 1
        e = store.get(rid, {})
        out.append({"id": rid, "layer": e.get("layer", "t2"), "loudness": r["loudness"],
                    "content": e.get("content", ""), "vector": r["vector"]})
    return out


def inject(input_embeddings, state_vectors):
    """Собрать вход с Φ-состоянием: записи идут префиксом, до внимания.

    Место подачи по docs/DESIGN-PARAMETRIC-PHI.md §4: память входит в поле
    внимания вместе с вопросом. Вызывать с готовыми векторами на основе полосы.
    """
    import mlx.core as mx
    if not state_vectors:
        return input_embeddings
    pref = mx.stack([mx.array(v) for v in state_vectors])[None, :, :]
    return mx.concatenate([pref, input_embeddings], axis=1)
