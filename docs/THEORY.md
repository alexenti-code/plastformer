# PlastFormer — Theory

**Status:** ACTIVE — mechanisms only (v4.1, disinfected 2026-09-10; background tick deferred per Fork 8; §9 state updated). (mechanisms)

**Version:** 4.0 (restructured per ADR-002; norms moved to CONSTITUTION.md v3.0)
**Status:** Draft — mechanisms description, complements CONSTITUTION.md v3.0
**Related documents:** [ADR-001](ADR-001-plastformer-transition.md) · [ADR-002](ADR-002-docs-architecture.md) · [CONSTITUTION.md](CONSTITUTION.md) · [preprint v0.5](../preprint.md) · [GLOSSARY.md](GLOSSARY.md) · [MANIFEST.md](MANIFEST.md) · Russian version: [THEORY.ru.md](THEORY.ru.md)

> Naming note (lineage): this theory circulated earlier under the working name "Matryoshka" (see MANIFEST.md lineage). The architecture is now **PlastFormer**. An earlier draft used a split-topology interface abbreviated **MMI**, later renamed **PMI**; the split topology is retired from the architecture (history, not a live component; these names are not a source of ТЗ and appear here only to prevent re-import of the retired scheme).

> What this document is: a description of mechanisms — multi-tau decay, two clocks, reconcile, background tick as core-without-input, cascade anchors, acts, and open questions. Normative statements and tests live in [CONSTITUTION.md](CONSTITUTION.md). Where this file and the preprint overlap, preprint v0.5 wording describes the formalization; where this file and CONSTITUTION overlap, CONSTITUTION governs (see ADR-002 migration table).

---

## 1. Starting description: a model that writes into its own memory

PlastFormer describes one transformer whose weights are a single file: an unchanged part K and a plastic part Φ of the same body. The model reads and writes its own Φ by its own acts. In this description:

1. **Memory write is described as an act in the model's action space**, in the same class as saying, answering, or opening a file — analogous to a person writing a note.
2. **Remembering is described as a competence of the model itself.** In an open model, the memory act rules are embedded once — by a one-time instruction pass (the act grammar) — after which the core is frozen.
3. **Granularity of a record** (a paragraph, an event, a decision, a conclusion) is described as the model's output — the record content comes from the model's stream.
4. **The write command arrives as an act in the model's output stream; the physics executes it.** The mapping of removed normative sentences to enforceable tests is recorded in ADR-002 (entries T1–T4 → CONSTITUTION C2/C4).

## 2. Experience levels: tact → episode → day → project → life

A level is described by four generalizing features, not by contents ("conversation", "project" are bindings to office life):

1. **time scale** — its own order of duration;
2. **boundaries** — the form has a beginning and an end;
3. **meaning** — the level gives meaning to what is nested in it;
4. **containment** — the level contains smaller forms and is contained in a larger one.

The minimal complete set used in this theory is five levels:

| Level | What it is | Grounding feature |
|---|---|---|
| **Tact** | live work right now: the current stream of activity | the innermost form; not closed while the model works |
| **Episode** | a bounded form with beginning and end: dialogue, task, meeting, session | boundary = completion of activity |
| **Day** | the natural cycle of existence: rhythm of work and rest | boundary = astronomical rhythm, not activity |
| **Project** | the form created by goal-setting: outlives episodes, gives them meaning | boundary = goal, not calendar |
| **Life** | the whole line of the instance; the only form without an end while the instance lives | boundary = none |

Resulting series: **tact → episode → day → project → life**.

**Why five entries.** The draft started from conversation and lost the innermost level — the present. The fifth level (tact) is the point where experience is not yet a form but live work. A sixth level ("life band", "chapter") is treated as a section of biography, not a separate store, unless it shows a separate timescale and a separate role.

