# Run Manifest — PlastFormer E1 (template)

**What this is:** the passport of one registered run (C8: every result cites its run_id).
**What this is not:** the protocol. The protocol (`e1-protocol.md`, v1.5) is one; manifests are many — one per run or per series.
**Rule (C3):** values below are frozen **before** the run. A mid-run change of any value is a violation. Nothing here reads record content.

## Identification

| Field | Value |
|---|---|
| run_id | `<series>-<nn>` (e.g. `e1-b01`) |
| date / operator | |
| repo commit hash | |
| protocol version | e1-protocol v1.5 |

## Configuration axes

| Axis | Value |
|---|---|
| substrate | symbolic / parametric |
| topology | co-located / split (PMI) |
| act state | instructed / prompted |

## Memory constants (owner-approved set, THEORY §2.2.1)

| Constant | Value for this run | Decided by / note |
|---|---|---|
| dormancy_rate | 0.0 | strict position; >0 only in dormancy ablations |
| audibility_floor | 0.01 | raise if age profile blurs; lower if dying traces are lost early |
| act_price | 1.0 tick | MUST be identical across compared arms — the honesty constant for B vs D |
| interference_factor | 1.0 (off) | stress test only: 1.0 → 1.1 → 1.25 on long biographies |
| consolidation_ceiling | 8.0 | lower if the organ loops on `repeat`; raise if R5 facts die early |
| surfacing_cap | 12 records | E1 range 8–16; ≤2k tokens injected |

## Ablations (default OFF in the main run)

| Ablation | State |
|---|---|
| RAG-style read (relevance ranking) | off |
| unconscious-surrogate | off |
| decay in wall-clock | off |
| single-τ | off |
| loudest-N auto (pre-turn push) | off |

## Judge and control

| Field | Value |
|---|---|
| judge model (not Gemma) | |
| judge blindness confirmed | yes/no + method |
| act-rate control method (identical across arms) | |
| provenance cap table (a0: user / connect / docs) | |

## Declaration (C8)

This run reports: configuration coordinates, frozen constant values, ablation states, judge and blindness method, act-rate control. What is NOT claimed until built: parametric substrate, hash-chained journal, act-ceiling numbers.
