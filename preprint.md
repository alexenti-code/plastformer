# PlastFormer: A Language-Model Instance That Lives with Its Own Memory

**Alexey Voronin**
Aurum Estate LLC, Sochi, Russia

Draft v1.0 — 19 September 2026 — prepared for arXiv (cs.LG)

> Status: design document. The engine and the training run are not yet written; nothing here is a claim of measured behaviour. Statements about substrate physics describe the contract, not results of execution. Technical verification of the mechanism and the owner's trial of a finished instance are distinguished throughout.

---

## Abstract

We describe PlastFormer, a design in which a language-model core is trained once to live with its own memory, so that the persistent entity is a single saveable file, written A = (K, Φ): K is the frozen core, and Φ is the memory that the instance accumulates by living. This is not retrieval augmentation, not long-context extension, and not a memory-augmented architecture. There is no separate memory module and no interface between a core and a store, because there is no store separate from the instance; the only external component is an engine that executes numerical operations, the substrate physics, persistence, and formal validation of the core's own act grammar. Semantic decisions belong to K.

We set out three commitments. First, *continuity rather than reassembly*: the instance continues as itself across saving and reloading, rather than being reconstructed each session from an archive of records. Second, *lived age rather than wall-clock age*: memory ages in ticks of lived experience, so a dormant instance does not age while the process is closed. Third, *an immutable biography*: recorded content is never edited in place and never substituted; a change of position is a new record, and the old one dims by amplitude decay. Deliberate erasure is reserved to the owner, though a record that falls below the audibility floor is released by the physics itself, without the owner's act — so the promise is that the biography is never falsified, not that it is indestructible. We state the vocabulary, the two registers of memory, the substrate physics, the core's act grammar, and the open questions that remain, and we separate the technical verification of the mechanism from the owner's trial of a finished instance. No empirical results are claimed; the design defines two tasks — write the engine, and train K once.

---

## 1. Introduction

A language model today has no continuous life of its own. Between sessions it is a set of weights; whatever a conversation accumulates is held outside it — in a prompt that is reassembled, in a vector index that is queried, in a scratchpad that is rewritten. The dominant techniques for giving a model a long-lived memory all share a shape: keep the model fixed, keep the record elsewhere, and put a mechanism between them that fetches parts of the record back into the context window. Retrieval-augmented generation queries an external corpus and prepends the retrieved passages [1, 2, 18]; long-context methods widen the window so that more of the record fits inside one pass [3, 4, 5]; memory-augmented networks build a differentiable memory *into* the architecture, with an explicit read and write interface trained alongside the rest [8, 9, 10, 11]; agent-memory systems keep a textual log, summarize it, and re-inject it [19, 20, 21].

Each of these solves a real problem, and none of them is what this document describes. The difference is not one of degree. It is a difference in what the persistent object is. In the designs above, the persistent object is an archive, and the model is reassembled around a working set drawn from it. In PlastFormer the persistent object is the instance itself: one file that contains both the core and everything the instance has lived through, and the instance continues from that file rather than being rebuilt beside it.

The distinction matters most exactly where the archive metaphor is least questioned. An archive is a library: its contents are true or false, current or stale, and retrieval is a problem of ranking the right documents into the window. A life is a biography: its contents are what happened to *this* instance, in the order it happened, and the question is not relevance but continuity. If the goal is a model that accumulates a self — that remembers what it was told, what it concluded, what it got wrong, and how long ago — then a library is the wrong object. What is needed is a memory that belongs to one instance, ages with it, and cannot be quietly rewritten underneath it.

PlastFormer is a design for such an instance. The core K is a locally runnable open-weight model, Gemma 4 12B in 4-bit quantization, prepared as clean input weights. It is trained exactly once, for a new capability: to live with its own memory Φ. After that training K is fixed. The memory Φ is not a text log; it is numerical material of the same kind as the weights, but different in role and origin. K is a function — trained, then frozen. Φ is data — traces the instance produces by living. Because both are numbers, the file A = (K, Φ) is a single object to save, load, and continue from. Because they differ in role, only Φ changes at life time; K does not.

