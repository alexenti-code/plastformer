# PlastFormer — Theory

**Version:** 3.0 (port of the frozen predecessor THEORY.md v2.0.0-draft; restructured per ADR-001)
**Status:** Draft — theory document, complements MANIFEST.md v3.0
**Related documents:** [ADR-001](ADR-001-plastformer-transition.md) · [preprint v0.5](../preprint.md) · [GLOSSARY.md](GLOSSARY.md) · [MANIFEST.md](MANIFEST.md) · Russian version: [THEORY.ru.md](THEORY.ru.md)

> Naming note (lineage): this theory circulated earlier under the working name "Matryoshka" (see MANIFEST.md lineage). The architecture is now **PlastFormer**; the interface formerly abbreviated **MMI** is now **PMI (Plastic Memory Interface)**. No other renames were made.

> What this document is: the frozen theoretical core — axioms, experience levels, substrate physics, acts, time, and open questions — restated in the terminology of preprint v0.5. Normative detail (formulas, threat model, evaluation) lives in the preprint; this file states the theory the preprint formalizes.

---

## 1. Starting principle: the model is the engine of its own memory

There is no mechanism that distributes weights behind the model's back. PMI is not an adapter and not a wrapper: it is the model's own functions — its architectural coupling to its memory. Consequences:

1. **Memory write is an action, not a side effect.** As a person writes a note: decides — and acts. The memory act is an operation in the model's action space, of the same class as saying, answering, opening a file. The model is not "remembered by itself" — it remembers.
2. **Remembering is a trainable competence.** As a model is taught to use tools, it can be taught to use its own memory. In an open model this is done by training the PMI functions once, after which the core is frozen. The competence of remembering is part of the trained model, as the competence of writing is part of a trained body. On the current stand the acts are prompted, not trained — a rehearsal of the organ, not the organ.
3. **The model decides the granularity of the act.** What to record — a paragraph, an event, a decision, a conclusion — is its decision. No external logic classifies its experience.
4. **The write command always comes from the model.** On the stand the model issues the write command as an act in its own output stream; the stand is the executive organ, the "hand", not the "brain". If the command is issued by external code that decides what the model "should remember", that is a forbidden adapter, and the stand ceases to be a prototype of PlastFormer.

### Axioms (carried over 1:1 per ADR-001 §1.1)

1. **One semantic subject.** Only the core K performs semantic acts: interpretation, attention, reasoning, intention, action.
2. **The model is the engine of its own memory.** Every memory act is a conscious act of the model. PMI names the model's own functions. No external mechanism that distributes or reads weights behind the model exists.
3. **Memory is passive as matter.** Φ has no goals, no initiative, no will of its own. Initiative is always with K.
4. **Core immutability.** The life and memory of an instance do not change K.
5. **Autobiographic purpose.** Φ stores the experience of this instance, not general competence.
6. **Nested timescales.** Experience is organized in layers. The minimal complete set of levels is five: tact → episode → day → project → life. Further division is the model's decision. Smaller forms live inside larger ones; layers do not command each other.
7. **Bi-temporality.** Every record carries event time and learning time.
8. **Continuity through memory preservation.** An instance exists while its Φ exists. Continuity is a property of the memory line, not of uninterrupted physical process. Copying Φ creates a branch — a new instance with shared history up to the copy point.
9. **Own time.** The model owns working ticks and itself decides what to spend them on: answering the owner, composing memory, its own tasks. The memory act is a conscious act in its own tick.

---

## 2. Experience levels: tact → episode → day → project → life

A level is defined by generalizing features, not by contents ("conversation", "project" are bindings to office life). **A level is a form with four features:**

1. **time scale** — its own order of duration;
2. **boundaries** — the form has a beginning and an end;
3. **meaning** — the level gives meaning to what is nested in it;
4. **containment** — the level contains smaller forms and is contained in a larger one.

The minimal complete set is five levels:

