"""Phi bank — trace vectors + tau amplitudes. DESIGN-PARAMETRIC-PHI §7.1.

State: one mx.array of trace vectors [N, d] (fp16) + one [N, k] amplitude table
(fp32, k=5 tau components) + JSONL metadata. The budget of section Phi (0.5 GB)
bounds the bank: max_traces = 0.5e9 / (d*2 + k*4) bytes.

Physics (C5, THEORY 2.2.1): decay is lazy — amplitudes are stored at write with
last_tick; the live amplitude is amp_i(tick) = amp_write_i * exp(-(tick - last_tick)/tau_i).
Read = loudest-N by total amplitude (sum over components), floor-filtered, content-blind (C2).
"""
import json, math, os
import numpy as np
import mlx.core as mx

TAUS = [15.0, 80.0, 400.0, 2000.0, 10000.0]
FLOOR = 0.01
DEPOSIT = [1.0, 0.8, 0.5, 0.25, 0.1]        # O-10: one write deposits across all five
LOUDNESS = {"note": 0.5, "record": 1.0, "anchor": 1.5}
CAPS = {"user": 1.0, "tool_result": 0.8, "own_derivation": 0.6}
LAYER_BOOST = 1.6                            # asserted layer emphasis (tau_multiplier.t_i)

class PhiBank:
    def __init__(self, d: int, max_bytes: int = 500_000_000, path: str = None):
        self.d = d
        per_trace = d * 2 + len(TAUS) * 4
        self.max_traces = max_bytes // per_trace
        self.vecs = np.zeros((0, d), dtype=np.float16)      # bank on CPU; read path moves to mx
        self.amps = np.zeros((0, len(TAUS)), dtype=np.float32)
        self.meta = []                                       # list of dicts
        self.tick = 0
        self.path = path

    # ---------- write ----------
    def deposit_amplitudes(self, source: str, loudness: str, layer: str):
        cap = CAPS.get(source, CAPS["own_derivation"])
        mult = LOUDNESS.get(loudness, LOUDNESS["record"])
        idx = {"t1":0,"t2":1,"t3":2,"t4":3,"t5":4}.get(layer, 2)
        amps = [min(base * mult, cap) for base in DEPOSIT]
        amps[idx] = min(amps[idx] * LAYER_BOOST, cap * LAYER_BOOST)
        return amps

    def append(self, vec, source, loudness, layer, meta):
        assert vec.shape == (self.d,)
        if len(self.meta) >= self.max_traces:
            # evict quietest (floor physics, never semantic — C2)
            totals = self._live_totals()
            victim = int(np.argmin(totals))
            self._drop(victim)
        amps = self.deposit_amplitudes(source, loudness, layer)
        self.vecs = np.vstack([self.vecs, vec.astype(np.float16)])
        self.amps = np.vstack([self.amps, np.array(amps, dtype=np.float32)])
        self.meta.append({"tick": self.tick, "last_tick": self.tick,
                          "repeats": 0, **meta})
        return len(self.meta)  # id = 1-based

    def touch(self, tid: int):
        """repeat act: re-amplify (C2-safe: fixed factor, physics only)."""
        m = self.meta[tid - 1]
        m["repeats"] += 1
        m["last_tick"] = self.tick
        # written amplitudes rise toward the cap; fixed gain per repeat
        g = 1.3
        self.amps[tid - 1] = np.minimum(self.amps[tid - 1] * g, 1.6)

    # ---------- read (content-blind, C2) ----------
    def _live_totals(self) -> np.ndarray:
        if not len(self.meta): return np.zeros(0)
        dn = np.array([self.tick - m["last_tick"] for m in self.meta], dtype=np.float32)
        decay = np.exp(-dn[None, :] / np.array(TAUS, dtype=np.float32)[:, None])  # [k, N]
        return (self.amps.T * decay).sum(axis=0)                                  # [N]

    def loudest(self, n: int):
        totals = self._live_totals()
        alive = np.where(totals >= FLOOR)[0]
        order = alive[np.argsort(-totals[alive])][:n]
        return [(int(i) + 1, float(totals[i])) for i in order]

    def prefix_vectors(self, n: int) -> "mx.array":
        """[n, d] mx.array of live trace vectors for the resident prefix."""
        picks = self.loudest(n)
        if not picks: return None
        ids = [i - 1 for i, _ in picks]
        totals = np.array([t for _, t in picks], dtype=np.float32)
        v = self.vecs[ids].astype(np.float32) * totals[:, None]
        return mx.array(v).astype(mx.bfloat16)

    # ---------- lifecycle ----------
    def _drop(self, i: int):
        self.vecs = np.delete(self.vecs, i, axis=0)
        self.amps = np.delete(self.amps, i, axis=0)
        self.meta.pop(i)

    def zero(self):
        self.vecs = np.zeros((0, self.d), dtype=np.float16)
        self.amps = np.zeros((0, len(TAUS)), dtype=np.float32)
        self.meta = []

    def export(self, path: str):
        os.makedirs(path, exist_ok=True)
        np.save(os.path.join(path, "vectors.npy"), self.vecs)
        np.save(os.path.join(path, "amplitudes.npy"), self.amps)
        with open(os.path.join(path, "meta.jsonl"), "w") as f:
            for m in self.meta: f.write(json.dumps(m, ensure_ascii=False) + "\n")
            f.write(json.dumps({"tick": self.tick}) + "\n")

    def import_(self, path: str):
        self.vecs = np.load(os.path.join(path, "vectors.npy"))
        self.amps = np.load(os.path.join(path, "amplitudes.npy"))
        self.meta = []
        with open(os.path.join(path, "meta.jsonl")) as f:
            for line in f:
                m = json.loads(line)
                if "tick" in m and "content" not in m: self.tick = m["tick"]
                else: self.meta.append(m)
        return len(self.meta)