**Status of the levels in v4.0.** The five levels are an *interpretation of the amplitude profile*, not containers. A fresh trace is strong in fast components — it is read as "in the tact"; hours later the fast part has faded and the middle part holds — the trace reads as "in the day"; weeks later only the slow part remains — the trace reads as "in the life". Nesting is how the physics reads, not where records are moved.

## 2.1. Organization of layers: speed, not place

**Mechanism: a layer is a speed.** Layers are decay time constants of one and the same trace. One write deposits a trace into all temporal components of the plastic part Φ at once — fast, middle, slow; the components decay continuously with different τ:

- a fresh trace: the fast component is strong — the trace reads as "in the tact";
- hours later: the fast part is gone, the middle part holds — the trace reads as "in the day";
- weeks later: only the slow part remains — the trace reads as "in the life".

"Migration" between layers is described as flow of amplitude between components of one trace, not as relocation. The second time stamp is placed at the birth of the trace (at write time); layers are further dynamics.

**The `repeat` mechanism.** Re-recording re-amplifies the components. The rest of a trace's fate is friction (continuous decay).

**Scientific anchors.** The mechanism follows cascade consolidation: Fusi, Drew & Abbott (2005), Benna & Fusi (Nature Neuroscience, 2016) — a multi-speed synapse without a selection mechanism; unlike classical CLS theory, where consolidation is driven by a separate module.

**Φ memory (parametric).** Each Φ region holds fast and slow matrices. One write deposits into both. Friction per tick multiplies by e^(−Δn/τ), τ_fast ≪ τ_slow. Reading sums the components — recent and old arrive together, and the mixture reports age to the core. Fast components free capacity by continuous decay.

## 2.2. Memory parameters: physical dials in the temperature class

A transformer already has a class of settings — continuous physics of generation and of memory writing: temperature, top_p, top_k, repetition_penalty, rope_scaling, n_ctx. Memory parameters are described as entering the same class; they are stored where physics is stored: model metadata and the Φ header.

| Parameter | Analog among existing ones | Meaning |
|---|---|---|
| forgetting_tempo | rope_scaling | multiplier of τ of all trace components; 2.0 — decays twice as fast |
| write_gain | temperature | how much trace one unit of experience leaves |
| curiosity_gain | frequency_penalty | how much prediction error amplifies the trace |
| memory_volume | n_ctx | memory capacity |
| recall_sharpness | top_k | sharpness of key-proximity sampling |
| repeat_gain | repetition_penalty (mirror) | how much `repeat` re-amplifies the trace |

### 2.2.1. Canonical memory constants (owner-approved 2026-09-06)

Six constants form the minimal regulation set for the first registered run. Start values are declared here and frozen per run in the run manifest (C3); mid-run changes are violations.

| Constant | Start value | Meaning | Analog |
|---|---|---|---|
| dormancy_rate | 0.0 | rate of the background tick in dormancy; 0 = dormancy is zero lived time (strict position, §4.3) | — |
| audibility_floor | 0.01 | amplitude threshold below which a trace is unreadable to the core; "forgotten" without a delete call | min_p |
| act_price | 1.0 tick | base price of one storing act (1 executed act = +1 tick; friction_schedule adds per-speed surcharges) | — |
| interference_factor | 1.0 (off) | readout blurring as traces accumulate in one speed component; factor stays 1.0; raised only as a stress test on long biographies | top_p (mirror) |
| consolidation_ceiling | 8.0 | cumulative amplification cap per trace: (1+repeats) ≤ ceiling; guards against a perpetual anchor from looped `repeat` | repetition_penalty (hard) |
| surfacing_cap | 12 records | N in the loudest-N physics injection (E1 range 8–16; ≤2k tokens) | top_k |

All six are content-blind: they apply to amplitudes, act types and counters, never to record text. Anything that weights by meaning is a decider, not a constant, and stays out of the main run (ablation only).

Descriptive note: temperature describes WHAT distribution text is sampled from without selecting content; forgetting_tempo is described in the same class. Enforceable boundaries for these dials (enumerated set, pre-registration, freezing) live in CONSTITUTION C3 (ADR-002 entries T5–T6).