| Level | What it is | Grounding feature |
|---|---|---|
| **Tact** | live work right now: the current stream of activity | the innermost form; not closed while the model works |
| **Episode** | a bounded form with beginning and end: dialogue, task, meeting, session | boundary = completion of activity |
| **Day** | the natural cycle of existence: rhythm of work and rest | boundary = astronomical rhythm, not activity |
| **Project** | the form created by goal-setting: outlives episodes, gives them meaning | boundary = goal, not calendar |
| **Life** | the whole line of the instance; the only form without an end while the instance lives | boundary = none |

Resulting series: **tact → episode → day → project → life**.

**Why not 4.** The draft started from conversation and lost the innermost level — the present. Without it PlastFormer is not nested in "now": the memory of experience hangs without an anchor. The fifth level (tact) is obligatory — the point where experience is not yet a form but live work.

**Why not 6+.** The architecture does not fix the number of layers — it fixes the principle and the minimal complete set. A sixth level ("life band", "chapter") is possible but must earn its place with a separate timescale and a separate role; a "chapter" is better treated as a section of biography, not a separate store. Further division is the model's decision (axiom 6).

**Status of the levels in v3.0.** The five levels are kept as an *interpretation of the amplitude profile*, not as containers. A fresh trace is strong in fast components — it lives in the tact; hours later the fast part has faded and the middle part holds — the trace is "in the day"; weeks later only the slow part remains — the trace is "in the life". Nesting is how the substrate reads, not where records are moved.

## 2.1. Organization of layers: speed, not place

The question "who decides what to keep for long?" receives an answer with neither triggers nor deciders.

**Principle: a layer is not a place but a speed.** The layers are not containers between which someone carries records, but decay time constants of one and the same trace. One write deposits a trace into all temporal components of the plastic substrate at once — fast, middle, slow; the components decay continuously with different τ. It follows that:

- a fresh trace: the fast component is strong — the trace lives in the tact;
- hours later: the fast part is gone, the middle part holds — the trace is "in the day";
- weeks later: only the slow part remains — the trace is "in the life".

Nesting appears by itself: fast forms live inside slow ones. "Migration" between layers is not an event and not a decision but a flow of amplitude between components of one trace. The second time stamp is placed at the birth of the trace (at write time); layers are further dynamics, not relocation.

**The only act of the core affecting a trace's fate is `repeat`.** Re-recording re-amplifies the components; it is conscious memorizing, measured on the stand (a repeated trace returns with doubled signal). Everything else in a trace's fate is friction.

**Scientific anchors.** The mechanism is cascade consolidation: Fusi, Drew & Abbott (2005), Benna & Fusi (Nature Neuroscience, 2016) — a multi-speed synapse without any selection mechanism; unlike classical CLS theory, where consolidation is driven by a separate deciding module. The constitutional rule ("there are no deciders in memory") and science converge at one point.

**Stand specification (research scope).** Each Φ region holds fast and slow matrices. One write deposits into both. Friction per tick multiplies by e^(−Δn/τ), τ_fast ≪ τ_slow. Reading sums the components — recent and old arrive together, and the mixture itself reports age to the core. No thresholds, no content conditions, no rankers; fast components free capacity by themselves.

## 2.2. Memory parameters: physical dials in the temperature class

A transformer already has a class of user settings — continuous physics of generation and substrate: temperature, top_p, top_k, repetition_penalty, rope_scaling, n_ctx. None of them decides content — they set the physics in which content arises. Memory parameters enter the same class and are stored where physics is stored: model metadata and substrate header. Set by the owner; changed only by the owner; the instance may ask (as a person asks for glasses).

