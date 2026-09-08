# PlastFormer — Glossary

**Version:** 4.0 (restructured per ADR-002; norms moved to CONSTITUTION.md v3.0)
**Status:** Draft — dictionary only, complements THEORY.md v4.0 and CONSTITUTION.md v3.0
**Related documents:** [THEORY.md](THEORY.md) · [CONSTITUTION.md](CONSTITUTION.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md)

> This file is a dictionary: term → definition. It states no rules and no tests. Enforceable statements previously located here now live in [CONSTITUTION.md](CONSTITUTION.md); the migration table is in [ADR-002](ADR-002-docs-architecture.md). Where this file and the preprint overlap, preprint v0.5 terminology governs the formalization.

---

## Glossary (English, with Russian term in brackets)

### PlastFormer [ПластФормер]
A transformer architecture with an unchanged core and a plastic per-instance module, organized in layers by timescale. One architecture with three configuration axes — substrate, topology, act state (see THEORY.md §3). Target form: parametric × co-located × instructed.

### Idiographic memory [идиографическая память]
After Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case).

### Frozen core K [неизменное ядро, K]
The part of the model weights carrying general competence. Unchanged during the life of an instance. Shared by all instances of one core. Frozen after the single instruction pass (the act grammar) that makes the model operate its own memory organ.

### Plastic module Φ [пластичный модуль, Φ]
The part of the model that changes under memorization without changing the frozen core. Belongs to one instance. Φ holds vectors.

### Embedded read interface
The architectural coupling connecting the frozen core with its plastic module in one model; the model's functions for writing and reading its memory. The interface is embedded once — by a one-time instruction pass (the act grammar) — after which the core is frozen. (Historical note: an early draft carried a split-topology interface abbreviated MMI, later PMI; the split topology is retired from the architecture.)

### Memory act [акт запоминания] — name / repeat / connect / reconcile / read
An act of the model that writes into its memory as part of its activity — analogous to a person writing a note. The acts: `name` (fix source, time, boundaries), `repeat` (re-amplify, paying the write cost), `connect` (deposit a summary or rule as a new trace, sources untouched), `reconcile` (record the relation of felt time to audited time). `read` is surfacing (`read last N / ids / range` through the embedded interface). TICK is counted by the substrate, not issued by the model.

### Instance A = (K, Φ) [экземпляр]
The acting whole A(t) = (K, Φ(t)). The core is shared by all instances of one core; the plastic module belongs to one instance.

### Bi-temporality [би-темпоральность]
Property of a Φ record: event time (when it was true in the world) and learning time (when the instance learned it). Training weights carry no stream-time marks; memory records carry both.

### Rollback [откат]
Restoration of the bank to an earlier state, possible only through export/import (E4): a snapshot taken at tick N can be restored; within a live bank there is no rollback operation — traces are append-only (O-5) and decay is physics. Rollback is an environment/owner operation on the artifact, not a model act.

### Tick [тик]
One inference step (one generation batch). The substrate counts ticks; one executed storing act = +1 tick (sparse sampling of abstract ticks; counter rule in CONSTITUTION C5). The tick rate is a property of the substrate and is finite.

### Lived time [прожитое время]
The substrate's own time: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time in this description.

### Audited time [аудируемое время]
Bi-temporal stamps on every trace. Precise and verifiable; in this description they have no effect on amplitude.

### Trace amplitude [амплитуда следа]
A vector with one component per decay time constant τ_1 < τ_2 < … < τ_k: a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks. Content is immutable in this description; amplitude decays by substrate dynamics.

### Stand [стенд] (retired term)
Historical term for the external implementation of PlastFormer outside the model, used in drafts before the vector substrate was built. No live component of the architecture carries this name.

### Journal [журнал] — out of scope
An external append-only log with a hash chain, kept by the environment at deployment time. Not part of PlastFormer: the architecture neither includes nor claims a journal (ADR-004). A deployment may add one for its own audit purposes.

### Instruction [Инструкция]
A frozen competency layer carrying the act grammar — the rules by which the model operates its own memory: when to emit memory acts, how to write, how to read. Embedded once into the core by a single instruction pass, after which the core is frozen. The act of handing the model the rules of memory work is the Instruction; the core itself is never modified afterwards (except by that one embedding).

### Self-enrichment [самообогащение памяти]
The model's own act of adding new traces to its plastic module Φ during its life: writing facts, summaries, connections into memory without changing the core. The growth of the biography. (Next stage — self-improvement [самоулучшение] — means improving the memory operations themselves: how the model writes, reads, connects and consolidates; not yet part of the architecture.)

### PlastFormer (sense definition) [ПластФормер — смысл]
PlastFormer is a dedicated layer of the weight file reserved for the fact of memory: a transformer whose weights are split so that one part stays the unchanged organism and another part is a living, model-owned record. The model receives its memory rules through the Instruction, then enriches its own plastic layer by itself. Transformer + plastic Φ.
