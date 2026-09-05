# PlastFormer — Glossary

**Version:** 4.0 (restructured per ADR-002; norms moved to CONSTITUTION.md v1.0)
**Status:** Draft — dictionary only, complements THEORY.md v4.0 and CONSTITUTION.md v1.0
**Related documents:** [THEORY.md](THEORY.md) · [CONSTITUTION.md](CONSTITUTION.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md)

> This file is a dictionary: term → definition. It states no rules and no tests. Enforceable statements previously located here now live in [CONSTITUTION.md](CONSTITUTION.md); the migration table is in [ADR-002](ADR-002-docs-architecture.md). Where this file and the preprint overlap, preprint v0.5 terminology governs the formalization.

---

## Glossary (English, with Russian term in brackets)

### PlastFormer [ПластФормер]
A transformer architecture with an unchanged core and a plastic per-instance module, organized in layers by timescale. One architecture with three configuration axes — substrate, topology, act training (see THEORY.md §3). Target form: parametric × co-located × trained.

### Idiographic memory [идиографическая память]
After Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case).

### Frozen core K [неизменное ядро, K]
The part of the model weights carrying general competence. Unchanged during the life of an instance. Shared by all instances of one core. Frozen after the single training stage that teaches the model to operate its own memory organ.

### Plastic module Φ [пластичный модуль, Φ]
The part of the model that changes under memorization without changing the frozen core. Belongs to one instance. In the target form: vectors/weights; on the stand: symbolic records.

### PMI — Plastic Memory Interface [ПМИ]
The architectural coupling connecting the frozen core with its plastic module in one model; the model's functions for writing and reading its memory. When core and module are physically split (core at a provider, module at the owner), the same acts cross the boundary serialized as tool calls; that serialization is PMI in the narrow sense.

### Memory act [акт запоминания] — name / repeat / connect / reconcile / read
An act of the model that writes into its memory as part of its activity — analogous to a person writing a note. The acts: `name` (fix source, time, boundaries), `repeat` (re-amplify, paying the write cost), `connect` (deposit a summary or rule as a new trace, sources untouched), `reconcile` (record the relation of felt time to audited time). `read` is surfacing (`read last N / ids / range` through PMI). TICK is counted by the substrate, not issued by the model.

### Instance A = (K, Φ) [экземпляр]
The acting whole A(t) = (K, Φ(t)). The core is shared by all instances of one core; the plastic module belongs to one instance.

### Bi-temporality [би-темпоральность]
Property of a Φ record: event time (when it was true in the world) and learning time (when the instance learned it). Training weights carry no stream-time marks; memory records carry both.

### Tick [тик]
One inference step (one generation batch). The substrate counts ticks; on the stand one executed storing act = +1 stand tick (sparse sampling of abstract ticks; counter rule in CONSTITUTION P6). The tick rate is a property of the substrate and is finite.

### Lived time [прожитое время]
The substrate's own time: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time in this description.

### Audited time [аудируемое время]
Bi-temporal stamps on every trace. Precise and verifiable; in this description they have no effect on amplitude.

### Trace amplitude [амплитуда следа]
A vector with one component per decay time constant τ_1 < τ_2 < … < τ_k: a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks. Content is immutable in this description; amplitude decays by substrate dynamics.

### Stand [стенд]
The external implementation of PlastFormer outside the model, rehearsing the functions of the future built-in memory from outside. Stand configuration: symbolic × split (PMI) × prompted. Parametric rank-1 writes on the frozen predecessor stand remain research scope.

### Journal [журнал]
An external append-only journal with a hash chain, kept by the environment. A chronicle — complete and immutable. Memory (selective, decaying) and journal (complete, immutable, post-mortem) are different objects (retention rules in CONSTITUTION P8).
