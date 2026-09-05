# PlastFormer — Theory (mechanisms)

**Version:** 4.0 (restructured per ADR-002; norms moved to CONSTITUTION.md v1.0)
**Status:** Draft — mechanisms description, complements CONSTITUTION.md v1.0
**Related documents:** [ADR-001](ADR-001-plastformer-transition.md) · [ADR-002](ADR-002-docs-architecture.md) · [CONSTITUTION.md](CONSTITUTION.md) · [preprint v0.5](../preprint.md) · [GLOSSARY.md](GLOSSARY.md) · [MANIFEST.md](MANIFEST.md) · Russian version: [THEORY.ru.md](THEORY.ru.md)

> Naming note (lineage): this theory circulated earlier under the working name "Matryoshka" (see MANIFEST.md lineage). The architecture is now **PlastFormer**; the interface formerly abbreviated **MMI** is now **PMI (Plastic Memory Interface)**.

> What this document is: a description of mechanisms — multi-tau decay, two clocks, reconcile, background tick as core-without-input, cascade anchors, acts, and open questions. Normative statements and tests live in [CONSTITUTION.md](CONSTITUTION.md). Where this file and the preprint overlap, preprint v0.5 wording describes the formalization; where this file and CONSTITUTION overlap, CONSTITUTION governs (see ADR-002 migration table).

---

## 1. Starting description: model coupled to its own memory substrate

PlastFormer describes a transformer with an unchanged core K and a plastic module Φ, connected by the architectural coupling PMI. In this description:

1. **Memory write is described as an act in the model's action space**, in the same class as saying, answering, or opening a file — analogous to a person writing a note.
2. **Remembering is described as a trainable competence.** In an open model, PMI functions are trained once, after which the core is frozen. On the current stand the acts are given by prompt — a rehearsal of the organ, not the organ.
3. **Granularity of a record** (a paragraph, an event, a decision, a conclusion) is described as the model's output — the record content comes from the model's stream.
4. **On the stand**, the write command arrives as a tool call in the model's output stream; the stand executes it. The mapping of removed normative sentences to enforceable tests is recorded in ADR-002 (entries T1–T4 → CONSTITUTION P2/P5).

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

**Status of the levels in v4.0.** The five levels are an *interpretation of the amplitude profile*, not containers. A fresh trace is strong in fast components — it is read as "in the tact"; hours later the fast part has faded and the middle part holds — the trace reads as "in the day"; weeks later only the slow part remains — the trace reads as "in the life". Nesting is how the substrate reads, not where records are moved.

## 2.1. Organization of layers: speed, not place

**Mechanism: a layer is a speed.** Layers are decay time constants of one and the same trace. One write deposits a trace into all temporal components of the plastic substrate at once — fast, middle, slow; the components decay continuously with different τ:

- a fresh trace: the fast component is strong — the trace reads as "in the tact";
- hours later: the fast part is gone, the middle part holds — the trace reads as "in the day";
- weeks later: only the slow part remains — the trace reads as "in the life".

"Migration" between layers is described as flow of amplitude between components of one trace, not as relocation. The second time stamp is placed at the birth of the trace (at write time); layers are further dynamics.

**The `repeat` mechanism.** Re-recording re-amplifies the components (on the stand, a repeated trace returns with doubled signal). The rest of a trace's fate is friction (continuous decay).

**Scientific anchors.** The mechanism follows cascade consolidation: Fusi, Drew & Abbott (2005), Benna & Fusi (Nature Neuroscience, 2016) — a multi-speed synapse without a selection mechanism; unlike classical CLS theory, where consolidation is driven by a separate module.

**Stand description (research scope).** Each Φ region holds fast and slow matrices. One write deposits into both. Friction per tick multiplies by e^(−Δn/τ), τ_fast ≪ τ_slow. Reading sums the components — recent and old arrive together, and the mixture reports age to the core. Fast components free capacity by continuous decay.

## 2.2. Memory parameters: physical dials in the temperature class