---

## 3. Configuration

PlastFormer has one configuration: parametric × co-located × instructed. Traces are vectors in the model's own plastic Φ section, surfaced before attention — the rule for that is embedded once, after which the core is frozen.

Ownership description: the frozen core K is shared weights; the plastic Φ belongs to one instance. Personal data are described as living in Φ, inside the same body that holds the core. Instance continuity is described as preservation of the dedicated region between sessions. On a K version change, the question of Φ compatibility with the new core arises — see open questions.

## 4. Time: lived ticks, audited stamps, reconcile

Decay is described in **lived ticks** Δn (preprint §3.2, §3.5, §4):

- **Tick.** One tick = one inference step (one generation batch). The tick rate is a property of the physics and is finite. Counter mapping: 1 executed storing act = +1 tick (sparse sampling of abstract ticks); see CONSTITUTION C5 for the enforceable counter rule.
- **Decay law.** a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks; all τ_i therefore in ticks.
- **Audited time** is record-kept: bi-temporal stamps on every trace (event time + learning time). A stamp reading "two years ago" carries no felt age and has no effect on amplitude in this description.
- **Lived (felt) time** is the physics's own: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time in this description.
- **Two-clock gap as prediction error (physics):** a gap between audited stamps and the amplitude profile is described as a prediction error for the core that fires the surprise gate — the gap itself becomes an event of the biography.
- **`reconcile` (act):** read stamps, compare with felt age, deposit an explicit correction trace ("client data may be stale; confirm before acting") into a slow component. Felt time is not modified; a belief about its relation to world time is added beside it.

The acting whole at time t: **A(t) = (K, Φ(t))**. K is the frozen core; Φ(t) is the experience of this instance at tick t.

**Background tick (mechanism — DEFERRED, Fork 8).** The background tick (the core running with no user input; nothing external executes work — there is no such executor in the architecture) — described for completeness: the core running with no user input at a memory-set low rate, replaying traces and issuing `connect` acts, each recorded as a new trace. It is a deferred milestone, not a current mechanism: dormancy is zero lived time by construction, and no process outside the core executes work (DESIGN §13, Fork 8; owner decision 2026-09). A memory process linking traces by itself (no core act) is a different mechanism and belongs to ablations (CONSTITUTION C4/C7; ADR-002 entry T11).

## 5. Acts: name / repeat / connect / reconcile (+ write / read)

- **TICK is counted by the physics**, not issued by the model.
- **`name`** — fix source, time, boundaries; turns a drifting trace into an episode.
- **`repeat`** — re-amplify a trace, paying the write cost.
- **`connect`** — deposit a summary or rule into slow components as a *new* trace; sources untouched.
- **`reconcile`** — record the relation between felt time and audited time as a new trace (see §4 above).
- **Physical `write (unconscious)`** — described as: the physics writes a low-amplitude fast trace when the core's own prediction error (next-token perplexity, read from the same forward pass in the parametric co-located configuration) exceeds a frozen, content-blind threshold; nothing writes below it. The embedding-distance surrogate is an external classifier and stays forbidden in every configuration (C2; ADR-002 entry T9). Surprise traces are enabled in the main run of the parametric assembly with provenance `source=surprise` (owner decision 2026-09-07; e1-protocol v1.6).
- **Physical `read`** — surfacing from the model's own Φ section (`read last N / ids / range`): the N loudest traces by amplitude — no relevance, no embeddings. (Enforceable trigger/rank rules: CONSTITUTION C2; ADR-002 entries T7–T8.)

## 6. Bi-temporality and instance continuity (description)

Every fact recorded in Φ carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). Training weights carry no stream time; memory records carry both.

Continuity of an instance is described as following from preservation of Φ: the instance does not begin again with each session. Duplicating Φ is described plainly: the duplicate is a new instance that shares history with the original up to the moment of duplication and diverges afterwards. Dormancy is zero lived time, and waking after dormancy is a recorded event (see §4). (Copy = duplication, continuity = the Φ line: CONSTITUTION O-3/O-7; ADR-002 entries T12–T13.)

