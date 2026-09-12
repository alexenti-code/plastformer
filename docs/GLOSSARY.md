# PlastFormer — Glossary

**Version:** 4.2 (disinfected 2026-09-10; corrected 2026-09-11: acts — seven, not eight; the split-era interface entry RETIRED)
**Status:** ACTIVE — dictionary only, complements THEORY.md v4.1 and CONSTITUTION.md v3.0
**Related documents:** [THEORY.md](THEORY.md) · [CONSTITUTION.md](CONSTITUTION.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md)

> This file is a dictionary: term → definition. It states no rules and no tests. Enforceable statements previously located here now live in [CONSTITUTION.md](CONSTITUTION.md); the migration table is in [ADR-002](ADR-002-docs-architecture.md). Where this file and the preprint overlap, preprint v0.5 terminology governs the formalization.

---

## Glossary (English, with Russian term in brackets)

### PlastFormer [ПластФормер]
A transformer architecture with an unchanged core and a plastic per-instance module, organized in layers by timescale. One architecture with three configuration axes — where the trace lives, topology, act state (see THEORY.md §3). Target form: parametric × co-located × instructed.

### Idiographic memory [идиографическая память]
After Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case).

### Frozen core K [неизменное ядро, K]
The part of the model weights carrying general competence. Unchanged during the life of an instance. Shared by all instances of one core. Frozen after the single instruction pass (the act grammar) that makes the model operate its own memory organ.

### Plastic module Φ [пластичный модуль, Φ]
The part of the same weight file that changes under memorization without changing the frozen part K. It is a section of one body, not a second store. Belongs to one instance.

### Embedded read interface (RETIRED — lineage only)
Historical name from the era when the model was described as two connected parts. There is no interface in the architecture: the model reads and writes its own Φ section by its own acts, as one body. The name is kept only so that old texts can be recognised; it must not appear as a live description. (Historical note: an early draft carried a split-topology interface abbreviated MMI, later PMI; the split topology is retired from the architecture.)

