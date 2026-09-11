#!/usr/bin/env python3
"""Работа с Φ — пластичной частью единого файла A = (K, Φ).

Φ живёт ХВОСТОВЫМ РЕГИОНОМ файла весов: обычные тензоры кончаются на
известном смещении, за ними лежат байты Φ. Шапка весов не меняется,
модель о Φ не знает — читает и пишет код.

Восемь функций:
  phi_open      — открыть Φ, прочитать шапку
  phi_write     — записать одну запись
  phi_read      — прочитать записи
  phi_resident  — собрать постоянный префикс (самые громкие)
  phi_calibrate — обработать акт calibrate (границы, бюджет)
  phi_scan      — отдать настоящие числа физики
  phi_knobs     — читать/писать значения ручек в шапке
  phi_project   — взять проекцию вектора на основу рабочей полосы

Только стандартная библиотека и numpy.
"""
import json
import os
import struct
import time

import numpy as np

MAGIC = "PLASTPHI"
VERSION = 1
HEADER_RESERVE = 4096          # 4 КБ под шапку
VEC_NUMS = 1920                # чисел в векторе содержания
VEC_BYTES = VEC_NUMS // 2      # полбайта на число = 960 байт
SERVICE = 43                   # 20 амплитуды + 8 valid_time + 4 tick + 1 источник + 8 номер + 2 слой
REC_SIZE = VEC_BYTES + SERVICE # 1003 байта

# ручки: стартовые значения (утверждены владельцем 06.09.2026)
DEFAULT_KNOBS = {
    "audibility_floor": 0.01,
    "surfacing_cap": 12.0,
    "consolidation_ceiling": 8.0,
    "interference_factor": 1.0,
    "prefix_depth": 12.0,
    "residency_horizon": 10.0,
    "rebuild_period": 1.0,
    "gap_threshold": 100.0,
    "surprise_threshold": 0.9,
    "tau_multiplier.t1": 1.0,
    "tau_multiplier.t2": 1.0,
    "tau_multiplier.t3": 1.0,
    "tau_multiplier.t4": 1.0,
    "tau_multiplier.t5": 1.0,
}
FROZEN_KNOBS = ("act_price", "self_improvement")
KNOB_BOUNDS = {"tau_multiplier": (0.5, 2.0), "default": (0.5, 1.5)}

SOURCE_CODES = {"user": 0, "own_derivation": 1, "tool_result": 2}
SOURCE_NAMES = {v: k for k, v in SOURCE_CODES.items()}


# ---------------------------------------------------------------- смещение Φ
def _tensor_end(path):
    """Смещение, где кончаются объявленные тензоры файла весов."""
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
    data_start = 8 + n
    end = 0
    for k, v in header.items():
        if k == "__metadata__":
            continue
        off = v["data_offsets"][1]
        if off > end:
            end = off
    return data_start + end


def _header_len(path, offset):
    with open(path, "rb") as f:
        f.seek(offset)
        return struct.unpack("<I", f.read(4))[0]


# ------------------------------------------------------------------- открыть
def phi_open(path):
    """Прочитать шапку Φ. Возвращает словарь состояния."""
    offset = _tensor_end(path)
    with open(path, "rb") as f:
        f.seek(offset)
        n = struct.unpack("<I", f.read(4))[0]
        raw = f.read(n)
    if not raw:
        raise ValueError("Φ не создана: за тензорами ничего нет")
    head = json.loads(raw.decode("utf-8"))
    if head.get("magic") != MAGIC:
        raise ValueError(f"не Φ: magic={head.get('magic')!r}")
    head["_offset"] = offset
    head["_path"] = path
    head["_rec"] = head.get("rec", REC_SIZE)
    return head


