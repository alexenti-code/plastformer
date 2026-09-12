
"""Сборка опытного образца A = (K, Φ) по плану (этапы 3-6).

Шаги:
  1. mlx_lm fuse — вшить адаптер (безопасно: по слою, полные числа, обратное сжатие)
  2. склейка частей веса в ОДИН файл
  3. создание Φ (1,50 ГБ) с ручками и бюджетами в шапке
  4. проверка: загрузка, генерация, запись-чтение Φ
"""
import os, sys, json, struct, shutil, time, subprocess
sys.path.insert(0, "/Users/alex/plastformer/plastformer")
import numpy as np
from phi import phi_create, phi_open, phi_write, phi_read, phi_resident, phi_scan, phi_knobs

R = "/Users/alex/plastformer"
CORE = f"{R}/experiments/o8-pass/gemma4-12b-text-4bit"
ADAPTER = f"{R}/experiments/o8-pass/pass-phi-v1"
FUSED = "/tmp/fused"
OUTDIR = f"{R}/models/plastformer-e1"
PHI1 = 1_300_000_000
PHI2 =   200_000_000

step = sys.argv[1] if len(sys.argv) > 1 else "all"

def sh(cmd):
    print(">>>", cmd, flush=True)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(p.stdout[-2000:]); print(p.stderr[-1000:])
    return p.returncode

# ---------------- шаг 1: слияние адаптера ----------------
if step in ("all", "fuse"):
    if os.path.exists(FUSED): shutil.rmtree(FUSED)
    rc = sh(f"cd {R} && python3 -m mlx_lm fuse --model {CORE} "
            f"--adapter-path {ADAPTER} --save-path {FUSED}")
    print("слияние rc:", rc, flush=True)
    if rc != 0: sys.exit(1)

# ---------------- шаг 2: склейка в один файл ----------------
if step in ("all", "merge"):
    os.makedirs(OUTDIR, exist_ok=True)
    parts = sorted(f for f in os.listdir(FUSED) if f.endswith(".safetensors"))
    print("частей веса:", len(parts), flush=True)
    metas = []
    for f in parts:
        p = os.path.join(FUSED, f)
        with open(p, "rb") as fh:
            n = struct.unpack("<Q", fh.read(8))[0]
            hdr = json.loads(fh.read(n))
        metas.append((p, hdr, 8 + n))
    newhdr = {}; offs = 0; order = []
    for p, hdr, body in metas:
        for k, d in hdr.items():
            if k == "__metadata__": continue
            ln = d["data_offsets"][1] - d["data_offsets"][0]
            newhdr[k] = {"dtype": d["dtype"], "shape": d["shape"],
                         "data_offsets": [offs, offs + ln]}
            if d.get("__metadata__"): newhdr[k]["__metadata__"] = d["__metadata__"]
            offs += ln; order.append((p, body + d["data_offsets"][0], ln))
    blob = json.dumps(newhdr, separators=(",", ":")).encode()
    blob += b" " * ((8 - len(blob) % 8) % 8)
    out = os.path.join(OUTDIR, "model.safetensors")
    t0 = time.time()
    with open(out, "wb") as w:
        w.write(struct.pack("<Q", len(blob))); w.write(blob)
        for p, start, ln in order:
            with open(p, "rb") as r:
                r.seek(start); left = ln
                while left:
                    ch = r.read(min(left, 64 << 20))
                    if not ch: break
                    w.write(ch); left -= len(ch)
    print(f"один файл: {os.path.getsize(out)/1e9:.2f} ГБ, тензоров {len(newhdr)}, {time.time()-t0:.1f} с", flush=True)
    for f in ("config.json","generation_config.json","tokenizer.json",
              "tokenizer_config.json","chat_template.jinja"):
        src = os.path.join(FUSED, f)
        if os.path.exists(src): shutil.copy2(src, os.path.join(OUTDIR, f))

# ---------------- шаг 3: создание Φ ----------------
if step in ("all", "phi"):
    out = os.path.join(OUTDIR, "model.safetensors")
    head = phi_create(out, PHI1, PHI2, budget_scan=6, budget_calibrate=3)
    print(f"Φ создана: файл {os.path.getsize(out)/1e9:.2f} ГБ", flush=True)
    print(f"  Φ1 {head['n1']} записей, Φ2 {head['n2']}, запись {head['rec']} байт", flush=True)
    json.dump({k: v for k, v in head.items() if not k.startswith("_")},
              open(os.path.join(OUTDIR, "phi.json"), "w"), ensure_ascii=False, indent=1)

# ---------------- шаг 4: проверка ----------------
if step in ("all", "check"):
    import mlx.core as mx
    from mlx_lm import load, generate
    out = os.path.join(OUTDIR, "model.safetensors")
    t0 = time.time()
    m, tok = load(OUTDIR)
    print(f"загрузка: {time.time()-t0:.1f} с | память {mx.get_active_memory()/1e6:.0f} МБ", flush=True)
    p = tok.apply_chat_template([{"role":"user","content":"Скажи одним предложением, кто ты."}],
                                add_generation_prompt=True)
    t0 = time.time()
    o = generate(m, tok, prompt=p, max_tokens=60, verbose=False)
    print(f"генерация: {time.time()-t0:.1f} с | пик {mx.get_peak_memory()/1e6:.0f} МБ", flush=True)
    print("ОТВЕТ:", repr(o[:200]), flush=True)
    # запись и чтение Φ
    rng = np.random.default_rng(1)
    n = phi_write(out, "phi1", rng.normal(size=1920), np.abs(rng.normal(size=5))+1,
                  valid_time=1789000000, tick=1, source="user", layer_taken=24)
    print("Φ1 запись:", n, flush=True)
    n2 = phi_write(out, "phi2", rng.normal(size=1920), np.abs(rng.normal(size=5))+2,
                   valid_time=1789000000, tick=2, source="own_derivation", layer_taken=24)
    print("Φ2 запись:", n2, flush=True)
    print("скан:", json.dumps(phi_scan(out), ensure_ascii=False)[:300], flush=True)
    res = phi_resident(out)
    print(f"постоянный префикс: {len(res)} записей", flush=True)
    # модель всё ещё грузится после записи
    m2, _ = load(OUTDIR)
    print("повторная загрузка после записи в Φ: ок", flush=True)
    print("ГОТОВО", flush=True)
