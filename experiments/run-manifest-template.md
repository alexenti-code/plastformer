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

## Configuration (fixed: parametric × co-located × instructed)

| Component | Value |
|---|---|
| substrate | parametric (vector bank, embedded read interface) |
| topology | co-located |
| act state | instructed (act grammar embedded once) |

## Memory constants (owner-approved set, THEORY §2.2.1)

| Constant | Value for this run | Decided by / note |
|---|---|---|
(dormancy_rate removed 09.09.2026: in the parametric assembly dormancy = zero ticks BY CONSTRUCTION — the bank is not running, nobody executes background work; a background tick would be an executable job with no executor. Wake-up is recorded by the gap-trace, already enabled.)
| audibility_floor | 0.01 | raise if age profile blurs; lower if dying traces are lost early |
| act_price | 1.0 tick | MUST be identical across compared arms — the honesty constant for B vs D |
| interference_factor | 1.0 (off) | stress test only: 1.0 → 1.1 → 1.25 on long biographies |
| consolidation_ceiling | 8.0 | lower if the organ loops on `repeat`; raise if R5 facts die early |
| surfacing_cap | 12 records | E1 range 8–16; ≤2k tokens injected |
| prefix_depth | =surfacing_cap (provisional) | size of the resident prefix; may differ from N |
| residency_horizon | (provisional) | how many recent prefix changes stay visible as history |
| rebuild_period | 1 (provisional) | prefix rebuild frequency, in ticks |
| gap_threshold | (provisional) | tick gap firing the dormancy gap-trace |
| surprise_threshold | (provisional) | perplexity threshold for surprise traces |

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

## Instruction pass (O-8) record

| Field | Value |
|---|---|
| grammar version | act-grammar v0.1.2 |
| pass structure | mixed distribution: grammar (verbatim + dry calibration pairs) + self-distillation anchor on frozen core outputs |
| mixture proportion | grammar % / anchor % |
| LoRA rank / lr / seed | |
| material checksum | |

## Post-pass battery (embedding tax, Limitation 10)

| Check | Result | Ceiling |
|---|---|---|
| grammar verbatim reproduction | | ≥ 95% |
| valid act-schema form | | ≥ 95% |
| MMLU-mini / GSM8K-mini / IFEval-mini avg delta vs base | | ≤ −2 pts |
| perplexity drift on held-out general texts | | ≤ +3% |
| genre-diversity probe vs base (blind) | | no genre below base |
| outcome | accepted / re-run (rank, mixture) | |

## Declaration (C8)

This run reports: configuration coordinates, frozen constant values, ablation states, judge and blindness method, act-rate control, instruction-pass record and post-pass battery. What is NOT claimed until built: parametric substrate, hash-chained journal, act-ceiling numbers.