| Parameter | Analog among existing ones | Meaning |
|---|---|---|
| forgetting_tempo | rope_scaling | multiplier of τ of all trace components; 2.0 — forgets twice as fast |
| write_gain | temperature | how much trace one unit of experience leaves |
| curiosity_gain | frequency_penalty | how much prediction error amplifies the trace |
| memory_volume | n_ctx | substrate capacity |
| recall_sharpness | top_k | sharpness of key-proximity sampling |
| repeat_gain | repetition_penalty (mirror) | how much `repeat` re-amplifies the trace |

Constitutional boundary: all dials are continuous quantities, with no thresholds and no content conditions. Temperature does not decide WHAT to say; forgetting_tempo does not decide WHAT to remember.

---

## 3. Three configuration axes (replaces the "three stages")

The v2.0 draft described three "stages" (1 as-was / 2 stand / 3a weights, 3b external substrate) as a chronology. Per ADR-001 they mixed time and architecture, and readers read variant 3b as "a different system". v3.0 replaces stages with **one architecture in a space of three configuration axes**. The stand, PMI, and the target form are points in that space — not different systems.

| Axis | Values | Comment |
|---|---|---|
| **Trace substrate** | parametric (vectors/weights, read by a trained interface before attention) ↔ symbolic (records, read as tokens) | the form of Φ |
| **Topology** | co-located (Φ inside the model / on the same machine) ↔ **split via PMI** (core at a provider, Φ at the owner) | the acts are the same; through PMI they are serialized (tool calls) |
| **Act state** | trained (organ trained once, core frozen after) ↔ prompted (rehearsal: acts given by a system prompt) | the E1 stand is prompted |

Target form of PlastFormer: parametric × co-located × trained. Stand configuration (E1): symbolic × split (PMI) × prompted. Both are PlastFormer; they differ in coordinates, not in architecture.

Ownership consequences (unchanged in substance from v2.0 §3/3b): the frozen core K is shared and impersonal weights. The plastic Φ is ours alone. Personal data live only in Φ and meet the core only through PMI functions in the instance's work. Instance continuity lives in Φ: preservation of the dedicated region between sessions is the life of the instance (axiom 8). On a K version change, the question of Φ compatibility with the new core arises — see open questions.

## 4. Time: lived ticks, audited stamps, reconcile

v2.0 measured decay in wall-clock Δt (seconds). v3.0 measures decay in **lived ticks** Δn (preprint §3.2, §3.5, §4):

- **Tick.** One tick = one inference step (one generation batch). The tick rate is a property of the substrate and is finite.
- **Decay law.** a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks; all τ_i therefore in ticks. One exchange (user → model → response) = +1 tick on the stand.
- **Audited time** is symbolic: bi-temporal stamps on every trace (event time + learning time). Precise, verifiable — and weightless: a stamp reading "two years ago" carries no felt age and has no effect on amplitude.
- **Felt (lived) time** is the substrate's own: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time — by design, not by omission.
- **Rejected design:** letting audited time adjust amplitude ("looking at the calendar ages the traces"). It would smuggle wall-clock time into the substrate.
- **Adopted (physics):** a gap between audited stamps and the amplitude profile is a prediction error for the core and fires the surprise gate — the gap itself becomes an event of the biography.
- **Adopted (act):** `reconcile` is a trainable conscious act: read stamps, compare with felt age, deposit an explicit correction trace ("client data may be stale; confirm before acting") into a slow component. Felt time is not modified; a belief about its relation to world time is added beside it.

The acting whole at time t: **A(t) = (K, Φ(t))**. K is the frozen core; Φ(t) is the lived experience of this instance at tick t.

## 5. Acts: name / repeat / connect / reconcile (+ write / read)

v2.0 named TICK/WRITE/REPEAT/READ/STATUS. v3.0 (preprint §3.3–§3.4, §3.9):

