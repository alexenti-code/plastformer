#!/usr/bin/env python3
"""PlastFormer calibration -- validator for the `calibrate` act.

Environment side. Checks a model-emitted calibrate proposal against the
physics bounds of calibration/protocol.md v0.1 and the frozen-dial rules.
Content-blind by construction: operates on dial names and numbers only.

Constitutional anchors (CONSTITUTION v3.0):
  C1/C4 -- the proposal is a MODEL decision; the validator only enforces
           environment physics, it never proposes or edits.
  C2    -- no content reads anywhere in this module.
  C3    -- dials are fixed before the next run; nothing here mutates a
           running episode. act_price / dormancy_rate are rejected
           unconditionally (frozen: honesty constant of B vs D / strict
           dormancy position).
  O-10  -- no silent defaults: an out-of-bounds value is a REJECTION,
           never a clamp.

Pure stdlib. Deterministic.
"""

import json
from pathlib import Path

# Frozen dials (protocol.md section 3): never searchable, never applicable.
# self_improvement (calibrate budget) is also frozen for the core: the model
# cannot raise its own recursion budget (protocol.md section 3).
FROZEN = {"act_price", "dormancy_rate", "self_improvement"}

# Bounds: (min, max) absolute; plus per-cycle multiplicative step limits.
BOUNDS = {
    "audibility_floor":       (0.002, 0.05),
    "interference_factor":    (1.0, 1.25),
    "consolidation_ceiling":  (4.0, 16.0),
    "surfacing_cap":          (8, 16),
}
for layer in ("beat", "episode", "day", "project", "life"):
    BOUNDS[f"tau_multiplier.{layer}"] = (0.25, 4.0)

# Per-cycle step limits (protocol.md section 6): multiplicative bounds on
# new/old per cycle. tau-like dials: x[0.5, 2.0]; floor/ceiling/cap: x[0.5, 1.5]
# (+-50%). Separate lo/hi fixes the round-1 review bug (4.1): a single
# symmetric limit allowed ratio down to ~0 (unbounded downward step).
STEP_LIMITS = {
    "tau": (0.5, 2.0),
    "plain": (0.5, 1.5),
}

def _step_class(name):
    return "tau" if name.startswith("tau_multiplier.") else "plain"

BUDGET_PER_CYCLE = 2
BUDGET_PER_RUN = 10

ALLOWED_KEYS = set(BOUNDS) | FROZEN


def _num_ok(name, value):
    lo, hi = BOUNDS[name]
    if isinstance(lo, int) and isinstance(hi, int):
        return isinstance(value, int) and lo <= value <= hi
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return lo <= v <= hi


def _step_ok(name, old, new):
    if old in (None, 0):
        return False
    ratio = float(new) / float(old)
    lo, hi = STEP_LIMITS[_step_class(name)]
    return lo <= ratio <= hi


def validate(proposal_act, current, budget_run_used):
    """Validate one `calibrate` act.

    proposal_act     -- dict parsed from the model's JSON block
    current          -- dict of current dial values (keys = ALLOWED_KEYS minus
                        tau multiplier keys absent from the stand config)
    budget_run_used  -- int, accepted changes so far in this run

    Returns (ok: bool, new_dials: dict | None, errors: list[str]).
    On failure new_dials is None and `current` is returned unchanged in
    spirit: the caller MUST NOT apply anything. Rejections are logged by the
    caller, never silent (C-silent rule).
    """
    errors = []

    if proposal_act.get("act") != "calibrate":
        return False, None, ["act must be 'calibrate'"]

    proposal = proposal_act.get("proposal") or {}
    if not isinstance(proposal, dict) or not proposal:
        return False, None, ["proposal missing or empty"]

    # Budget: <= BUDGET_PER_CYCLE per cycle, and equals len(proposal).
    n = len(proposal)
    if n > BUDGET_PER_CYCLE:
        errors.append(f"budget: {n} changes per cycle > {BUDGET_PER_CYCLE}")
    if proposal_act.get("budget_used") != n:
        errors.append("budget_used does not match len(proposal)")
    if budget_run_used + n > BUDGET_PER_RUN:
        errors.append(
            f"budget: run budget exceeded ({budget_run_used}+{n} > {BUDGET_PER_RUN})")

    # Evidence: required, content-blind references only.
    evidence = proposal_act.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence missing or empty")

    new_dials = {}
    for name, value in proposal.items():
        if name in FROZEN:
            errors.append(f"frozen dial rejected unconditionally: {name}")
            continue
        if name not in BOUNDS:
            errors.append(f"unknown dial: {name}")
            continue
        if not _num_ok(name, value):
            errors.append(f"{name}: value {value} outside bounds {BOUNDS[name]}")
            continue
        old = current.get(name)
        if old is not None and not _step_ok(name, old, value):
            lo, hi = STEP_LIMITS[_step_class(name)]
            errors.append(f"{name}: step ratio {new_ratio(old, value)} outside [{lo}, {hi}]")
            continue
        new_dials[name] = value

    if errors:
        return False, None, errors
    return True, new_dials, []