def _write_header(path, head):
    offset = head["_offset"]
    clean = {k: v for k, v in head.items() if not k.startswith("_")}
    raw = json.dumps(clean, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > HEADER_RESERVE - 4:
        raise ValueError(f"шапка Φ не влезает: {len(raw)} байт")
    with open(path, "r+b") as f:
        f.seek(offset)
        f.write(struct.pack("<I", len(raw)))
        f.write(raw)
        f.write(b"\x00" * (HEADER_RESERVE - 4 - len(raw)))
    head.update(clean)
    return head


# ------------------------------------------------------------------ создание
def phi_create(path, phi1_bytes, phi2_bytes, knobs=None, budget_scan=6,
               budget_calibrate=3, rec=REC_SIZE):
    """Дописать хвостовой регион Φ к существующему файлу весов.

    Возвращает шапку. Вызывается ОДИН РАЗ при сборке изделия.
    """
    if _tensor_end(path) != os.path.getsize(path):
        raise ValueError("в файле уже есть хвост — Φ, похоже, создана")
    offset = os.path.getsize(path)
    n1 = phi1_bytes // rec
    n2 = phi2_bytes // rec
    head = {
        "magic": MAGIC, "v": VERSION, "rec": rec,
        "n1": n1, "n2": n2, "tick": 0,
        "bytes_phi1": n1 * rec, "bytes_phi2": n2 * rec,
        "written1": 0, "written2": 0,
        "budget_scan": budget_scan, "budget_calibrate": budget_calibrate,
        "scan_used": 0, "calibrate_used": 0,
        "physics": 1,
    }
    for k, v in (knobs or DEFAULT_KNOBS).items():
        head["knob_" + k] = v
    with open(path, "ab") as f:
        f.write(b"\x00" * (HEADER_RESERVE + n1 * rec + n2 * rec))
    head["_offset"] = offset
    head["_path"] = path
    return _write_header(path, head)


# ------------------------------------------------------------------ записать
def _encode_vector(vec):
    """Вектор 1920 чисел → 960 байт (полбайта на число, сжатие к размаху)."""
    v = np.asarray(vec, dtype=np.float32).ravel()[:VEC_NUMS]
    if v.size < VEC_NUMS:
        v = np.pad(v, (0, VEC_NUMS - v.size))
    lo, hi = float(v.min()), float(v.max())
    span = hi - lo if hi > lo else 1.0
    q = np.clip(((v - lo) / span * 15.0).round(), 0, 15).astype(np.uint8)
    return q, lo, hi


def _pack_half(q):
    """Две 4-битных величины в один байт."""
    q = np.asarray(q, dtype=np.uint8)
    pairs = q[0::2] | (q[1::2] << 4)
    return pairs.tobytes()


def _unpack_half(raw, n=VEC_NUMS):
    b = np.frombuffer(raw, dtype=np.uint8)
    lo = b & 0x0F
    hi = (b >> 4) & 0x0F
    q = np.empty(n, dtype=np.uint8)
    q[0::2] = lo
    q[1::2] = hi
    return q.astype(np.float32) / 15.0


def phi_write(path, kind, vector, amplitudes, valid_time, tick,
              source="user", layer_taken=24, knobs=None):
    """Записать одну запись. kind: 'phi1' или 'phi2'. Возвращает номер."""
    head = phi_open(path)
    rec = head["_rec"]
    is1 = kind == "phi1"
    written = head["written1" if is1 else "written2"]
    cap = head["n1" if is1 else "n2"]
    if written >= cap:
        written = _evict(path, head, kind)          # вытеснение старейшей
    base = head["_offset"] + HEADER_RESERVE
    if not is1:
        base += head["bytes_phi1"]
    q, lo, hi = _encode_vector(vector)
    amp = np.asarray(amplitudes, dtype=np.float32).ravel()
    amp = np.pad(amp, (0, max(0, 5 - amp.size)))[:5]
    payload = (
        _pack_half(q)
        + amp.tobytes()
        + struct.pack("<q", int(valid_time))
        + struct.pack("<i", int(tick))
        + struct.pack("<B", SOURCE_CODES.get(source, 0))
        + struct.pack("<q", int(written))
        + struct.pack("<h", int(layer_taken))
    )
    assert len(payload) == rec, (len(payload), rec)
    with open(path, "r+b") as f:
        f.seek(base + written * rec)
        f.write(payload)
    head["written1" if is1 else "written2"] = written + 1
    head["tick"] = max(head["tick"], int(tick))
    _write_header(path, head)
    return written


def _evict(path, head, kind):
    """Вытеснить старейшие записи: сдвиг области на одну запись влево."""
    rec = head["_rec"]
    is1 = kind == "phi1"
    cap = head["n1" if is1 else "n2"]
    base = head["_offset"] + HEADER_RESERVE + (0 if is1 else head["bytes_phi1"])
    size = cap * rec
    with open(path, "r+b") as f:
        f.seek(base + rec)
        blob = f.read(size - rec)
        f.seek(base)
        f.write(blob)
    return cap - 1


# ------------------------------------------------------------------ прочитать
def _decode_record(raw, rec):
    v = _unpack_half(raw[:VEC_BYTES])
    o = VEC_BYTES
    amp = np.frombuffer(raw[o:o + 20], dtype=np.float32).copy()
    o += 20
    valid_time = struct.unpack("<q", raw[o:o + 8])[0]; o += 8
    tick = struct.unpack("<i", raw[o:o + 4])[0]; o += 4
    src = raw[o]; o += 1
    num = struct.unpack("<q", raw[o:o + 8])[0]; o += 8
    layer = struct.unpack("<h", raw[o:o + 2])[0]
    return {
        "num": num, "tick": tick, "valid_time": valid_time,
        "source": SOURCE_NAMES.get(src, "?"), "layer_taken": layer,
        "amplitudes": amp.tolist(), "loudness": float(amp.max()),
        "vector": v,
    }


def phi_read(path, kind="phi2", mode="last", n=12, ids=None):
    """Прочитать записи. mode: last (n самых громких) | ids | all."""
    head = phi_open(path)
    rec = head["_rec"]
    is1 = kind == "phi1"
    written = head["written1" if is1 else "written2"]
    base = head["_offset"] + HEADER_RESERVE + (0 if is1 else head["bytes_phi1"])
    if written == 0:
        return []
    with open(path, "rb") as f:
        f.seek(base)
        blob = f.read(written * rec)
    out = []
    for i in range(written):
        raw = blob[i * rec:(i + 1) * rec]
        if len(raw) < rec:
            break
        out.append(_decode_record(raw, rec))
    if mode == "ids" and ids:
        want = set(ids)
        out = [r for r in out if r["num"] in want]
    elif mode == "last":
        out.sort(key=lambda r: -r["loudness"])
        out = out[:n]
    return out


def phi_resident(path, limit=None):
    """Постоянный префикс: самые громкие записи Φ2."""
    head = phi_open(path)
    if limit is None:
        limit = int(head.get("knob_prefix_depth", 12))
    return phi_read(path, kind="phi2", mode="last", n=limit)


# -------------------------------------------------------------- ручки и скан
def phi_knobs(path, updates=None):
    """Прочитать или обновить значения ручек в шапке Φ."""
    head = phi_open(path)
    if updates:
        for k, v in updates.items():
            if k in FROZEN_KNOBS:
                raise ValueError(f"ручка {k} заморожена")
            head["knob_" + k] = v
        _write_header(path, head)
        return {k: v for k, v in head.items() if k.startswith("knob_")}
    return {k[len("knob_"):]: v for k, v in head.items() if k.startswith("knob_")}


def phi_scan(path, kind="phi1", mode="summary"):
    """Отдать НАСТОЯЩИЕ числа физики: амплитуды, тики, слои."""
    head = phi_open(path)
    if mode == "summary":
        return {
            "tick": head["tick"],
            "phi1_written": head["written1"], "phi1_cap": head["n1"],
            "phi2_written": head["written2"], "phi2_cap": head["n2"],
            "knobs": phi_knobs(path),
            "scan_left": head["budget_scan"] - head["scan_used"],
        }
    recs = phi_read(path, kind=kind, mode="all")
    if mode == "ticks":
        return {"ticks": [r["tick"] for r in recs]}
    return {"amplitudes": [r["amplitudes"] for r in recs],
            "loudness": [r["loudness"] for r in recs],
            "layers": [r["layer_taken"] for r in recs]}


def phi_calibrate(path, proposal, evidence=None):
    """Обработать акт calibrate: перечень, границы, бюджет."""
    head = phi_open(path)
    knob = proposal.get("knob") or proposal.get("name")
    value = proposal.get("value")
    if knob in FROZEN_KNOBS:
        return {"accepted": False, "why": f"ручка {knob} заморожена"}
    if knob not in DEFAULT_KNOBS:
        return {"accepted": False, "why": f"ручки {knob!r} нет в перечне"}
    if head["calibrate_used"] >= head["budget_calibrate"]:
        return {"accepted": False, "why": "бюджет правок исчерпан"}
    cur = float(head.get("knob_" + knob, DEFAULT_KNOBS[knob]))
    lo, hi = KNOB_BOUNDS["tau_multiplier"] if knob.startswith("tau_multiplier") else KNOB_BOUNDS["default"]
    ratio = float(value) / cur if cur else float("inf")
    if not (lo <= ratio <= hi):
        return {"accepted": False, "why": f"выход за границы: {ratio:.2f} не в [{lo};{hi}]",
                "knob": knob, "current": cur, "proposed": value}
    return {"accepted": True, "knob": knob, "from": cur, "to": float(value),
            "applies_from": "следующий эпизод", "evidence": evidence or []}


def phi_apply_calibration(path, decision):
    """Применить принятую правку: обновить ручку и списать бюджет."""
    if not decision.get("accepted"):
        return decision
    head = phi_open(path)
    head["knob_" + decision["knob"]] = decision["to"]
    head["calibrate_used"] += 1
    _write_header(path, head)
    return decision


# ------------------------------------------------------------------ проекция
def phi_project(head_path, vector, basis_path=None):
    """Проекция вектора на основу рабочей полосы.

    Если basis_path не задан, возвращает вектор без изменений
    (заглушка до построения объектива).
    """
    if basis_path is None or not os.path.exists(basis_path):
        return np.asarray(vector, dtype=np.float32)
    B = np.load(basis_path)          # (k, d) — основа
    v = np.asarray(vector, dtype=np.float32).ravel()
    B = B.reshape(B.shape[0], -1)
    coef = B @ v / (np.linalg.norm(B, axis=1) ** 2 + 1e-9)
    return (coef[:, None] * B).sum(0).astype(np.float32)
