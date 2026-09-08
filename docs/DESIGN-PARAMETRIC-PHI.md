# Design: Parametric Phi — Variant B (trace bank + MAC interface)

**Status:** ENGINEERING DESIGN (owner review pending) — 07.09.2026
**Decision context:** E1 arm D needs a parametric substrate. Two candidates analyzed:
(A) rank-1 weight updates in a Titans-style memory block; (B) trace bank + learned
write/read interfaces at the MAC position. **Variant B selected** for E1 and the paper.

## 1. What variant B is

Phi = co-located trace bank. Each trace:

```
trace = {
  content:      verbatim text (hard facts, Sec 3.7) + content_vector (d_model=3840),
  provenance:   source class (user | own_derivation | tool_result),
                bi-temporal stamps (valid_time, record_tick),
  amplitude:    vector [a_1..a_k] over k decay speeds (tau components, THEORY),
  state:        act type (name | repeat | connect | reconcile), actor=K
}
```

Substrate physics (properties of the artifact; nobody executes them):
- decay `a_i(n) = a_i(0) * exp(-dn / tau_i)` (ticks, never wall-clock)
- tick counter by the substrate; act_price 1.0 tick; audibility_floor 0.01
- surfacing_cap 12 records (<= 2k tokens) per read
- surprise traces: low-amplitude writes gated by the core's own prediction error
  (next-token perplexity, frozen content-blind threshold, provenance source=surprise)
- gap-trace: substrate writes a low-amplitude event trace when the tick gap since the
  last act exceeds a frozen threshold (dormancy event, visible via the resident prefix)

Two learned interfaces, both embedded by the single instruction pass (O-8), then frozen:
- write interface: model act (JSON in its own output) -> content_vector + amplitude -> bank
- read interface: loudest-N vectors by amplitude -> hidden space, inserted BEFORE attention
  at the MAC position

Trunk (all 48 layers of Gemma4-12B) unchanged after the grammar pass.
Skill = act grammar v0.1.1 embedded in the trunk (one pass, frozen).
Memory content = the bank, written only by the model's own acts (C4).

## 2. Why not variant A (rank-1 weight writes, Titans-style)

A is the literature reference for "memory in weights" — the comparison is required
for the paper, not for us. A stores traces AS weight updates; B stores traces AS
addressable records. Against our canon A breaks two of four requirements:

| Requirement | A | B |
|---|---|---|
| multi-tau cascade (Fusi/Benna) | broken: weights decay at one rate; keeping per-trace tau = factorized bank (= B with extra math) | native: amplitude is an explicit vector |
| verbatim hard facts (Sec 3.7) | not guaranteed: vector compression distorts; fails MRCR/RULER needles | native: verbatim text stored alongside vector |
| bi-temporal stamps | nowhere to put (open question, THEORY Sec 8) | explicit field |
| audit / E4 export | opaque | row-by-row export |

Titans writes everything through a surprise gate (unconscious register, our Sec 3.3
"physics"). B implements BOTH registers: the conscious one (only explicit acts write
content, C4) and the physical one (surprise traces from the core's own perplexity and
gap-traces on dormancy — gated by the core's internal signal, enabled in the main run
per e1-protocol v1.6; the embedding-distance surrogate remains forbidden everywhere, C2).
Honest framing: "Titans = unconscious-only writes + MAC; PlastFormer = conscious acts
+ internal-signal physics + MAC."
THEORY Sec 9 already marks rank-1 writes as future work; A remains a post-publication
research branch.

## 3. Why this is not RAG with vectors (registered arguments)

1. **Who decides what to read.** RAG: an external system ranks chunks by query
   relevance; the model is passive. B: the model itself emits the `read` act
   (last N / ids / from-to) in its own output (C1).
2. **How surfaced material is selected.** RAG: similarity(query, chunk),
   content-dependent. B: content-blind loudest-N by amplitude — no relevance, no
   embeddings, no keyword match, no query dependence (C2; e1-protocol). The trunk
   selects relevance AFTER insertion, with its own attention.
3. **Between reads.** RAG: static store. B: live physics — decay per tick,
   dormancy = zero lived time, act_price; the substrate is never static.
4. **Writes.** RAG: an external indexer writes. B: only the model's own acts write (C4),
   with its own trust-class and layer judgments.
5. **What is stored.** RAG: document chunks, model-independent. B: instance biography —
   provenance, two clocks, amplitude profile, refs; exportable artifact (E4).