A transformer already has a class of settings — continuous physics of generation and substrate: temperature, top_p, top_k, repetition_penalty, rope_scaling, n_ctx. Memory parameters are described as entering the same class; they are stored where physics is stored: model metadata and substrate header.

| Parameter | Analog among existing ones | Meaning |
|---|---|---|
| forgetting_tempo | rope_scaling | multiplier of τ of all trace components; 2.0 — decays twice as fast |
| write_gain | temperature | how much trace one unit of experience leaves |
| curiosity_gain | frequency_penalty | how much prediction error amplifies the trace |
| memory_volume | n_ctx | substrate capacity |
| recall_sharpness | top_k | sharpness of key-proximity sampling |
| repeat_gain | repetition_penalty (mirror) | how much `repeat` re-amplifies the trace |

Descriptive note: temperature describes WHAT distribution text is sampled from without selecting content; forgetting_tempo is described in the same class. Enforceable boundaries for these dials (enumerated set, pre-registration, freezing) live in CONSTITUTION P4 (ADR-002 entries T5–T6).

---

## 3. Three configuration axes

| Axis | Values | Comment |
|---|---|---|
| **Trace substrate** | parametric (vectors/weights, read by a trained interface before attention) ↔ symbolic (records, read as tokens) | the form of Φ |
| **Topology** | co-located (Φ inside the model / on the same machine) ↔ **split via PMI** (core at a provider, Φ at the owner) | the acts are the same; through PMI they are serialized (tool calls) |
| **Act state** | trained (organ trained once, core frozen after) ↔ prompted (rehearsal: acts given by a system prompt) | the E1 stand is prompted |

Target form of PlastFormer: parametric × co-located × trained. Stand configuration (E1): symbolic × split (PMI) × prompted. Both are described as PlastFormer; they differ in coordinates, not in architecture.

Ownership description: the frozen core K is shared weights; the plastic Φ belongs to one instance. Personal data are described as living in Φ and meeting the core through PMI functions in the instance's work. Instance continuity is described as preservation of the dedicated region between sessions. On a K version change, the question of Φ compatibility with the new core arises — see open questions.

## 4. Time: lived ticks, audited stamps, reconcile

Decay is described in **lived ticks** Δn (preprint §3.2, §3.5, §4):

- **Tick.** One tick = one inference step (one generation batch). The tick rate is a property of the substrate and is finite. Stand counter mapping: 1 executed storing act = +1 stand tick (sparse sampling of abstract ticks); see CONSTITUTION P6 for the enforceable counter rule.
- **Decay law.** a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks; all τ_i therefore in ticks.
- **Audited time** is symbolic: bi-temporal stamps on every trace (event time + learning time). A stamp reading "two years ago" carries no felt age and has no effect on amplitude in this description.
- **Lived (felt) time** is the substrate's own: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time in this description.
- **Two-clock gap as prediction error (physics):** a gap between audited stamps and the amplitude profile is described as a prediction error for the core that fires the surprise gate — the gap itself becomes an event of the biography.
- **`reconcile` (act):** read stamps, compare with felt age, deposit an explicit correction trace ("client data may be stale; confirm before acting") into a slow component. Felt time is not modified; a belief about its relation to world time is added beside it.

The acting whole at time t: **A(t) = (K, Φ(t))**. K is the frozen core; Φ(t) is the experience of this instance at tick t.

**Background tick (mechanism).** Background tick is described as the core running with no user input at a substrate-set low rate: replay of traces and `connect` acts issued by the core, each journaled as the core's act. A substrate process linking traces by itself (no core act) is a different mechanism and belongs to ablations (see CONSTITUTION P5/P9; ADR-002 entry T11).

## 5. Acts: name / repeat / connect / reconcile (+ write / read)