### Memory act [акт памяти] — name / repeat / connect / reconcile / read / calibrate / scan
An act of the model that writes into its memory as part of its activity — analogous to a person writing a note. The acts: `name` (fix source, time, boundaries), `repeat` (re-amplify, paying the write cost), `connect` (deposit a summary or rule as a new trace, sources untouched), `reconcile` (record the relation of felt time to audited time). `read` is surfacing (`read last N / ids / range` from the model's own Φ section). `calibrate` — the model inspects the physics of its own memory and proposes dial changes; boundaries are validated and changes apply from the next episode (budget capped; master switch owned by the owner). `scan` — the model inspects the Φ1 register layout. TICK is counted by the physics, not issued by the model. (Ratified set of SEVEN acts: `name`, `repeat`, `connect`, `reconcile`, `read`, `scan`, `calibrate` — act-grammar v0.2.0, owner approval 2026-09-09. The earlier "eight" was a numbering error in the CAL-1 protocol.)

### Instance A = (K, Φ) [экземпляр]
The acting whole A(t) = (K, Φ(t)). The core is shared by all instances of one core; the plastic module belongs to one instance.

### Bi-temporality [би-темпоральность]
Property of a Φ record: event time (when it was true in the world) and learning time (when the instance learned it). Training weights carry no stream-time marks; memory records carry both.


### Tick [тик]
One inference step (one generation batch). The code counts ticks; one executed storing act = +1 tick (sparse sampling of abstract ticks; counter rule in CONSTITUTION C5). The tick rate is fixed by the physics and is finite.

### Lived time [прожитое время]
Lived time is the record's own time: a trace's age is its amplitude profile; an interval's length is its tick count plus the accumulated trace mass. A year of dormancy is zero lived time in this description.

### Audited time [аудируемое время]
Bi-temporal stamps on every trace. Precise and verifiable; in this description they have no effect on amplitude.

### Trace amplitude [амплитуда следа]
A vector with one component per decay time constant τ_1 < τ_2 < … < τ_k: a_i(n) = a_i(0)·e^(−Δn/τ_i), Δn in lived ticks. Content is immutable in this description; amplitude decays by the physics of Φ.

### Stand [стенд] (RETIRED)
Historical term for an external implementation of PlastFormer outside the model, used in drafts before Φ was built. No live component carries this name. Forbidden as a live actor in any current document.

### Adapter [адаптер] / LoRA-adapter / base+adapter (RETIRED — forbidden)
The Instruction is a competency layer embedded once into the core; "adapter", "LoRA-adapter", and the split form "base+adapter" describe a temporary storage state of development, not an architecture entity. The artifact is ONE weight file. The split form is FORBIDDEN by the owner (2026-09-09) as a state, result, or "working pair".

### Harness / жгут (RETIRED — forbidden)
Development code that runs the physics during experiments is instrumentation ("инструментарий разработки") and lives outside the artifact. The role is the model's own; the physics is code (CONSTITUTION, ADR-003).

### PMI / MMI (RETIRED — lineage only)
Split-topology interface from early drafts. The split topology is retired from the architecture; the interface of the co-located configuration has no separate name. Historical mentions must carry a LINEAGE/RETIRED mark.

### trained (as a configuration value) (RETIRED — forbidden)
The canonical act-state value is **instructed** (one instruction pass, then frozen — O-8). "Trained" misdescribes the one-time embedding as ongoing training.

### Journal [журнал] — out of scope
An external append-only log with a hash chain, kept by a deployment for its own audit purposes (ADR-004). Audit belongs to deployment; PlastFormer neither includes nor claims a journal.

### Instruction [Инструкция]
A frozen competency layer carrying the act grammar — the rules by which the model operates its own memory: when to emit memory acts, how to write, how to read. Embedded once into the core by a single instruction pass, after which the core is frozen. The act of handing the model the rules of memory work is the Instruction; the core itself is never modified afterwards (except by that one embedding).

### Self-enrichment [самообогащение памяти]
The model's own act of adding new traces to its plastic module Φ during its life: writing facts, summaries, connections into memory without changing the core. The growth of the biography. (Next stage — self-improvement [самоулучшение] — means improving the memory operations themselves: how the model writes, reads, connects and consolidates; not yet part of the architecture.)

### PlastFormer (sense definition) [ПластФормер — смысл]
PlastFormer is a single weight file divided into sections: the section K stays the unchanged organism, the section Φ is a living, model-owned record. The model receives its memory rules through the Instruction, then enriches its own Φ section by itself. Transformer + plastic Φ.


### Φ-состояние [F-состояние, F-state] — состояние, не место
Набор записей Φ, поданных в вычисление модели прямо сейчас: постоянный набор (самые громкие записи по амплитуде) плюс записи, выбранные явными чтениями. Подаются в поток на слое 12 — в начало рабочей области (`docs/TABLE-MEASUREMENT-2026-09-12.ru.md`). Величина меняется от хода к ходу; именно ею управляет модель, выбирая, что прочитать.
**Не путать:** рабочая полоса (J-space) — не наше место и не наша сущность; это полоса слоёв внутри модели, она есть у всякой модели, связывающей шаги. Φ-состояние — то, что мы на эту полосу кладём. «Φ» — часть весов в файле; «Φ-состояние» — имя состояния, а не третьей части. Решение владельца 11.09.2026: именно **Φ-состояние**, а не «Φ-space», потому что space — это место, а места у нас нет.

### Проход отражения [reflection pass]
Приём обучения, перенятый из статьи о рабочей полосе (Anthropic, глава 7). Берётся задача, обрывается в случайном месте, дописывается короткий вопрос на размышление и ответ с опорой на Инструкцию; **правила из контекста убираются**, и ошибка считается **только на ответе-размышлении**. Навык вкладывается так, чтобы понятия Инструкции появлялись на рабочей полосе **без подсказки**. Технически — флаг «считать ошибку только на последнем сообщении». Не создаёт новой сущности и не меняет Φ.

### Объектив [J-lens, якобиев объектив]
Прибор: по промежуточной активации модели показывает, какие понятия она готова произнести на этом слое. Строится усреднением влияния малой добавки к активации на выход по множеству разных вопросов. Нужен, чтобы измерить, что попало на рабочую полосу, а не судить по ответу.

### Навык наготове [skill at the ready]
Метрика: понятия Инструкции присутствуют на рабочей полосе, когда их никто не звал. Проверяется объективом после прохода.