6. **RAG-style read is a registered ablation** in e1-protocol ("relevance ranker =
   external decision-maker, axiom-2 violation, survives only as control ablation").
   The comparison is pre-registered, not improvised.

## 4. MAC position (Memory as Context, Titans arXiv:2501.00663 Sec 4.1)

Retrieved memory enters as a PREFIX of the sequence, in hidden space, before attention:

```
h_t   = M*_{t-1}(q_t)               # retrieve (Titans: similarity query)
St~_t = [p_1..p_Np] || h_t || S_t   # persistent || memory || current segment
y_t   = Attn(St~_t)
```

Why before attention: biography enters the attention field together with the input;
attention decides what matters now. Post-attention insertion could not steer perception.
Write late (post-step, mature representation), read early (pre-attention).

Differences from Titans-MAC (stated honestly in the paper):
- Titans retrieval is similarity-based (content-dependent); ours is amplitude-based
  (content-blind, C2). We deliberately take the dumber selector: the trunk does the
  intelligent work with its own attention.
- Titans' M trains by gradient at test time; our bank is written only by acts,
  trunk frozen.
- Insertion position is the same; we take the MAC mechanics, not the neural-memory
  mechanics.

## 5. Speed and resources (M1 Pro 16 GB, Gemma4-12B qat-4bit)

Model: d_model 3840, 48 layers, head_dim 256, 16 heads (8 KV).

Bank size (bf16 content vectors):
  1k traces ~ 8 MB | 10k ~ 77 MB | 100k ~ 768 MB | 1M ~ 7.7 GB (fits, at the limit)

Per-turn cost:
- amplitude sort: O(N log N), microseconds at 100k
- project 12 vectors: 12 x 3840^2 ~ 0.18 GFLOP — milliseconds on Metal
- MAC prefix insertion: concatenation — free
- attention over +12 positions: ~+0.3% per turn
- decay tick over 100k traces: vectorized, milliseconds

Total memory overhead < 1% of a turn; generation (~12 tok/s) remains the bottleneck.
The 200-message scenario (~2-3 h) is unaffected.

## 6. Honest caveats

- Cost figures in §5 are LATENCY overhead (wall-clock per turn), not quality tax.
  The quality effect of the 12-position prefix and injected vectors on answer quality
  (the "embedding tax") is NOT covered by §5 and is measured only by the E1 battery
  (secondary metrics) and pre/post core benchmarks; no claim better than "to be measured".
- Read-decoding is a REGISTERED GATE (E1 v1.7 PR0): the untrained read side cannot
  decode trace content (gap A, diagnostics 08.09); the whole comparison assumes a
  trained projector G and is blocked until the smoke test passes.
- Not "memory in weights" literally: traces in the bank, interfaces in weights.
  Paper framing: frozen core + addressable plastic substrate; interfaces embedded once.
- The difference from RAG is governance (who decides), not access mechanics; both
  stated explicitly.
- Same insertion position as Titans-MAC; different selection and write register.

## 7. Build plan (5 modules, MLX)

1. Phi bank (mx.array + metadata): append, decay(tick), loudest-N, floor filter,
   export/import (E4), zeroing.
2. Write interface (projector d x d + small MLP): act JSON -> vector + amplitude.
3. Read interface (projector d x d): trace vectors -> hidden space; MAC-prefix
   insertion before attention (custom forward).
4. Grammar pass: act-grammar v0.1.1 embedded in the trunk (one LoRA pass, frozen).
5. Harness: substrate, ticks, act acknowledgements, judge channel.

## 8. Residency of the surfaced set (decided: V3, owner-approved 07.09.2026)

**Decision principle:** chosen by the project's intent (give the transformer memory and
awareness of its own history), not by cost. Cheapness is explicitly not a criterion.

**V3 = resident prefix + read acts on top.** Two registers of memory:

1. **Resident prefix (background self-knowledge).** The surfaced set (loudest-N by
   amplitude, N <= surfacing_cap) stays resident as the MAC prefix across turns.
   It updates when the substrate physics changes the loudness profile materially:
   a trace enters the top-N, dies below the audibility floor, or the ordering shifts.
   Constant prefix -> the biography is part of the model's standing self-view.
2. **Read acts (deliberate recollection).** The model's own `read` act
   (ids / from-to) extends or re-selects the resident set for the turn.