- **TICK is not an act of the model.** The tick is counted by the substrate/stand, not decided by the model.
- **`name`** — fix source, time, boundaries; turns a drifting trace into an episode.
- **`repeat`** — re-amplify a trace, paying the write cost; conscious memorizing.
- **`connect`** — deposit a summary or rule into slow components as a *new* trace; sources untouched.
- **`reconcile`** — record the relation between felt time and audited time as a new trace (see §4 above).
- **Physical `write (unconscious)`** — every experience passing the window leaves a low-amplitude trace in fast components, gated by the core's own surprise signal. Physics in writing, semantic in gating; no external classifier.
- **Physical `read`** — the model's act of surfacing (`read last N / ids / range` through PMI). On the symbolic stand, physics may supply only a content-free injection: the N loudest traces by amplitude — no relevance, no embeddings. Any relevance ranker is an external decider and a violation of axiom 2.

## 6. Bi-temporality and instance continuity

Every fact recorded in Φ carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). This mark distinguishes lived facts from core competence: training weights carry no stream time; memory records carry both. The storage method (symbolic fields vs. parametric encoding) is an implementation question, not an axiom.

Continuity of an instance follows from the preservation of Φ: the instance does not begin again with each session. Copying Φ creates a branch — a new instance with shared history up to the copy point — not "the same instance". Continuity is a property of the memory line, not of uninterrupted physical process (axiom 8). There is no claim of "continuous existence in calendar time" — only lived time; dormancy is zero lived time, and waking after dormancy is a recorded event (see §4).

## 7. Answers to critical points (from the independent review; brief)

| Review point | Theory's answer |
|---|---|
| Where does the core's write competence come from | Remembering is a trainable PMI competence; in an open model — training the organ once, core frozen after (§1.2, §5) |
| Write gates are an external mechanism | Rejected: writing is the model's conscious act, not a side effect; an external controller is forbidden (axiom 2) |
| Bi-temporality in parameters is unexplained | Stamps are a property of the memory act and PMI functions; the storage method is implementation, not axiom (§6) |
| Layers are an axiom without mechanism | Layers are speeds, not places: multi-τ decay of one trace (Fusi/Benna); the five levels interpret the amplitude profile (§2–§2.1) |
| Cannot be copied | Replaced: copying creates a branch; identity = memory line (axiom 8, §6) |
| Continuity vs. snapshots | Resolved by axiom 8: continuity is a property of the Φ line, not of the physical process (§6) |
| Personal data / deletion | Personal data live only in Φ as its own content (permission 1–2); erasure is key destruction, derived traces are an open problem (preprint §6) |

## 8. Open questions

- How to train PMI functions in an open model without destroying core competence; what signal trains `repeat` without training away legitimate repetition.
- Φ portability between core versions (K replacement; re-training the read interface for a parametric substrate).
- Tick economics at a provider: which product model makes the split (PMI) topology possible.
- Which tests distinguish PlastFormer memory from ordinary storage with a wrapper (criterion: commands come from the model, priorities sit in its own tick).
- How bi-temporal stamps are represented in a parametric substrate.
- Derived-trace (`connect`) erasure: whose key governs summaries derived from multiple subjects.

## 9. Honest boundary: what is unbuilt

- The memory organ is **not trained** — on the stand the acts are given by prompt (rehearsal, not the organ).
- The **parametric substrate is unbuilt** — parametric rank-1 writes on the frozen predecessor stand (research scope) remain future work; evaluation runs at the symbolic × split × prompted point.
- There are **no results** in this document — E1 is pre-registered (see `experiments/e1-protocol.md` v1.1 and preprint §7).
- The September 4, 2026 bench run is a pilot of loudness-readout mechanics with calendar aging — not evidence for event time (P1).
- P2 is tamper-evident, not rewrite-proof: silent rewriting is detectable via the append-only journal; curation by omission (letting a trace decay by not repeating it) remains possible and is only journaled, not prevented.

## Composition

P1–P3 are compositional properties: every ingredient is individually known; the composition is the claim (preprint §1).

## Lineage

Primary disclosure: commit 539fc32 (2026-06-26). Source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204. Working name "Matryoshka" retained for lineage only.