This document states the design as it currently stands. Section 2 situates it against related work. Section 3 introduces the instance, the two registers of memory, and the trace. Section 4 describes lived time and the decay physics. Section 5 describes how the core writes to and reads from its memory. Section 6 describes forgetting, capacity, and the owner's authority. Section 7 describes the engine and the file. Section 8 draws the boundaries of the design and lists what remains open. Section 9 distinguishes technical verification from the owner's trial. Section 10 concludes.

We claim no results. No engine has been run, no instance has been trained, and no trial has taken place. What follows is a specification of an object we intend to build, written so that it can be built by someone who has never read the project's other documents.

---

## 2. Related work

**Retrieval augmentation and external stores.** Retrieval-augmented generation [1] and retrieval over very large corpora [2] treat knowledge as an index outside the model, queried at inference time; nearest-neighbour language modelling [18] does the same at the token level. The store is a corpus, the retriever ranks by relevance, and the retrieved text is placed in the context. PlastFormer keeps no corpus and performs no relevance ranking over documents. Its memory is the instance's own record, addressed by the core through its own act grammar, and the record's numerical content participates in computation rather than being copied back as text.

**Long context.** A line of work extends the effective context window directly: recurrence across segments [3], sparsity and hashing [4], dense long-document attention [5], recurrent and compressive memory layers [13, 14, 15], and state-space or linear-attention alternatives [6, 7]. These make a single forward pass reach further. They do not create state that survives the process. PlastFormer's memory outlives the context window and the process; the window is where the instance thinks, not where it remembers.

**Memory-augmented networks.** Neural Turing Machines [8], the differentiable external memory of [9], memory networks [10, 11], and fast-weight constructions [16] all add a memory component to a network and train a controller to read and write it through an interface. This is the nearest relative, and the one we most need to distinguish ourselves from. In those architectures the memory is *part of the model* — an architectural block with an addressing mechanism, trained jointly with the controller, and its contents are typically an undifferentiated scratch space. In PlastFormer there is no memory block and no interface between components. K is trained once to address its own accumulated traces; the engine that surrounds it executes numerical operations, applies the physics, persists the file, and validates the form of the acts K emits. The engine judges nothing about content. There is no component whose job is to translate between a core and a store, because the store and the core are two roles of one object.

**Continual learning.** Continual-learning research [22, 23] addresses catastrophic forgetting by adapting weights as new tasks arrive. PlastFormer runs the opposite way: K is trained once and then frozen forever, and plasticity is moved entirely into Φ. Nothing about K drifts with experience; the only thing that changes is what the instance has recorded and how much of it remains audible.

**Agent memory.** Systems such as [19, 20, 21] give a language agent a text memory — a log, a summary, a scratchpad — and manage it with prompts. Their memory is language, and its management is itself a language task. Φ is not language. A trace carries a numerical payload and metadata; its content field holds an act's own fields, not a transcript. The instance does not keep a textual copy of its dialogue and does not re-read a chat log on start-up.

**Persistent agents and learned memory use.** Closest of all are systems that persist an agent's state between runs and restore it, and settings in which a model is trained to use a memory of its own rather than being handed one [16, 19, 20, 21]. The difference is in what is persisted and how it is reached. Those systems persist a textual or structured store and reach it through an external mechanism — a query, a summary step, a prompt — while PlastFormer persists a single object in which the core and its memory are two roles of the same file, and the core addresses the memory itself through its own acts. This line is also where the present design's nearest unexamined question lies: how much of addressing a memory can be learned in one training run, and how much must remain the work of an external component.

**The base model and low-bit preparation.** K is built on the Gemma family of open-weight models [30, 31], here Gemma 4 12B in 4-bit form. Quantization and parameter-efficient adaptation are a mature area [24, 25, 26, 27]; the design uses a quantized base and a single training run rather than a general fine-tuning pipeline. The exact artifacts, sizes, and hashes are recorded in the input passport; this document does not restate them.