## 7. Relation to earlier review points (mechanism reading; brief)

| Review point | Mechanism description |
|---|---|
| Where write competence comes from | Remembering is described as the model's own competence; in an open model — embedded once by the instruction pass, core frozen after (§1, §5) |
| Write gates | Writing is described as the model's act; Φ only stores state (C1); decay by τ, ticks, and volume are the physics's dynamics — they happen, and nobody executes them (§5; enforceable test in CONSTITUTION C2/C4) |
| Bi-temporality in parameters | Stamps are described as a property of the memory act (§6) |
| Layers without mechanism | Layers are speeds: multi-τ decay of one trace (Fusi/Benna); five levels interpret the amplitude profile (§2–§2.1) |
| Copying | Outside the project (owner decision 2026-09-11). Identity = the memory line (§6; CONSTITUTION O-3) |
| Continuity vs. snapshots | Continuity is described as a property of the Φ line (§6; CONSTITUTION O-7) |
| Personal data / deletion | Personal data live in Φ as its own content; erasure = deletion of the Φ section (the core survives); a `connect` summary is an ordinary trace of Φ and is erased with it |

## 8. Open questions

- How to embed the memory act rules in an open model without destroying core competence; how the instruction anchors `repeat` without suppressing legitimate repetition.
- Φ portability between core versions (K replacement; re-embedding the act rules for a parametric memory).
- Which tests distinguish PlastFormer memory from ordinary storage (description-level criterion: commands arrive from the model; enforceable test in CONSTITUTION C2/C4).
- How bi-temporal stamps are represented in a parametric memory.

## 9. Honest boundary: what is built and what is not (state of 2026-09-12)

- Built as development instrumentation (not part of the artifact): a working model of the Φ physics, the write and read paths, the act grammar **v0.2.0** (owner-approved 2026-09-09; seven acts — `name`, `repeat`, `connect`, `reconcile`, `read`, `scan`, `calibrate`; layer names t1–t5).
- **BUILT (2026-09-12): the single weight file A = (K, Φ)** — `models/plastformer-e1/`, 8.20 GB, with the Instruction embedded into K by the one pass. The Φ section is read and written at run time: `plastformer/phi.py` holds the eight functions and `plastformer/loop.py` is the return loop that executes the model's acts and feeds back the `<<ENV>>` confirmation.
- **Not built:** feeding the Φ-state as the projection of a record vector onto the working-band basis (today records are fed as text from the pointer, and the lens is too noisy to build the basis); writing Φ1, which by ADR-005 is created by the physics of perception — the loop does not write it; the autonomous act trigger without prompt scaffolding (by O-8 the skill should live in the weights, while today the act skill still needs the training system prompt supplied from outside).
- Memory registers Φ1/Φ2 (ADR-005, owner-approved 2026-09-09): two provenance registers of one memory — Φ1 (involuntary layout of perception, written by physics only: surprise, gap-after-dormancy; visible in `scan`, never in the prefix) and Φ2 (personality; explicit acts only; only Φ2 enters the prefix). Φ1/Φ2 volume is unlimited; decay is the only limiter.
- There are **no results** in this document — E1 is pre-registered (see `experiments/e1-protocol.md`, version in the file header, and preprint §7).
- The September 4, 2026 bench run is a pilot of loudness-readout mechanics with calendar aging — not evidence for event time (P1).
- P2 restates the immutable past: records are append-only; a position change is a new trace; curation by omission (letting a trace decay by not repeating it) remains possible: nothing in the architecture prevents the model from letting its own traces fade.

## Composition

P1–P3 are compositional properties: every ingredient is individually known; the composition is the claim (preprint §1).

## Lineage

Primary disclosure: commit 539fc32 (2026-06-26). Source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204. Working name "Matryoshka" retained for lineage only.
