# calibration — CAL-1: dial search & offline consolidation (pre-E1)

**Status:** DRAFT harness (protocol v0.1, agent draft 2026-09-07) — owner adjudication pending on three constitutional points (protocol.md §8). Not part of E1; results never touch the E1 corpus.

**What this is:** the pre-E1 calibration loop. It finds working values for the Φ dials (memory constants of the run manifest) by two independent procedures and compares them:

- **Phase A** — external random search over the dial space (`runner.py A`), proxy score from content-blind telemetry. No model decisions; not RSI.
- **Phase B** — offline consolidation: between episodes the core reads a content-blind `<<PMI>>` telemetry report and emits a new act `calibrate` (schema: `calibrate-schema.json`); the environment validates (validator.py: bounds, step limits, budget, frozen dials) and applies the change only to the NEXT episode (C3). The offline phase does NOT advance lived ticks (protocol.md §6 — owner adjudication pending).
- **Phase C** — A* vs B* vs default on the held-out corpus (never seen in search). Refutation criteria are pre-declared in protocol.md §7.

**Rule (C2/C7):** telemetry and the ledger oracle are content-blind and post-hoc. No module in this directory reads record `content`; oracle data never enters the model's context.

**Replay mode (current):** Phase B runs over recorded act streams (organ-dataset demonstrations) with a deterministic harness policy — a harness test of telemetry/validation/budget, NOT a model decision. A model-in-the-loop run requires its own run manifest in `manifests/`.

## Files

| File | Purpose |
|---|---|
| `protocol.md` | pre-registered calibration protocol v0.1 (corpora, score S, phases, refutation criteria, adjudication points) |
| `telemetry.py` | content-blind metrics: recall, stale_wins, window_cost, economy → proxy score S; died_too_early report; usable standalone (`--acts/--bio`) |
| `calibrate-schema.json` | the `calibrate` act contract (7th act, offline-only) |
| `validator.py` | physics bounds, per-cycle/per-run budget, frozen dials (`act_price`, `dormancy_rate` rejected unconditionally); self-test on `__main__` |
| `runner.py` | Phases A/B/C orchestration |
| `manifests/` | one manifest per search run (`cal-a-search-*.json`, `cal-b-replay-*.json`) |

## Quick start

```bash
python3 validator.py                  # self-test
python3 telemetry.py --acts ../organ-dataset/acts/bio-01.json \
                     --bio ../organ-dataset/biographies/bio-01.json
python3 runner.py A --n 24 --log manifests/cal-a-search-01.json
python3 runner.py B --cycles 5 --log manifests/cal-b-replay-01.json
python3 runner.py C --log manifests/cal-a-search-01.json
```

## First harness findings (2026-09-07, replay)

1. On a 200-exchange biography the τ multipliers are nearly inert (ticks ≪ τ): sensitivity concentrates in `surfacing_cap` and `audibility_floor`. τ sensitivity is expected on the extended 2000-exchange corpus only.
2. Proxy score S is dominated by `window_cost` under the default cap — the search immediately trades surfacing volume against recall.
3. `died_too_early` is empty on bio-01 with defaults (no over-fast decay at this horizon) — the report channel stays silent, which is the correct behavior.

## Constitution anchors

- C1/C4 — `calibrate` is a model decision; the environment only validates physics bounds, never proposes or edits.
- C2 — content-blind telemetry; amplitude/tick/layer level only.
- C3 — dials frozen before each episode; mid-episode retuning invalidates the series.
- O-10 — out-of-bounds proposals are rejected, never clamped; no silent defaults.
- O-5 — the past is never rewritten: calibration changes physics, not records.