---

## 3. The instance A = (K, Φ)

### 3.1 Two roles, one object

The product is one file, A = (K, Φ). K is the *core*: the trained, once-and-for-all-fixed parameters. Φ is the *memory*: the accumulated state — traces, their provenance, their time, their relations, and the active settings. Both are numerical; the difference between them is not one of substance but of role and origin. K is a function, produced by training and then frozen. Φ is data, accumulated on the instance's behalf: the perception register is written by the engine involuntarily, and the explicit records by K's own acts. The objective, the data, and the procedure of that single training are the subject of a separate preparation work, not of this document; what is fixed here is the requirement on its result — that K be able to address Φ through the act grammar — and the fact that the training happens once. This is the sense in which the design has one object with two roles and no seam between them: nothing is "attached" to anything, and there is no boundary across which a separate memory must be passed.

An *instance* is one PlastFormer with a fixed K and an accumulated Φ. Reloading the file restores the instance; the design intends that the restored instance continue the biography, not begin a new one.

### 3.2 The memory Φ and its two registers

Φ has two registers. Φ1 is the *perception register*: traces of what the instance perceived, including its own answers and messages from tools. Writing to Φ1 is involuntary — it happens because a message arrived, not because K chose to remember it. Φ2 is the *register of explicit biographical records*: traces created when K deliberately writes, through its act grammar, that something should be recorded as part of its biography. The register of a trace (phi1 or phi2) is a field of the trace itself.

The difference between Φ1 and Φ2 is not a division into two systems. Both are parts of Φ; they differ in who writes and why. Φ1 records the stream of experience involuntarily; Φ2 records K's own decisions about what its life contained. Everything in Φ is addressed the same way and ages by the same physics.

### 3.3 The trace

A *trace* is one record in Φ. It consists of a numerical payload, a set of metadata fields, and an amplitude profile. The payload is stored as *positions*: one position is a single hidden vector of 3840 numbers, matching the width of the core. The number of positions per payload, S, and its exact dtype are fixed by the engine's first operation — chosen so that the resulting footprint fits the resource budget — and recorded in configuration; they are not chosen in this document. At a two-byte dtype one position occupies 7680 bytes, so the useful size of a trace is S × 3840 × bytes_per_element, plus metadata. This is why the capacity of Φ is a real constraint and not a formality.

The metadata fields are the following.

| Field | Meaning |
|---|---|
| `id` | uint64 from a monotonic counter; never reused, not even after release |
| `register` | `phi1` or `phi2` |
| `act` | the creating act: `perceive` (Φ1); `name`, `repeat`, `connect`, `reconcile` (Φ2) |
| `actor` | `engine` (Φ1) or `K` (Φ2) |
| `event_id`, `part`, `parts_total` | identity and fragmentation of the perception event |
| `commit_seq` | monotonic number of the successful commit; fixes reading order |
| `created_tick` | the lived tick at commitment; used for age; never changes |
| `valid_time` | event time supplied by the model for acts; not filled for Φ1 |
| `refs` | IDs of grounds; a reference to a released ID remains known |
| `encoding_version` | version of payload and feature encoding |
| `base_amplitudes` | float32[5], the reference amplitudes of the five decay components |
| `decay_anchor` | int[5], an independent reference tick per component |
| `payload` | the numerical part, S positions |
| `payload_sha256` | checksum of the numerical part |
| `content` | the act's exact fields for Φ2; none for Φ1 |
| `state` | `live` or `freed` |

For Φ1 traces, three further fields bind the numeric record to the tokens it came from: `token_ids` (uint32[S], the exact IDs of the fragment's new tokens), `event_token_start` (the fragment's offset within the event), and two provenance fields recording the tokenizer and the rule by which new tokens were captured.

