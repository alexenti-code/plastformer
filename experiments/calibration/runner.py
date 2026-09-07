#!/usr/bin/env python3
"""PlastFormer calibration -- runner for Phases A / B / C.

Phase A: random search over the dial space, proxy score from telemetry.
Phase B: offline-consolidation loop skeleton. The core's `calibrate` act
         is validated by validator.py and applied only to the NEXT episode
         (C3: dials fixed before a run). The stand adapter is a pluggable
         interface: the symbolic stand (prompted acts) is the reference
         implementation target; until an adapter is wired, Phase B runs in
         REPLAY mode -- the loop runs over a recorded act stream (a
         gen_acts.py demonstration), which is enough to exercise telemetry,
         validation and budget accounting end-to-end. Replay proposals are
         supplied by a deterministic policy, NOT by a model (this is a
         harness test, not a model decision; any model-in-the-loop run must
         record its run manifest, see manifests/).
Phase C: score A* / B* / default on the held-out corpus.

Pure stdlib. Deterministic. Content-blind (C2): no module here reads
record content; the ledger oracle is post-hoc only (C7).
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import telemetry as T
import validator as V

HERE = Path(__file__).parent
ORGAN = HERE.parent / "organ-dataset"


def load_pair(seed_suffix):
    acts = json.load(open(ORGAN / f"acts/bio-{seed_suffix}.json"))
    bio = json.load(open(ORGAN / f"biographies/bio-{seed_suffix}.json"))
    return acts, bio


# ---------------- Phase A ----------------

def sample_dials(rng):
    """Uniform random sample over the dial space (protocol.md section 3).
    FROZEN dials (act_price, dormancy_rate) are never sampled."""
    d = {}
    d["audibility_floor"] = round(10 ** rng.uniform(-2.7, -1.3), 5)  # ~0.002..0.05
    for layer in T.LAYERS:
        d[f"tau_multiplier.{layer}"] = round(rng.uniform(0.25, 4.0), 3)
    d["surfacing_cap"] = rng.randint(8, 16)
    d["consolidation_ceiling"] = round(rng.uniform(4.0, 16.0), 2)
    d["interference_factor"] = 1.0  # stress-test dial: off in calibration
    return d


def phase_a(corpus="01", n=24, seed=43, log=None):
    rng = random.Random(seed)
    acts, bio = load_pair(corpus)
    results = []
    for i in range(n):
        dials = sample_dials(rng)
        m = T.metrics(acts, bio, dials)
        results.append({"config": f"cal-a{i+1:02d}", "dials": dials, "S": m["S"],
                        "components": {k: m[k] for k in
                        ("recall", "stale_wins", "window_cost", "economy")}})
    results.sort(key=lambda r: -r["S"])
    if log:
        with open(log, "w") as f:
            json.dump({"phase": "A", "seed": seed, "n": n, "results": results},
                      f, ensure_ascii=False, indent=1)
    return results


def sensitivity(results):
    """Crude sensitivity map: S spread across the top/bottom tercile per dial."""
    out = {}
    by_S = sorted(results, key=lambda r: r["S"])
    for key in by_S[0]["dials"]:
        lo = sum(r["dials"][key] for r in by_S[: len(by_S) // 3]) / (len(by_S) // 3)
        hi = sum(r["dials"][key] for r in by_S[-(len(by_S) // 3):]) / (len(by_S) // 3)
        out[key] = {"mean_low_tercile": round(lo, 4), "mean_high_tercile": round(hi, 4)}
    return out


# ---------------- Phase B (replay harness) ----------------

def replay_policy(metrics_report, dials):
    """DETERMINISTIC HARNESS POLICY for replay-mode testing only.
    It is NOT the core and NOT a model decision. A real Phase B run replaces
    this with the model's `calibrate` act over the <<PMI>> report.
    Policy: if died_too_early non-empty -> lower floor x0.8 and slow the
    thinnest layer x1.3 (within validator bounds)."""
    proposal = {}
    if metrics_report.get("died_too_early"):
        proposal["audibility_floor"] = round(dials["audibility_floor"] * 0.8, 5)
    if metrics_report["metrics"]["stale_wins"] > 0:
        proposal["tau_multiplier.day"] = round(
            dials["tau_multiplier.day"] / 1.3, 4)
    return proposal or None


def phase_b(corpus="01", cycles=5, seed=None, log=None):
    """Offline-consolidation loop in replay mode. Ticks do NOT advance:
    telemetry works on the recorded act stream; consolidation is lived-time-
    free (protocol.md section 6, owner adjudication pending)."""
    acts, bio = load_pair(corpus)
    dials = dict(T.DEFAULT_DIALS)
    run_budget = 0
    history = []
    for c in range(1, cycles + 1):
        rep = T.report(acts, bio, dials)
        proposal = replay_policy(rep, dials)
        entry = {"cycle": c, "S": rep["metrics"]["S"], "dials": dict(dials),
                 "proposal": proposal}
        if proposal:
            act = {"act": "calibrate", "proposal": proposal,
                   "evidence": [{"metric": "died_too_early"}],
                   "budget_used": len(proposal)}
            ok, new_dials, errs = V.validate(act, dials, run_budget)
            entry.update({"accepted": ok, "errors": errs})
            if ok:
                dials, run_budget = V.apply(new_dials, dials, run_budget)
        else:
            entry.update({"accepted": False, "errors": ["policy: no proposal"]})
        history.append(entry)
    out = {"phase": "B-replay", "cycles": cycles, "run_budget_used": run_budget,
           "final_dials": dials, "history": history}
    if log:
        with open(log, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    return out


# ---------------- Phase C ----------------

def phase_c(heldout="02", a_star=None, b_star=None):
    """Score configurations on the held-out corpus. Means over one stream
    here (the stand has no temperature variance in replay); real Phase C
    with a live stand reports mean +- sd over 3 runs."""
    acts, bio = load_pair(heldout)
    rows = []
    for name, dials in (("default", dict(T.DEFAULT_DIALS)),
                        ("A*", a_star), ("B*", b_star)):
        if dials is None:
            continue
        m = T.metrics(acts, bio, dials)
        rows.append({"config": name, "S": round(m["S"], 4),
                     "components": {k: round(m[k], 4) for k in
                     ("recall", "stale_wins", "window_cost", "economy")}})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["A", "B", "C"])
    ap.add_argument("--corpus", default="01")
    ap.add_argument("--heldout", default="02")
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--cycles", type=int, default=5)
    ap.add_argument("--log", default=None)
    args = ap.parse_args()
    if args.phase == "A":
        res = phase_a(args.corpus, args.n, args.seed, args.log)
        print(json.dumps({"best": res[0], "sensitivity": sensitivity(res)},
                         ensure_ascii=False, indent=1))
    elif args.phase == "B":
        print(json.dumps(phase_b(args.corpus, args.cycles, log=args.log),
                         ensure_ascii=False, indent=1)[:2000])
    else:
        a = json.load(open(args.log))["results"][0] if args.log else None
        a_star = a["dials"] if a else None
        b = phase_b(args.corpus, args.cycles)
        b_star = b["final_dials"] if b["run_budget_used"] else None
        print(json.dumps(phase_c(args.heldout, a_star, b_star),
                         ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