**Why this serves the intent (owner's argument, adopted):**
- A per-turn flash (V1) makes memory a repeated hint, not lived history: the model
  cannot build cross-turn reasoning over its own biography. Rejected as contrary
  to the intent.
- A resident prefix makes biography part of the "I": stable background knowledge,
  cross-turn reasoning becomes possible.
- **Change of the prefix is a visible event.** A trace entering/leaving the resident
  set is perceived by the model as a delta of its own biography — the horizon of
  events. This matches THEORY Sec 4: the gap between audited stamps and the amplitude
  profile becomes an event of the biography (surprise gate). V1 has no delta — nothing
  can be an event.
- Two registers mirror human memory: background knowing (physics) + deliberate
  recollection (act). Together they implement the state-form of memory (the project's
  "state vs archive" thesis): a stable offset, not a bimodal retrieval.

**Constitutional position (re-checked, unchanged):** what is surfaced — substrate
physics (C2, content-blind); what the model does with it — its own attention (C1);
writes — only explicit acts (C4). The resident prefix adds no external semantic
decision-maker: updates are amplitude physics, not content analysis.

**Honest risks (experiment will show, registered loci):**
- attention habituation to a constant prefix; mitigated by the prefix actually
  changing on events, and by N <= surfacing_cap;
- stale-trace conservation amplified by residency; measured by the registered
  locus "suppression of stale material".

KV-cache cost of the resident prefix (+N positions) is acknowledged and accepted
as non-decisive.

## 9. Tau set (owner-approved 2026-09-07): k = 5

| Component | tau (ticks) | Horizon |
|---|---|---|
| tau_1 | 15 | in-tact (turn intonation) |
| tau_2 | 80 | episode (~session) |
| tau_3 | 400 | day-week of the project |
| tau_4 | 2000 | whole project |
| tau_5 | 10000 | identity ("forever") |

Geometric progression x5; at 200 ticks (E1): tau_1 dead, tau_2 ~8%, tau_3 ~61%,
tau_4 ~90%, tau_5 ~98% — the expected survival profile of a session biography.
One write deposits across all five (O-10); the registered Arm D uses k=5.
Note: these figures were approved in the architecture discussion of 2026-09-07;
they are dials (C3) and must be frozen in the run manifest before the first run.

## 11. Show dials (owner decision 08.09.2026, Fork 7 closed)

Resident prefix: ALL changes are shown to the model — the substrate hides nothing and
decides nothing about significance. Distinguishing "is this an event" is a semantic act
of the core. The environment owns only show-dials (content-blind boundaries, frozen per
manifest, tuned in the experiment):

| Dial | Meaning |
|---|---|
| surfacing_cap (N) | top-N traces by amplitude shown as the prefix |
| prefix_depth | how many traces the resident prefix carries (can differ from N) |
| residency_horizon | how many recent prefix changes remain visible as history |
| rebuild_period | how often the substrate rebuilds the top-N (1 = every turn) |
| gap_threshold | tick gap that fires the dormancy gap-trace |
| surprise_threshold | perplexity threshold for surprise traces |

Design-stage dial set is provisional: the model plus telemetry find the optimal values
and the final dial composition. HARD RULE: a dial must never become an external decider
of what the model does with its own memory — dials bound what is SHOWN, never what it MEANS.
Any dial that would filter, rank, or threshold by meaning is an external decider (C2) and
is forbidden (owner decision, Fork 7: no "significant change" thresholds).

## 12. Embedding coverage: assembly space, alpha first (owner decision 08.09.2026, Fork 6 closed)

The instruction-pass coverage is NOT a one-time irreversible choice. O-8 freezes the core
within one instance's life; it does not forbid multiple instances assembled from the same
base checkpoint by different mechanisms. Each assembly is a separate artifact (O-3: a copy
made by a different pass is a new instance that diverges from the point of assembly).

- **Assembly alpha (first):** embedding into ALL target modules — MLP + q,v across all
  layers (k,o untouched so the weighing mechanics stay exactly baseline; the B-vs-D delta
  must come from skill + Phi, not from a shifted attention). Maximum skill capacity,
  maximum competence surface touched.
- **Assembly beta (contingency):** narrow embedding (upper-layer MLPs only). Minimum tax,
  risk of under-embedding. Built ONLY if alpha shows degradation: "если тупит и потеря
  себя — собираем абсолютно новую бетту" (owner). Built from the ORIGINAL base checkpoint,
  never as a second pass over alpha (second pass over a frozen core is not O-8).
- Both assemblies pass the same post-pass battery (grammar >=95%, act form >=95%,
  competence <=-2 pts, perplexity <=+3%, genre probe). The battery comparison yields an
  empirical curve "embedding coverage <-> tax" — paper material.
- Switching between assemblies in a live instance is impossible (second pass over a live
  frozen core violates O-8); switching between ARTIFACTS by the deployer is always available
  (download another assembly; the base checkpoint is free, the pass takes hours).

Preprint line (registered): the choice of embedding coverage is a per-deployment
computation; the protocol admits several assemblies of one base core; an assembly is an
instance (O-3); the choice between assemblies belongs to the deployer.

## 13. Dormancy = zero ticks by construction (owner decision 09.09.2026, Fork 8 closed)

In the parametric assembly (trace bank + interfaces) dormancy is not a configuration
choice: the bank is a passive array; no instance running means no ticks, no decay
(delta-n is measured in ticks, which do not advance), no replays. A "background tick"
would be executable work with no executor — the exact thing the architecture removed
("decay/ticks/volumes are substrate dynamics nobody executes"). Wake-up is recorded by
the gap-trace (enabled). The dormancy_rate dial is removed from the manifest template.