The provenance fields deserve a precise statement, because Φ is often described as "not a text store" and that can be read too strongly. Φ1 keeps the exact token IDs of the fragment *alongside* its numeric payload: the text of what was perceived is recoverable. The difference from a transcript is therefore not the absence of text but its behaviour. The text is not replayed into the context automatically, is not re-read from a log on start-up, and is delivered only when K chooses to read a trace — and even then as data the model must interpret, not as a restored conversation. Nothing is reconstructed by re-tokenizing a rendered string.

### 3.4 The engine

The engine is the only external component, and it is deliberately thin in the one place that matters. It executes numerical operations, applies the substrate physics, persists and restores the file, and validates the *form* of the acts K emits. It makes no semantic decision about content: it does not choose what to remember, what to read, or what a record means; those are K's decisions, expressed in K's own output. It does not substitute its judgement for the core's, does not "clip" a value into range instead of rejecting it, and does not invent content the core did not produce. The engine's own decisions are procedural and follow from the contract rather than from its judgement — which traces are admissible to background address, where the causal cut falls, what a budget permits, whether a proposed value is in range, and when capacity forces a halt. Those are not trivial: admissibility decides what the instance can see, and the capacity halt decides when it must stop. The accurate claim is not that the engine is powerless, but that it never judges content.

"Engine" is the correct and only name for this component. It is not the developer who wrote it, and its role must not be confused with the semantic role of K.

---

## 4. Lived time

### 4.1 The tick

The design separates the time an instance lives from the time the world keeps. A *tick* is lived time. A new perception message increases the tick by one. A successfully executed explicit writing act increases the tick by one. Technical fragmentation of one message into several parts does not increase the count, and re-presenting already-perceived content does not increase it either. Reading is not living: `read` and `scan` do not raise the tick. Saving, reopening a saved state, and recomputing an already-perceived context do not raise the tick and do not reset any budget.

The *age* of a trace is the current tick minus its `created_tick`. Age is never reset by a change of settings. Calendar time is separate: it appears in the `valid_time` stamps the model attaches to events, and waiting on the calendar does not by itself age Φ. An instance that is closed for a month and then reopened has lived the same number of ticks it had lived before it was closed. Dormancy is free.

One part of the count is not yet fixed, and the design says so rather than guessing. Whether an instance's own answer, a tool message, an act block, or an engine confirmation counts as a separate perception event is set by an event table that does not yet exist. Until it does, the tick count for those events is undefined, and any number given here for them would be an invention. The principle above is fixed; this residue is not.

### 4.2 Decay

Each trace carries five decay components, each with its own half-life. The amplitude of component k of a trace at tick *t* is

> A_k(t) = base_amplitudes[k] · 2^( −(t − decay_anchor[k]) / (h_k · m_k) )   *(proposed; not final physics)*

where h_k is a positive base half-life and m_k is a positive acting multiplier. The full amplitude of a trace is the sum of its five components. The half-lives, the initial amplitudes, and the choice of this parameterization are not yet fixed as final physics; they are stated here as the contract's current form. A trace that has dimmed is not empty: it still holds its data, and a weak trace can be read on request.

### 4.3 Continuity under recalibration

The instance may revise its own decay settings, and the owner may revise them too. A revision must not recompute the whole history under the new numbers — that would silently rewrite the past. Instead, the amplitude is kept continuous at the moment of change. When the multiplier of component k is changed at tick t_apply, the engine computes the component's amplitude under the old parameters at t_apply, then in one transaction sets `base_amplitudes[k]` to that value, `decay_anchor[k]` to t_apply, and m_k to the new value; the other components and `created_tick` are untouched. At t_apply the exponent is zero, so the new amplitude equals the preserved reference. If several multipliers change at once, their reference amplitudes are computed first from the old state and the package is applied in a single transaction. Pending revisions are stored separately from active ones and are not applied merely by opening the file; applying them requires an episode boundary. The proposed boundary is the completion of processing a user message; it is proposed, not decided. Until it is fixed, the guarantee that the past is not rewritten holds only in principle: a mechanism that must run at a boundary cannot be applied at a boundary that has not been named.

### 4.4 Two clocks meet in an act