- **TICK is counted by the substrate/stand**, not issued by the model.
- **`name`** — fix source, time, boundaries; turns a drifting trace into an episode.
- **`repeat`** — re-amplify a trace, paying the write cost.
- **`connect`** — deposit a summary or rule into slow components as a *new* trace; sources untouched.
- **`reconcile`** — record the relation between felt time and audited time as a new trace (see §4 above).
- **Physical `write (unconscious)`** — described as: every experience passing the window leaves a low-amplitude trace in fast components, gated by the core's own surprise signal. On the symbolic stand the core's own prediction error is not accessible; the symbolic surrogate stays an ablation (see CONSTITUTION P5; ADR-002 entry T9).
- **Physical `read`** — surfacing through PMI (`read last N / ids / range`). On the symbolic stand, the content-free variant is described as: the N loudest traces by amplitude — no relevance, no embeddings. (Enforceable trigger/rank rules: CONSTITUTION P2; ADR-002 entries T7–T8.)

## 6. Bi-temporality and instance continuity (description)

Every fact recorded in Φ carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). Training weights carry no stream time; memory records carry both. The storage method (symbolic fields vs. parametric encoding) is an implementation question.

Continuity of an instance is described as following from preservation of Φ: the instance does not begin again with each session. Copying Φ is described as creating a branch — a new instance with shared history up to the copy point. Dormancy is zero lived time, and waking after dormancy is a recorded event (see §4). (Enforceable copy/continuity tests: CONSTITUTION P8/P10; ADR-002 entries T12–T13.)

## 7. Relation to earlier review points (mechanism reading; brief)

| Review point | Mechanism description |
|---|---|
| Where write competence comes from | Remembering is described as a trainable PMI competence; in an open model — training the organ once, core frozen after (§1, §5) |
| Write gates | Writing is described as the model's act; the executor executes (§5; enforceable test in CONSTITUTION P2/P5) |
| Bi-temporality in parameters | Stamps are described as a property of the memory act and PMI functions; storage method is implementation (§6) |
| Layers without mechanism | Layers are speeds: multi-τ decay of one trace (Fusi/Benna); five levels interpret the amplitude profile (§2–§2.1) |
| Copying | Copying is described as branching; identity = memory line (§6; test in CONSTITUTION P10) |
| Continuity vs. snapshots | Continuity is described as a property of the Φ line (§6; test in CONSTITUTION P8) |
| Personal data / deletion | Personal data are described as living in Φ; erasure as key destruction; derived traces are an open problem (preprint §6; tests in CONSTITUTION P7–P8) |

## 8. Open questions

- How to train PMI functions in an open model without destroying core competence; what signal trains `repeat` without training away legitimate repetition.
- Φ portability between core versions (K replacement; re-training the read interface for a parametric substrate).
- Tick economics at a provider: which product model makes the split (PMI) topology possible.
- Which tests distinguish PlastFormer memory from ordinary storage with a wrapper (description-level criterion: commands arrive from the model; enforceable test in CONSTITUTION P2/P5).
- How bi-temporal stamps are represented in a parametric substrate.
- Derived-trace (`connect`) erasure: whose key governs summaries derived from multiple subjects.

## 9. Honest boundary: what is unbuilt

- The memory organ is **not trained** — on the stand the acts are given by prompt (rehearsal, not the organ).
- The **parametric substrate is unbuilt** — parametric rank-1 writes on the frozen predecessor stand (research scope) remain future work; evaluation runs at the symbolic × split × prompted point.
- There are **no results** in this document — E1 is pre-registered (see `experiments/e1-protocol.md` v1.1 and preprint §7).
- The September 4, 2026 bench run is a pilot of loudness-readout mechanics with calendar aging — not evidence for event time (P1).
- P2 restates the immutable past: records are append-only; a position change is a new trace (security claims are outside the current stage); curation by omission (letting a trace decay by not repeating it) remains possible and is only journaled, not prevented.

## Composition

P1–P3 are compositional properties: every ingredient is individually known; the composition is the claim (preprint §1).

## Lineage

Primary disclosure: commit 539fc32 (2026-06-26). Source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204. Working name "Matryoshka" retained for lineage only.
