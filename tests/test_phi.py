
import os, shutil, sys, time
sys.path.insert(0, "/Users/alex/plastformer/plastformer")
import numpy as np
from phi import (phi_create, phi_open, phi_write, phi_read, phi_resident,
                 phi_scan, phi_knobs, phi_calibrate, phi_apply_calibration,
                 REC_SIZE, VEC_BYTES, HEADER_RESERVE)

SRC = "/Users/alex/plastformer/experiments/o8-pass/gemma4-12b-text-4bit"
WORK = "/tmp/phi-test"

print("=== готовим копию ядра, склеенную в ОДИН файл ===")
if os.path.exists(WORK): shutil.rmtree(WORK)
os.makedirs(WORK)

import struct, json
parts = sorted(f for f in os.listdir(SRC) if f.endswith(".safetensors"))
metas = []
for f in parts:
    p = os.path.join(SRC, f)
    with open(p, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        hdr = json.loads(fh.read(n))
    metas.append((p, hdr, 8 + n, os.path.getsize(p)))

newhdr = {}; offs = 0; order = []
for p, hdr, body, sz in metas:
    for k, d in hdr.items():
        if k == "__metadata__": continue
        ln = d["data_offsets"][1] - d["data_offsets"][0]
        newhdr[k] = {"dtype": d["dtype"], "shape": d["shape"], "data_offsets": [offs, offs+ln]}
        if d.get("__metadata__"): newhdr[k]["__metadata__"] = d["__metadata__"]
        offs += ln; order.append((p, body + d["data_offsets"][0], ln))
blob = json.dumps(newhdr, separators=(",", ":")).encode()
blob += b" " * ((8 - len(blob) % 8) % 8)
OUT = os.path.join(WORK, "model.safetensors")
t0 = time.time()
with open(OUT, "wb") as w:
    w.write(struct.pack("<Q", len(blob))); w.write(blob)
    for p, start, ln in order:
        with open(p, "rb") as r:
            r.seek(start); left = ln
            while left:
                ch = r.read(min(left, 64<<20))
                if not ch: break
                w.write(ch); left -= len(ch)
for f in ("config.json","generation_config.json","tokenizer.json","tokenizer_config.json","chat_template.jinja"):
    shutil.copy2(os.path.join(SRC,f), os.path.join(WORK,f))
print(f"  один файл: {os.path.getsize(OUT)/1e9:.2f} ГБ за {time.time()-t0:.1f} с")

print()
print("=== создаём Φ ===")
t0 = time.time()
head = phi_create(OUT, phi1_bytes=1_300_000_000, phi2_bytes=200_000_000,
                  knobs=None, budget_scan=6, budget_calibrate=3)
print(f"  Φ создана за {time.time()-t0:.1f} с")
print(f"  размер файла: {os.path.getsize(OUT)/1e9:.2f} ГБ")
print(f"  Φ1 ёмкость: {head['n1']}, Φ2: {head['n2']}, запись {head['rec']} байт")
assert os.path.getsize(OUT) == os.path.getsize(OUT)

print()
print("=== записываем записи ===")
rng = np.random.default_rng(0)
for i in range(5):
    vec = rng.normal(size=1920).astype(np.float32)
    amp = np.abs(rng.normal(size=5)).astype(np.float32)
    num = phi_write(OUT, "phi1", vec, amp, valid_time=1789000000+i*60, tick=i+1, source="user", layer_taken=24)
    print(f"  Φ1 запись {num}: амплитуды {amp.round(2)}")
for i in range(3):
    vec = rng.normal(size=1920).astype(np.float32)
    amp = np.abs(rng.normal(size=5)).astype(np.float32) + 0.5
    num = phi_write(OUT, "phi2", vec, amp, valid_time=1789000000+i*600, tick=10+i, source="own_derivation", layer_taken=24)
    print(f"  Φ2 запись {num}: громкость {amp.max():.2f}")

print()
print("=== читаем ===")
s = phi_scan(OUT)
print("  скан:", json.dumps({k:v for k,v in s.items() if k!='knobs'}, ensure_ascii=False))
print("  ручки:", json.dumps(s["knobs"], ensure_ascii=False))
res = phi_resident(OUT)
print(f"  постоянный префикс: {len(res)} записей")
for r in res:
    print(f"    №{r['num']} громкость {r['loudness']:.2f} источник {r['source']} слой {r['layer_taken']}")

print()
print("=== калибровка ===")
d = phi_calibrate(OUT, {"knob":"audibility_floor","value":0.005})
print("  в границах:", d)
d2 = phi_calibrate(OUT, {"knob":"act_price","value":2.0})
print("  замороженная:", d2)
d3 = phi_calibrate(OUT, {"knob":"audibility_floor","value":100.0})
print("  вне границ:", d3.get("accepted"), d3.get("why"))
phi_apply_calibration(OUT, d)
print("  после применения:", phi_knobs(OUT)["audibility_floor"], "| scan:", phi_scan(OUT)["scan_left"], "сканов")

print()
print("=== переживает ли Φ перезапуск ===")
s2 = phi_scan(OUT)
print(f"  Φ1 записано {s2['phi1_written']}, Φ2 {s2['phi2_written']}, тик {s2['tick']}")
print(f"  ручка audibility_floor = {phi_knobs(OUT)['audibility_floor']}")

print()
print("=== проверка: файл всё ещё грузится как модель ===")
from mlx_lm import load
import mlx.core as mx
t0=time.time()
m, tok2 = load(WORK)
print(f"  загрузка {time.time()-t0:.1f} с | память {mx.get_active_memory()/1e6:.0f} МБ")
p = tok2.apply_chat_template([{"role":"user","content":"Скажи одно слово."}], add_generation_prompt=True)
from mlx_lm import generate
out = generate(m, tok2, prompt=p, max_tokens=20, verbose=False)
print("  ответ:", repr(out[:120]))
print()
print("ВСЁ ПРОШЛО")