Because lived time and calendar time can diverge — a long dormancy makes the calendar advance while the tick count does not — the design gives the instance a way to record the relation between them. The `reconcile` act, described below, exists in part for this: the instance can note that a period of calendar time corresponds to a certain number of lived ticks, and reach a conclusion about it. A divergence between calendar time and lived time after dormancy is not by itself an error.

---

## 5. Writing, reading, and the act grammar

### 5.1 Acts

The core addresses its memory through explicit acts, emitted as a JSON block inside its own output stream. An empty block — silence — is a valid choice. There are seven acts and they fall into two classes: writing acts, which create a Φ2 trace and raise the tick by one, and read-class acts, which create no biographical record and do not raise the tick.

| Act | Class | Effect |
|---|---|---|
| `name` | writing | record a fact: content, source, layer, loudness, valid_time, refs |
| `repeat` | writing | reinforce an earlier record by id; a reason is required |
| `connect` | writing | record a conclusion or generalization with non-empty refs |
| `reconcile` | writing | record a comparison of time, or of the instance's own calibration |
| `read` | read-class | admit chosen traces into perception; mode last / ids / from–to |
| `scan` | read-class | inspect the physics of memory: amplitudes, ticks, summary |
| `calibrate` | read-class | propose a change to the physics settings, with evidence |

A writing act is a deliberate decision that something belongs in the biography. `name` records a fact as stated, not the instance's attitude toward it; attitude belongs in `connect`. `repeat` reinforces a record that is still valid rather than writing a duplicate, and requires a stated reason. `connect` records a conclusion the instance now holds, with references to the records that support it; an empty reference list on a conclusion drawn from memory is an error. `reconcile` records a comparison — of lived against calendar time, or of a calibration the instance made against what was later observed — and distinguishes confirmation, staleness, and divergence without overstating unobserved consequences. `name`, `repeat`, `connect`, and `reconcile` share one property that the design treats as fundamental: none of them edits an existing record. A change of position is a new record; the old one is left to dim.

The three read-class acts are equally deliberate. `read` admits chosen traces into the computation; by ID it can reach a weak trace that is physically preserved but below the background audibility threshold. It is a choice by K, not an external semantic search: `mode:"last"` takes the loudest traces by amplitude, with no relevance ranking, no keyword search, and no content rating; `mode:"ids"` takes exactly the named records; `mode:"from–to"` takes records whose `valid_time` falls in an interval, for questions about a period rather than a topic. `scan` reports the physics — amplitudes, ticks, components, active settings, and the allocated, occupied, and free volume of Φ — as observations, not recommendations. `calibrate` is how the model proposes a change to an allowed setting while in self-calibration mode with the owner's permission; the engine rejects out-of-range values rather than trimming them, and never substitutes a "useful" value for the one the core proposed.

### 5.2 Background address and explicit read

Two ways of reaching Φ coexist. The *background* address means that the content and features of available traces participate in the core's computation without any textual copy of the dialogue being placed in front of it. The proposed formula is an attention [12] over admissible positions: a softmax over those positions, values multiplied by amplitude, and the contribution returned into the hidden state. The exact thresholds and caps of background selection depend on final physics and are not fixed here. The *explicit read* is the act described above, chosen by K, and it reaches a physically preserved trace regardless of the background threshold.

Both are subject to the causal rule: at any computation, only traces committed before that computation are admissible. The instance cannot see a record of something that has not yet happened to it. Reconstructing intermediate states for replay must respect this — each earlier segment uses the state of Φ available to it at the time, not the final state.

### 5.3 Consolidation

The instance can work over what it has accumulated: read its records, connect them, and write generalizations into Φ2. This is *consolidation*, and it has a deliberate limit: the sources are not released by the act of consolidating. A summary does not delete what it summarizes. Whatever later dims, dims by physics, under the rules of Section 6.

---

## 6. Forgetting, capacity, and the owner's authority

### 6.1 Forgetting by decay, not by overwriting