def new_ratio(old, new):
    try:
        return float(new) / float(old)
    except (TypeError, ZeroDivisionError):
        return float("nan")


def apply(new_dials, current, budget_run_used, log_path=None):
    """Apply accepted dials to the pending-configuration (not a running
    episode -- C3). Returns the new pending config and new run budget."""
    pending = dict(current)
    pending.update(new_dials)
    used = budget_run_used + len(new_dials)
    if log_path is not None:
        entry = {"applied": new_dials, "run_budget_used": used}
        with open(log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return pending, used


if __name__ == "__main__":
    import sys
    # Self-test: frozen dial, out-of-bounds, big step, good proposal.
    cur = {"audibility_floor": 0.01, "tau_multiplier.project": 1.0,
           "surfacing_cap": 12, "consolidation_ceiling": 8.0,
           "interference_factor": 1.0}
    tests = [
        ({"act": "calibrate", "proposal": {"act_price": 0.5}, "evidence": [{"metric": "died_too_early"}], "budget_used": 1}, cur, 0, False),
        ({"act": "calibrate", "proposal": {"audibility_floor": 0.9}, "evidence": [{"metric": "died_too_early"}], "budget_used": 1}, cur, 0, False),
        ({"act": "calibrate", "proposal": {"audibility_floor": 0.05}, "evidence": [{"metric": "wasted_surface"}], "budget_used": 1}, cur, 0, False),  # step x5 > x1.5
        ({"act": "calibrate", "proposal": {"audibility_floor": 0.0025}, "evidence": [{"metric": "wasted_surface"}], "budget_used": 1}, cur, 0, False),  # step x0.25 < x0.5 (round-1 bug)
        ({"act": "calibrate", "proposal": {"tau_multiplier.project": 0.3}, "evidence": [{"metric": "stale_win"}], "budget_used": 1}, cur, 0, False),  # tau step x0.3 < x0.5
        ({"act": "calibrate", "proposal": {"tau_multiplier.project": 1.8}, "evidence": [{"metric": "died_too_early"}], "budget_used": 1}, cur, 0, True),  # tau step x1.8 <= x2.0
        ({"act": "calibrate", "proposal": {"self_improvement": 20}, "evidence": [{"metric": "loop_repeat"}], "budget_used": 1}, cur, 0, False),  # frozen recursion budget
        ({"act": "calibrate", "proposal": {"audibility_floor": 0.008, "tau_multiplier.project": 0.7}, "evidence": [{"metric": "died_too_early", "record_id": 88}, {"metric": "stale_win", "record_id": 12}], "budget_used": 2}, cur, 0, True),
    ]
    for i, (act, c, b, expect) in enumerate(tests):
        ok, nd, errs = validate(act, c, b)
        status = "OK " if ok == expect else "FAIL"
        print(f"[{status}] test {i}: ok={ok} dials={nd} errs={errs}")
        if ok != expect:
            sys.exit(1)
    print("validator self-test passed")
