# PlastFormer — Glossary, Axioms, Permissions

**Version:** 3.0 (port of the frozen predecessor GLOSSARY.md v2.0.0-draft; restructured per ADR-001)
**Status:** Draft — complements THEORY.md v3.0 and MANIFEST.md v3.0
**Related documents:** [THEORY.md](THEORY.md) · [THEORY.ru.md](THEORY.ru.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md)

> Renamed terms (lineage): **Matryoshka → PlastFormer** (the architecture; the working name "Matryoshka" is retained for lineage/DOI only, see MANIFEST.md); **MMI → PMI** (Plastic Memory Interface); "Memory Φ" → **plastic module Φ**. Preprint v0.5 terminology is normative where this file and the preprint overlap.

---

## Glossary (English, with Russian term in brackets)

### PlastFormer [ПластФормер]
Principle: the model is the engine of its own memory. The experience of an instance is stored in its own plastic module and organized in layers by timescale (see axiom 6 and THEORY.md, "Experience levels"). One architecture with three configuration axes — substrate, topology, act training (see THEORY.md §3). Target form: parametric × co-located × trained.

### Idiographic memory [идиографическая память]
The property PlastFormer implements, after Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case).

### Frozen core K [неизменное ядро, K]
The part of the model weights carrying general competence. Does not change during the life of an instance. Shared by all instances of one core. Frozen after the single training stage that teaches the model to operate its own memory organ.

### Plastic module Φ [пластичный модуль, Φ]
The part of the model that changes under memorization without changing the frozen core. Belongs to the instance. It is part of the model, not external storage and not a database. In the target form: vectors/weights; on the stand: symbolic records.

### PMI — Plastic Memory Interface [ПМИ]
The architectural coupling connecting the frozen core with its plastic module in one model; the model's own functions for writing and reading its memory. Not an external mechanism, not an adapter, not a layer, not an organ — the architectural coupling and the model's own functions. When core and module are physically split (core at a provider, module at the owner), the same acts cross the boundary serialized as tool calls; that serialization is PMI in the narrow sense.

### Memory act [акт запоминания] — name / repeat / connect / reconcile / read
A conscious act of the model: the model itself initiates and performs the write into its memory as part of its activity — as a person writes a note: decides, and acts. Not a side effect of computation, not an automatic process. The trainable acts: `name` (fix source, time, boundaries), `repeat` (re-amplify, paying the write cost), `connect` (deposit a summary or rule as a new trace, sources untouched), `reconcile` (record the relation of felt time to audited time). `read` is the model's act of surfacing (`read last N / ids / range` through PMI). TICK is not an act: the tick is counted by the substrate.

### Instance A = (K, Φ) [экземпляр]
The acting whole A(t) = (K, Φ(t)). The core is shared by all instances of one core; the plastic module is unique. Instance continuity is ensured by preservation of its Φ (axiom 8).

### Bi-temporality [би-темпоральность]
Property of a Φ record: event time (when it was true in the world) and learning time (when the instance learned it). Distinguishes lived facts from core competence: training weights carry no stream-time marks; memory records carry both.

### Tick [тик]
One inference step (one generation batch). The substrate counts ticks; one exchange (user → model → response) = +1 tick on the stand. The tick rate is a property of the substrate and is finite.

### Lived time [прожитое время]
The substrate's own time: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time — by design. Never a wall-clock quantity.

### Audited time [аудируемое время]
Symbolic bi-temporal stamps on every trace. Precise, verifiable — and weightless: they have no effect on amplitude. Sources of wall-clock data serve verification, never felt duration.

### Trace amplitude [амплитуда следа]
A vector with one component per decay time constant τ_1 < τ_2 < … < τ_k: a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks. Content is immutable; amplitude decays by substrate dynamics. Fresh traces are loud in fast components; only what survived repetition remains in slow ones.

### Stand [стенд]
The external implementation of PlastFormer outside the model. Rehearses the functions of the future built-in memory from outside, because we do not change models now. The stand is a prototype of the organ, not a crutch over the model: write commands come from the model, the stand only executes. Stand configuration: symbolic × split (PMI) × prompted. Parametric rank-1 writes on the frozen predecessor stand remain research scope.

### Journal [журнал]
An external append-only journal with a hash chain, kept by the environment, never written by the model. The journal is a chronicle — complete, immutable, outside the model's reach. It guarantees the integrity of what was recorded, not the completeness of recording. Memory and records are different objects with different obligations.

---

## Axioms

1. **One semantic subject.** Only K performs semantic acts: interpretation, attention, reasoning, intention, action.
2. **The model is the engine of its own memory.** Every memory act is a conscious act of the model. PMI names the model's own functions. No external mechanism distributing or reading weights behind the model exists.
3. **Memory is passive as matter.** Φ has no goals, initiative, or will of its own. Initiative is always with K.
4. **Core immutability.** The life and memory of an instance do not change K.
5. **Autobiographic purpose.** Φ stores the experience of this instance, not general competence.
6. **Nested timescales.** Experience is organized in layers. The minimal complete set of levels is five: tact → episode → day → project → life. Further division is the model's decision. Smaller forms live in larger ones; layers do not command each other.
7. **Bi-temporality.** Every record carries event time and learning time.
8. **Continuity through memory preservation.** An instance exists while its Φ exists. Continuity is a property of the memory line, not of uninterrupted physical process. Copying Φ creates a branch — a new instance with shared history up to the copy point.
9. **Own time.** The model owns working ticks and itself decides what to spend them on: answering the owner, composing memory, its own tasks. The memory act is a conscious act in its own tick.

---

## Permissions

1. **Personal data in memory are permitted.** Φ is part of the model held by the owner. The instance's memory is not an external database but part of the model itself; personal data in it are its own content.
2. **Personal data live only in Φ.** The core K neither contains nor changes them; the core stays shared and impersonal wherever it runs.
3. **A dedicated memory region is a permitted substrate.** The owner allocates the memory region its volume, preservation, and ticks — physical conditions. The model interacts with the region itself, in parallel with its other activity (axioms 2 and 9).
4. **Copying Φ is a permitted operation.** A copy creates a branch — a new instance with shared history up to the copy point, not "the same instance".