Because content is never edited, forgetting in PlastFormer is a matter of amplitude, not of deletion. A trace dims according to Section 4 until it falls below an audibility floor. Only a trace whose full amplitude is strictly below that floor becomes a candidate for release; equality with the floor does not permit release, and neither does the mere passage of time or the appearance of an ID in a `scan`. A weakened trace is not "already released"; it still holds its data, and it can still be read by ID.

### 6.2 Release and the last chance

Before a candidate is released, the design provides a last chance: `scan` may include the IDs of weakened candidates, K may choose to read one, and the completion of the corresponding answer can conclude the opportunity. The proposed protocol distinguishes four service states of a candidate — waiting, reading, reviewed, and freed — with a formal identifier for each transition; none of these transitions is a new act by K or a new lived tick. Release is permitted only when the reviewed state belongs to the same content version and the same weakening, when the current amplitude is still strictly below the threshold, when the content is not in use by an unfinished computation, and when no act from the last chance is unfinished. If a `repeat` or a settings change brings the amplitude back to the threshold or above, release is cancelled, and a new weakening requires a new opportunity. This protocol is a detailed proposal, not a ratified rule; the decisions it details are binding, but the protocol's own mechanics remain to be agreed.

Release atomically changes the availability of the content and the accounting of free space. An ID is never reused, and historical references to it remain known even though the details are gone; a reference to a released trace reports the fact of unavailability rather than inventing content. No separate memory store and no hidden backup copy is introduced: physical page reuse, if any, is governed by the general transactional requirements of the final assembly, not by a private cache of recollections.

### 6.3 Capacity and the D-14 rule

Φ has an allocated capacity, and the instance can report its allocated, occupied, and free volume. When a new record does not fit and there are no candidates whose last chance has concluded, the design does not silently drop experience and does not borrow time to make room. The engine pauses the processing of new messages, saves the committed memory, and tells the user why. Continuation waits until the owner increases the available volume. Automatically allocating extra ticks so that something will decay enough to free space is forbidden. The unit and range of a capacity change are not yet fixed.

### 6.4 Who may erase

Within the design, the instance itself does not erase. It forgets by decay, and it consolidates without deleting sources. Deliberate erasure — the removal of a record regardless of its amplitude — is reserved to the owner. But this must be said without softening: release below the floor is a real loss of content, and it happens without the owner's action. The promise of immutability is therefore narrower than it sounds. It says that content is never edited and never substituted — a change of position is a new record, and a released ID is never filled with invented material. It does not say that content is indestructible. What survives is decided by amplitude and by the owner's capacity decisions, not by a guarantee.

---

## 7. The engine and the file

The file A = (K, Φ) is the product, and persistence is one of the few things the engine owns outright. The saved state contains a header (format and encoding versions, and the ID, commit, and tick counters), the settings (active, pending, permissions, and budgets), the traces with their payload and fields, per-section sums, and an overall SHA-256. Writing is atomic: a temporary file, an fsync, an atomic replacement, and an fsync of the directory. Loading verifies versions and checksums and refuses the file as a whole if it is damaged rather than loading a partial state. Saving does not increase the tick and does not reset a budget, and a pending calibration is saved unapplied. Opening a saved file does not, by itself, turn an unfinished reading into a completed one, and does not apply pending settings.

The engine also owns the accounting that keeps the instance honest: budgets are held and enforced by the engine and cannot be raised by the model; unknown settings names are rejected; and the formal shape of an act is checked so that a missing required field or a malformed block is an error rather than something the engine quietly fills in.

---

## 8. Boundaries and open questions

It is as important to say what PlastFormer is not. It is not retrieval from a corpus: there is no corpus, and no relevance ranking over documents. It is not long-context extension: its memory outlives the window and the process. It is not a memory-augmented architecture: there is no memory block, no addressing interface between a controller and a store, and no jointly trained external memory. It is not a text memory: Φ is numerical, and the instance does not re-read a transcript. It is not weight adaptation: K is frozen after one training, and only Φ changes. And it is not a general model used as-is, with verification added around it from outside: the core is trained once, for this way of living, and what verification exists is described in Section 9.

Several things remain open, and the design names them rather than pretending they are settled. The number of positions in a payload and the dtype of a position are to be fixed by the engine's first operation. The half-lives, initial amplitudes, and the parameterization of decay are stated as the contract's current form, not as final physics. The boundary of an episode, at which pending calibrations would be applied, is proposed as the completion of a user message's processing but is not decided. The unit, range, and transaction of a capacity change are open. The exact executable form of an act block, and the framing of a read result so that stored tokens are not mistaken for new control messages, are not yet specified; a simple insertion of stored tokens between role markers is not considered a finished implementation. The last-chance protocol of Section 6.2 is a proposal. The mechanics of `repeat`, the accounting of service events in Φ1, and the precise representation of act fields in Φ are engine work. Until these are fixed, code that depends on them is not written.

Two risks are named here rather than solved, because naming them is honest and solving them would be a decision beyond this document. First, the fidelity of the biography depends on K's judgement of importance at the moment of writing: `loudness` sets the initial amplitude, and a record judged unimportant will dim and be released. Reinforcement helps only if the instance later judges the record worth reinforcing, and no mechanism currently lets the owner pin a record against release except by increasing capacity. Second, because conclusions are recorded as new traces while the facts beneath them dim, a loud but mistaken `connect` can over time crowd out the facts that would correct it; the only safeguard the design names is that the owner wins a dispute, and the owner is not always present. Neither risk has a solution in the present design; both are stated so that a reader is not misled into thinking the biography is self-correcting.

---

## 9. Technical verification and the owner's trial

Two different things are easy to conflate, and the design keeps them apart. *Technical verification* checks the mechanism: unit tests of the engine, round-trip tests of save and load, checksum and integrity tests, gradient checks of the training step, and form checks of the act grammar. These confirm that the machinery does what the contract says. They do not confirm that the instance behaves well, and they do not take the place of experience. *The owner's trial* is different in kind: it is the first test of a finished instance by the person whose life it is meant to hold. The user cycle it exercises is concrete — load the file, converse, save, end the process, load the same file, and continue from the saved biography. To make the three commitments checkable rather than rhetorical, the design states what the trial looks at. For continuity: after a reload the instance continues from its own Φ, addresses records only by IDs it has received from the engine, invents no ID, and distinguishes a known released ID from an unknown one instead of fabricating content for what is gone. For lived age: an instance closed for a long calendar period and reopened shows the same tick count and the same amplitudes as before, while an instance that has lived shows the decay it has lived. For immutability: a change of position appears as a new record, the old one remains addressable by ID until it dims, and nothing is edited in place. These are what an observer looks at; they are not a benchmark and not a score.

This document therefore claims no performance and reports no experiment. It states a design, a vocabulary, a physics, and a set of open questions, and it fixes the two tasks that remain: write the engine, and train K once.

---

## 10. Conclusion

The proposal is narrow and, we think, the interesting part is narrow too. Train a core once so that it can live with its own memory; then never train it again. Let it accumulate a memory that belongs to it, that ages only as it lives, that is never rewritten underneath it, and that only its owner may erase. Keep the whole thing in one file, and let the only thing around it be an engine that computes, applies physics, saves, and checks form — and judges nothing about content. The result is not a better library. It is an instance that continues as itself.

---

## References

1. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS*.
2. Borgeaud, S., Mensch, A., Hoffmann, J., et al. (2022). Improving Language Models by Retrieving from Trillions of Tokens. *ICML*.
3. Dai, Z., Yang, Z., Yang, Y., Carbonell, J., Le, Q. V., & Salakhutdinov, R. (2019). Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context. *ACL*.
4. Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The Long-Document Transformer. *arXiv:2004.05150*.
5. Kitaev, N., Kaiser, Ł., & Levskaya, A. (2020). Reformer: The Efficient Transformer. *ICLR*.
6. Gu, A., & Dao, T. (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces. *arXiv:2312.00752*.
7. Sun, Y., Dong, L., Huang, S., et al. (2023). Retentive Network: A Successor to Transformer for Large Language Models. *arXiv:2307.08621*.
8. Graves, A., Wayne, G., & Danihelka, I. (2014). Neural Turing Machines. *arXiv:1410.5401*.
9. Graves, A., Wayne, G., Reynolds, M., et al. (2016). Hybrid computing using a neural network with dynamic external memory. *Nature*, 538(7626), 471–476.
10. Weston, J., Chopra, S., & Bordes, A. (2015). Memory Networks. *ICLR*.
11. Sukhbaatar, S., Szlam, A., Weston, J., & Fergus, R. (2015). End-To-End Memory Networks. *NeurIPS*.
12. Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention Is All You Need. *NeurIPS*.
13. Rae, J. W., Potapenko, A., Jayakumar, S. M., Hillier, C., & Lillicrap, T. P. (2020). Compressive Transformers for Long-Range Sequence Modelling. *ICLR*.
14. Wu, Y., Rabe, M. N., Hutchins, D., & Szegedy, C. (2022). Memorizing Transformers. *ICLR*.
15. Bulatov, A., Kuratov, Y., & Burtsev, M. S. (2022). Recurrent Memory Transformer. *NeurIPS*.
16. Schlag, I., Irie, K., & Schmidhuber, J. (2021). Linear Transformers Are Secretly Fast Weight Programmers. *ICML*.
17. Munkhdalai, T., Faruqui, M., & Gopal, S. (2024). Leave No Context Behind: Efficient Infinite Context Transformers with Infini-attention. *arXiv:2404.07143*.
18. Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., & Lewis, M. (2020). Generalization through Memorization: Nearest Neighbor Language Models. *ICLR*.
19. Packer, C., Wooders, S., Lin, K., et al. (2023). MemGPT: Towards LLMs as Operating Systems. *arXiv:2310.08560*.
20. Park, J. S., O'Brien, J. C., Cai, C. J., et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior. *UIST*.
21. Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. *NeurIPS*.
22. Kirkpatrick, J., Pascanu, R., Rabinowitz, N., et al. (2017). Overcoming catastrophic forgetting in neural networks. *PNAS*, 114(13), 3521–3526.
23. Parisi, G. I., Kemker, R., Part, J. L., Kanan, C., & Wermter, S. (2019). Continual lifelong learning with neural networks: A review. *Neural Networks*, 113, 54–71.
24. Hu, E. J., Shen, Y., Wallis, P., et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. *ICLR*.
25. Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *NeurIPS*.
26. Frantar, E., Ashkboos, S., Hoefler, T., & Alistarh, D. (2023). GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. *ICLR*.
27. Dettmers, T., Lewis, M., Belkada, Y., & Zettlemoyer, L. (2022). LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale. *NeurIPS*.
28. Malkov, Y. A., & Yashunin, D. A. (2020). Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. *IEEE TPAMI*, 42(4), 824–836.
29. Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data*, 7(3), 535–547.
30. Gemma Team (2024). Gemma: Open Models Based on Gemini Research and Technology. *arXiv:2403.08295*.
31. Gemma Team (2025). Gemma 3 Technical Report. *arXiv:2503.19786*.

---

## A note on vocabulary

This document uses a fixed vocabulary. *K* is the trained, frozen core. *Φ* is the memory: the accumulated traces and settings, data rather than a function. *A = (K, Φ)* is the product, one file. An *instance* is one PlastFormer with a fixed K and an accumulated Φ. The *engine* is the only external component, and it judges nothing about content. A *trace* is one record in Φ: a numeric payload, metadata, and an amplitude profile. A *position* is one hidden vector of 3840 numbers. A *tick* is lived time. The two registers are *Φ1* (perception, written involuntarily) and *Φ2* (explicit biographical records written by K). The seven acts are *name*, *repeat*, *connect*, *reconcile*, *read*, *scan*, and *calibrate*. *Silence* — an empty act block — is a valid choice. Words that are not in this list are not part of the design's working vocabulary.
