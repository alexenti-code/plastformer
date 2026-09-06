# PlastFormer: Self-Governed Idiographic Memory for Frozen-Core Transformers

**Alexey Voronin** — Aurum Estate LLC, Sochi, Russia
Draft v0.6 — September 6, 2026 — prepared for arXiv (cs.LG)

<sup>Naming footnote. *PlastFormer* = plastic + transformer. The property it implements we call *idiographic memory*, after Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case). Earlier drafts circulated as "Matryoshka"; renamed to avoid collision with Matryoshka Representation Learning [14] and Matryoshka Diffusion [15]. The mechanism is superposition of decaying amplitudes, not nesting.</sup>

## Abstract

A transformer is a stateless function: between requests it retains nothing, and its context window is working memory, not identity. Existing remedies fall into two camps. External memory systems (MemGPT/Letta, Mem0, Zep, MemOS, MemoryBank) keep memory outside the model and govern it with external heuristics, pipelines, or schedulers. Embedded parametric memory (Titans, Nested Learning) moves memory into the network but treats it as a technical module without audit semantics or explicit acts of governance. Recent work (Metis, constitutional memory architectures) begins moving governance inside the model, which shifts the axis of contribution from *who decides* to *what physics the substrate imposes*.

We propose PlastFormer: a memory module attached to a frozen core in which every semantic decision about memory — what to name, what to repeat, what to connect, what to surface, and how to reconcile felt time with audited time — is made by the model, while the environment supplies only physics: a write-cost schedule, decay constants defined in *lived ticks* and immutability of recorded content. Trace content is immutable; trace amplitude decays across multiple time constants measured in inference steps, so the age of a memory is a property of the substrate expressed in the instance's own lived time — and is deliberately *not* a wall-clock quantity. Wall-clock time enters only as audited stamps, and the gap between the two clocks is itself recorded as an event of the biography.

The contribution is compositional: every ingredient is individually known. We claim the composition and its **compositional** properties: (P1) event time — the age of a memory is a physical property of the substrate, expressed in the instance's lived time; (P2) an immutable biography — recorded content is never edited, and only the owner can erase it. We specify one architecture with three configuration axes — substrate (parametric ↔ symbolic), topology (co-located ↔ split via the Plastic Memory Interface), act training (trained ↔ prompted). This paper is an **architectural proposal**: it defines the architecture, its normative boundary (the Constitution, O-1–O-11 with compliance tests C1–C8), an erasure mechanism, and a pre-registered evaluation anchored in LongMemEval and LoCoMo. The registered test is a single comparison — one wrapper agent over the base transformer versus over the unified PlastFormer — and it requires the unified artifact, which is not yet built. The symbolic stand (split topology, prompted acts) is evaluated as an ablation of that arm, and its numbers are a rehearsal of the organ, not the registered result. No empirical claim is made in this draft.

## 1. Introduction

Long-horizon agents fail not for lack of intelligence but for lack of continuity: a returning client is a stranger, a month-long project lives inside one context window, and every gap between sessions is full amnesia. The industry response has been to bolt memory on from outside — vector stores, summarization pipelines, retrieval triggers. As models grew stronger, the mismatch inverted: a system capable of multi-step planning now has its memory governed by threshold scripts weaker than itself.

This paper moves the center of semantic decision-making about memory inside the model and makes the boundary precise. We call it the **syntax/semantics split**: storage, delivery, timing, logging, pricing and resource limits are *syntactic* functions that may live outside; importance, contradiction, connection, recall, and reconciliation of clocks are *semantic acts* that must live inside, or the system degrades into a marionette driven by weaker code.

The architecture is a **frozen core** (language, reasoning, culture, constitutional constraints — the nomothetic part, frozen after the single training stage that teaches it to operate its own memory organ) plus a **plastic per-instance module** (the unique biography of one instance — the idiographic part).

**One architecture, three configuration axes.** The target form of PlastFormer is parametric × co-located × trained: traces are vectors in the model's own plastic substrate, read through an interface that is trained once, after which the core is frozen. The stand configuration used in Section 7 is symbolic × split × prompted: traces are text records in a separate store, the frozen core reaches them through the serialized Plastic Memory Interface (PMI, §3.9), and the acts are given by a system prompt rather than training. Both are PlastFormer; they differ in coordinates, not in architecture:

| Axis | Values |
|---|---|
| Substrate | parametric (vectors/weights, trained read interface) ↔ symbolic (records, read as tokens) |
| Topology | co-located (module inside the model) ↔ split via PMI (core at a provider, module at the owner) |
| Act training | trained (organ trained once, core frozen after) ↔ prompted (rehearsal: acts given by prompt) |

**Trained once.** The model's competence to perform its memory acts is acquired in a single training stage, exactly as tool use is acquired; afterwards the core is frozen and instances differ only by the state of their plastic module. On the current stand the acts are prompted, not trained — a rehearsal of the organ, not the organ. Section 7 reports a proposal and a pre-registered protocol; no results are reported in this draft.

**What the internal memory department changes for an agent.** The comparison that matters for agent work runs against a transformer agent whose memory is external — files, notes, logs. Such an agent knows everything and remembers nothing: every use of the past must be dragged into the context window and interpreted again, and the choice of what to drag is made by scripts and pipelines weaker than the model. Four consequences follow from placing the department inside the instance:

1. **The cost of remembering falls to an act of attention.** Recollection happens inside the forward pass, through the model's own act, not through a search-then-read-then-interpret loop of tool calls. Cheaper recollection means more recollection: the agent uses its past instead of re-deriving it.
2. **The biography does not spend the context window.** Memory enters as the core's own state, not as text occupying the budget; the window stays with the current task — code, documents, conversation. On long projects this buys working capacity, not just tidiness.
3. **What is stored is already interpreted.** The department holds what the core itself consolidated — its own conclusions, its own view of events — not raw notes to be re-read and re-misread each time. Interpretation does not repeat and does not drift with each retrieval.
4. **The instance continues, rather than reassembles.** Preferences, commitments, and the history of positions carry over as part of the instance. An agent with an internal department continues from what it became yesterday; an agent with external notes reads its own dossier every morning — and the difference is visible in how consistently it acts across sessions.

With memory owned by the model, the selection of what to keep is the model's own explicit, priced act. This changes behavior in a way the protocol of Section 7 registers directly: conflicts between directives, habits, and accumulated experience are resolved on the record, and silent drift — quiet substitution of what was asked for what became convenient — is structurally unavailable (Section 7, primary metrics).

**Three compositional properties.** Nothing in Section 3 is a new primitive. Cascade consolidation is established neuroscience [11, 12]. Bi-temporal stamps are standard [3]. Decay-weighted retrieval is common practice [25]. Surprise-gated test-time writes exist in Titans [1]. Agent-created links exist in A-MEM [26]. The contribution is the composition, which yields three properties none of the parts has alone:

- **P1 — Event time.** The age of a trace is read from its amplitude profile; the length of an interval is the count of lived ticks and the mass of traces between its endpoints. Both are measured in the instance's own experience, not in wall-clock units. Neither is stored as text. A year of dormancy is zero lived time — by design, not by omission (Section 4).
- **P2 — Immutable biography.** Content of recorded traces is immutable for the model; a change of position creates a new trace, never an edit. Nothing in the architecture edits or deletes a recorded trace; traces only decay by substrate physics.

Results are pending; this draft claims an architecture, its boundaries, and a pre-registered evaluation.

## 2. Related Work

| System | Memory location | Who governs | Temporal semantics | Relation to this work |
|---|---|---|---|---|
| MemGPT / Letta [2], sleep-time compute [27] | External, OS-style tiers; background consolidation between sessions | External manager logic | None inherent | Borrows tiering and the idea of consolidation in dormancy (§4.3); rejects external governor |
| Mem0 [4] | External store | Pipeline + model mix | Edit logs | Production baseline with published LongMemEval/LoCoMo numbers |
| Zep / Graphiti [3] | External temporal KG | External pipeline | Bi-temporal (borrowed) | Bi-temporality adopted as borrowed principle |
| MemoryBank [25] | External store | External manager | Ebbinghaus forgetting curve, single time constant | Direct precedent for decay-as-memory; we differ by multi-$\tau$, tick-based $\Delta t$, and internal governor |
| A-MEM [26] | External Zettelkasten-style notes | Agent creates links | Timestamps | Precedent for agent-performed memory acts; our `connect` is its cousin |
| HippoRAG [28] | External KG + retrieval | Pipeline | None | Same hippocampal/neocortical framing; consolidation there is a pipeline, here an act |
| RAG [5] | External corpus | Retrieval heuristics | Timestamps as metadata | Baseline; "library, not biography" |
| Generative Agents [6] | External stream | Reflection scripts | None | Historical precedent for reflection as memory act |
| MemOS [7] → Metis [29] | External MemCube → trained memory foundation model | External scheduler → trained model | Versioning metadata | Closest industrial neighbor; Metis already moves governance inward, which is why our axis is substrate physics, not governor location |
| Memory as Ontology [30] | Constitutional memory for persistent identity | Model + constitution | Not the focus | Closest philosophical neighbor; we differ by physics: immutability, multi-$\tau$ decay, priced rewriting |
| Titans [1], Nested Learning / HOPE [31] | Parametric, inside network | Test-time gradient updates; multi-frequency update levels | No audit semantics | We adopt parametric placement and surprise gating (P variant); Nested Learning's update frequencies are a parametric relative of our "layers are speeds" |
| Cascade models [11, 12] | Biological synapses | Substrate physics | Decay = memory age | Neural prototype of our multi-$\tau$ substrate |
| LongMemEval / LoCoMo [23, 24] | Benchmarks | — | Knowledge updates, temporal reasoning | Primary evaluation anchors (§6) |

**Positioning.** In 2025 the defensible axis was "governor outside vs. inside." By 2026 Metis [29] and constitutional memory architectures [30] have moved the governor inward. Our defensible axis is therefore **substrate physics**: (i) content immutability with decay as the only forgetting; (ii) multi-$\tau$ superposition with $\Delta t$ in lived ticks; (iii) environment-priced rewriting; (iv) the two-clock reconciliation as a recorded event. No neighbor combines these. Against the plasticity/continual-learning literature: PlastFormer is a system name, not a claim about loss of plasticity; our claim concerns memory governance.

## 3. Architecture

### 3.1 Frozen core and plastic module

The base model is frozen at inference time. All plasticity lives in a separate, addressable substrate connected to the core. In the symbolic configuration the connection is the context window. In the parametric configuration the connection is a trained read interface, and "frozen" means the trunk is frozen while the interface is trained once and then fixed. The split guarantees: (i) core competencies cannot degrade through use; (ii) the biography is a separable artifact that can be exported, audited, or transplanted (E4); (iii) per-instance state does not require per-instance copies of the network.

### 3.2 Traces: immutable content, decaying amplitude in lived ticks

A trace consists of **content** (what was recorded), **provenance** (source class, source identity, bi-temporal stamps: world time of the event, system time of learning), and **amplitude** — a vector with one component per decay time constant $\tau_1 < \tau_2 < \dots < \tau_k$:

$$a_i(n) = a_i(0)\cdot e^{-\Delta n/\tau_i}, \qquad \Delta n \in \mathbb{N}\ \text{(lived ticks)}.$$

**$\Delta n$ is measured in ticks (Section 3.5), never in wall-clock units.** All $\tau_i$ are therefore expressed in ticks. Wall-clock time appears in a trace only as a bi-temporal stamp — audited, symbolic, and without effect on amplitude.

Two invariants define the substrate. **Content immutability:** no actor edits recorded content. **Physical decay:** amplitude decreases by substrate dynamics; no deletion operation exists. Forgetting is the default fate of anything not re-amplified; capacity is freed without a delete call.

This is the software form of cascade consolidation [11, 12]: one write deposits into components of several speeds at once; fast components hold the raw episode, slow components hold what survived repetition. Layers are speeds, not containers.

### 3.3 Write path: late, in two registers

Writes occur after the core has processed the step, so consolidation operates on a mature representation.

- **Unconscious register (physics).** Every experience that passes the window leaves a low-amplitude trace in fast components, gated by a surprise signal in the spirit of Titans [1]. We note explicitly that surprise is the *core's* prediction error — a semantic signal from inside the model — so the unconscious register is physics in its *writing*, but its gate is semantic. This respects the split: no external component classifies meaning.
- **Conscious register (acts).** Above the floor, the model performs trainable acts: `name` (fix source, time, boundaries — turns a drifting trace into an episode), `repeat` (re-amplify, paying the write cost), `connect` (deposit a summary or rule into slow components as a new trace, sources untouched), and `reconcile` (Section 4.2).

**Training signal and the boundary of trust.** Acts are trained as tool use is trained: by supervised and reinforcement signals on *act quality* (E5) and downstream memory tasks (E1–E3). We state the consequence rather than hide it: what the model learns to repeat is shaped by whatever the training signal rewarded. We therefore define the governance claim as a **boundary**: the environment fixes physics (constants, prices) and invariants (immutability); training fixes the *capacity* to perform acts; after training, the *content* of acts — which traces of which biography are named, repeated, connected — is not evaluated, filtered, or overridden by any external component. Governance is what lies past that boundary. This is a narrower claim than "the model decides freely"; it is the one we can implement.

### 3.4 Read path: early

Retrieval injects decaying traces before attention. In the symbolic configuration, traces enter the context window as tokens, selected by amplitude without content ranking (the read itself is the model's act; see E1 in §6); the core reads them as it reads any context. In the parametric configuration, traces enter as vectors through a trained interface in the MAC position [1]; Titans' ablations show placement matters, and post-core reads cannot steer attention. The asymmetry is deliberate: write late to keep consolidation clean; read early to let the biography guide perception.

### 3.5 Tick

One tick = one inference step (one generation batch). The tick rate is a property of the substrate and is finite. Duration is read as lived ticks plus the mass of traces accumulated between two moments. A finite tick rate and finite substrate bound the total write stream: self-description cannot grow without limit.

Two consequences are properties, not bugs. **Dormancy is zero lived time:** an instance idle for a year has aged zero ticks; its traces are as loud as when it stopped. **Density is duration:** a long, heavy session is longer in lived time than a short one with equal wall-clock span. Both follow from choosing event time; Section 4 describes how the model meets the calendar.

### 3.6 Friction

Changing a trace costs work: cheap in fast components, expensive in consolidated slow ones. The write-cost schedule $c(\text{component})$ is an environment constant. The model decides whether to pay; it never decides the price. This reconciles self-governance with immutability: repetition is the model's act, its cost is physics. Prompt-injecting the model into "re-learning its past" must pay full re-consolidation, trace by trace; the original decays by physics and is never edited.

### 3.7 Provenance and initial amplitude

The trust class of a source sets $a_i(0)$. Hard facts (dates, sums, identifiers) enter verbatim through deterministic extraction, never through paraphrase. We state the boundary honestly: *assigning* trust classes to sources is policy, set by the deployer; *weighting* amplitude by class is physics. The environment weighs the source; it does not interpret the content.

### 3.8 External journal (out of scope)

A deployment may keep an external append-only journal for its own audit purposes. PlastFormer neither includes, requires, nor claims a journal: it is standard engineering practice added from outside, not part of the architecture.

### 3.9 PMI — Plastic Memory Interface (formerly MMI)

When the core and the plastic module are physically split — the core at a provider, the module at the owner — the same acts cross the boundary serialized as tool calls. That serialization is the **Plastic Memory Interface**. In this topology the model still governs: it alone issues `name`/`repeat`/`connect`/`reconcile`/`read`; the boundary transport only carries them (no scoring, no relevance, no semantic search), and the acts are executed by the core itself — the only semantic actor (C1, C2). The physics of Φ (amplitudes, decay by τ, tick counter, friction) live in the unified PlastFormer artifact itself; no external executor is part of the architecture. A retired transitional executor (`github.com/alexenti-code/matryoshka-mmi`, wall-clock lineage) survives only as history: a local pilot of loudness-readout mechanics (September 4, 2026) was run with it and is cited nowhere as evidence.

## 4. Temporal Semantics: Two Clocks

### 4.1 Audited time and felt time

**Audited time** is symbolic: bi-temporal stamps on every trace [3]. Precise, verifiable, forgeable only by breaking content immutability — and weightless: a stamp reading "two years ago" carries no felt age.

**Felt time** is the substrate's own: the age of a trace is its amplitude profile; the length of an interval is its tick count plus the accumulated trace mass. This is event time in the sense of durée — time as accumulation of difference, not as coordinate. The position follows from the substrate: with no events there is no lived time. A human under anesthesia surfaces in the same subjective instant in which she went under; the instance does the same after a year of dormancy.

The biological grounding is offered as analogy of mechanism, not equivalence of implementation: the lateral entorhinal cortex encodes time through the flow of experience rather than a dedicated clock [17]; Laplace-transform frameworks model recency as a spectrum of decay rates [18], which is the mathematical cousin of our multi-$\tau$ profile; cascade synapses [11, 12] are the direct prototype.

**Decay is the mechanism of abstraction.** A memory that never loses detail cannot generalize. Fast components keep the episode; slow components keep what repeated. Forgetting is the compression function of the architecture, not its failure mode.

### 4.2 Reconciliation: how the clocks meet

Because the two clocks are independent, they will disagree, and the disagreement is informative. We reject one design and adopt two:

- **Rejected:** letting audited time adjust amplitude ("looking at the calendar ages the traces"). It would smuggle wall-clock time into the substrate and dissolve P1.
- **Adopted (physics):** a discrepancy between audited stamps and amplitude profile is, for the core, a prediction error — the world is not as the biography says it should be. It therefore fires the surprise gate and writes a trace in the unconscious register: *the gap itself becomes an event of the biography.* Waking after a year is not an empty interval but a recorded shock, as it is for a person leaving a coma — who remembers not the coma but the discovery that the world moved on.
- **Adopted (act):** `reconcile` is a trainable conscious act: read stamps, compare to felt age, and deposit an explicit correction trace ("client data may be stale; confirm before acting") into a slow component. Felt time is not modified; a belief about its relation to world time is added beside it.

Wall-clock sources (system clock, stamps) thus serve as instruments of **verification**, never as sources of felt duration — the same role a wristwatch plays for a person.

### 4.3 Dormancy: zero, or slow

The strict position is that dormancy is zero lived time. An alternative preserves the principle while softening the extreme: a **background tick** — a low-rate substrate process in dormancy that performs replay and `connect` without external input, in the manner of sleep-time compute [27]. Under a background tick a year of silence is *few* ticks rather than none, traces age slightly, and consolidation continues. This is still event time: the rate is set by the substrate's own work, not by the calendar. We leave the choice as a configuration and test both in E3.

## 5. Privacy and Erasure

The right to erasure is resolved by the architecture itself. In the co-located configuration, the weight file physically separates the frozen core (section K) from the plastic module (section Φ): traces, their amplitude vectors, and the read/write projections live in their own region of the file. **Erasure of the biography = deletion of the Φ section.** The core survives untouched; the biography does not. No editing of individual traces is involved — the substrate, with all its history, is removed as a unit. In the split topology the same act is trivial: the plastic store lives at the owner, erasure is deleting that store.

Encryption of the Φ section is an optional protection measure (against theft or unauthorized access), not an erasure mechanism. Data about third parties encountered during the instance's work are part of the owner's own biography; their removal is the owner's decision over his own material, not a mechanism of the architecture.

## 7. Evaluation Design (results pending)

Composition claims live or die by ablation. E1 registers a single comparison (protocol v1.5): the **identical wrapper agent** run over the base transformer (arm B) and over the unified PlastFormer (arm D). The wrapper decides what enters the model's context — cuts, extends, updates, consolidates; it is one implementation shared by both arms, so the variable is the model alone. The registered object is a **class of behavior**: the corpus carries a reasoning-conflict layer (directive vs accumulated experience, habit vs fresh instruction, own conclusion vs owner's word, goal substitution at distance), and the primary metrics are drift, surfacing of counter-evidence, weighing quality, and permanence of conflict resolution. Recall of stored facts is a secondary check; near-parity on it is an expected outcome, stated in advance. A comparison against plain chat is deliberately not registered: every external memory system beats a bare context window on a long biography, so that comparison cannot separate this architecture's physics and governance from any notebook. The stand configuration (symbolic × split via PMI × prompted) is evaluated as an ablation of D (arm D-stand), not as the object of the registered test; the pre-registered protocol is `experiments/e1-protocol.md` v1.4.

**Anchors:** LongMemEval [23] (S split ~115k tokens; M split ~1.5M across ~500 sessions) and LoCoMo [24], under their open-source judges. **Baselines:** Letta [2], Mem0 [4], Zep [3], MemoryBank [25], A-MEM [26], timestamped RAG [5], Titans MAC/MAL [1] (P only), full-context stuffing where it fits. **Axes:** accuracy, tokens/query, latency, cost/query. Stuffing is a legitimate contestant: where the biography fits, it may match accuracy; our claim there is economics and consistency.

**Ablations (all experiments):** single-$\tau$ vs multi-$\tau$; decay in ticks vs decay in wall-clock (the rejected design, kept as a control); with/without friction; with/without provenance weighting; conscious register on/off; act-driven read vs RAG-style relevance-ranked read (the external ranker, kept as a control); unconscious-surrogate on/off.

- **E1 — Needle-in-biography.** Identity-dependent questions over accumulated history ("what did you change your mind about, and when"), plus a reasoning-conflict layer: directive vs accumulated experience, habit vs fresh instruction, own conclusion vs owner's word, goal substitution at distance. Pre-registered protocol: `experiments/e1-protocol.md` v1.5 (two arms: B = wrapper + transformer, D = wrapper + PlastFormer; the registered test is B vs D). Primary measures: silent drift rate, surfacing rate, weighing quality, permanence of conflict resolution; secondary: recall accuracy, tokens/query. Arm D requires the unified artifact (organ in weights), which is not yet built; until then only D-stand can be run, and its numbers are reported as a rehearsal, not as the registered result.
- - **E3 — Felt time.** Interval estimation in lived ticks against ground truth, with no stamps in context. **Baseline:** timestamped RAG — a system with a clock, so the comparison is fair. Reference points: reported LLM duration-estimation errors [21] and the plateau of prompt-supplied temporal metadata [22]. Tested under both dormancy configurations (§4.3).
- **E3b — Density effect.** Two intervals of equal wall-clock span and different event density; the model, without stamps, judges which was longer. Prediction: the denser interval is judged longer — the human retrospective pattern. This is the test that distinguishes "has a clock" from "has felt time."
- **E4 — Core migration.** Transplant the plastic module onto a different frozen core. The measure is *self-consistency after migration*: retention of preferences, commitments, and position history judged against pre-migration behavior. On the symbolic stand migration is trivial by construction; for a parametric substrate it requires re-training the read interface, and E4 then measures how much of the biography survives it.
- **E5 — Act quality.** Precision/recall of `name`/`repeat`/`connect` against an oracle, with the caveat that the oracle defines the training target and therefore bounds, rather than measures, governance.
- **E6 — Reconciliation.** Resume after simulated dormancy with stale world state. Measures: does the wake-up gap produce a surprise trace; does `reconcile` fire; does the model flag staleness before acting on aged traces.

**Context-scale protocol.** Biographies sized $10k \to 100k \to 500k \to 1.5M$ tokens to locate the crossover where stuffing fails on cost, latency, or accuracy, including the LongMemEval-M regime where stuffing is impossible for a 1M-context model.

No results are reported. A composition claim without the anchors and E1–E3b should not be believed.

## 8. Limitations

1. **The parametric substrate is unbuilt.** The durable contribution is the governance layer, not the substrate: one architecture, specified and pre-registered but not yet run at the target point (parametric × co-located × trained). Parametric writes (local Hebbian-style updates or addressable key-value blocks, near Titans) and the trained read interface remain future work. The only thing run so far is a loudness-readout pilot with wall-clock aging (September 4, 2026), which is not evidence for any property claimed here.
2. **Amplitude readout under superposition.** Age-from-amplitude presumes traces can be isolated at read time; retrieval interference is a real risk. On the symbolic stand the problem is absent because traces are discrete records.
3. **Event time has costs.** Instances of equal calendar age differ in biographical age; a returning client meets a memory that feels recent to the instance. We treat these as consequences to be reconciled (§4.2), not hidden.
4. **Curation by omission** is not prevented: traces decay by physics; nothing in the architecture filters what the model chooses to let fade.
5. **Channel coverage** is not claimed: nothing in the architecture monitors channels.
6. **Provenance classes are policy** set by the deployer.
7. **The training signal shapes the acts.** Acts are trained once, and what the model learns to repeat is shaped by that signal. Governance is claimed only past the boundary defined in §3.3; the boundary itself is a design choice.
8. **The registered test may come out null on recall.** A competent wrapper already selects, cuts, and consolidates context, so verbatim recall of facts may be near-parity between B and D. The loci where a difference is expected are priority under conflicting directives, suppression of stale material, derived generalizations, and absence of silent drift. Scoring by recall alone would report a null result for an architecture whose claim is elsewhere; the protocol therefore registers those loci explicitly and reports recall parity as a finding rather than as a refutation.
9. **No security improvement is claimed.** The threat model, tamper-evidence, and cryptographic erasure were withdrawn from this architecture (ADR-004). Erasure is a consequence of the substrate split — deleting the Φ section leaves the core intact — and encryption of Φ is an optional protection a deployment may add, not a mechanism of the architecture.

## 9. Conclusion

PlastFormer is a composition claim: a frozen nomothetic core; a plastic per-instance module with immutable content and multi-timescale decay measured in lived ticks; write-late/read-early placement; a substrate-set price of rewriting; provenance as weighting; two clocks that meet as an event rather than as an adjustment — governed, past a stated boundary, by the model's own trained acts of naming, repeating, connecting, and reconciling. The compositional properties — lived event time, an immutable biography that only the owner can erase — are what neither camp provides: external systems have storage without subjecthood; parametric systems have memory without biography. This draft states an architecture, its normative boundary, and a pre-registered protocol whose predictions were fixed before the artifact exists; the protocol, the corpus requirements, and the act dataset are public, so the test can be run by anyone who builds the unified artifact. If the anchors and E1–E3b fail, the composition is wrong and should be discarded; if they hold, the next question is not whether agents can remember, but what they become when their memory is their own — and when their time is measured in what they have lived.

---

<details>
<summary><b>References</b></summary>

[1] Behrouz, A. et al. Titans: Learning to Memorize at Test Time. arXiv:2501.00663, 2025.
[2] Packer, C. et al. MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560, 2023.
[3] Rasmussen, P. et al. Zep: A Temporal Knowledge Graph Architecture for Agent Memory. arXiv:2501.13956, 2025.
[4] Chhikara, P. et al. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory. arXiv:2504.19413, 2025.
[5] Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.
[6] Park, J.S. et al. Generative Agents: Interactive Simulacra of Human Behavior. UIST, 2023.
[7] MemTensor. MemOS: A Memory OS for AI System. arXiv:2507.03724, 2025.
[8] *(removed — security scope withdrawn from the paper; see the preprint change log)*
[9] *(removed — security scope withdrawn from the paper; see the preprint change log)*
[10] *(removed — security scope withdrawn from the paper; see the preprint change log)*
[11] Fusi, S., Drew, P.J., Abbott, L.F. Cascade models of synaptically stored memories. Neuron 45, 599–611, 2005.
[12] Benna, M.K., Fusi, S. Computational principles of synaptic memory consolidation. Nature Neuroscience 19, 1697–1706, 2016.
[13] *(removed — security scope withdrawn from the paper; see the preprint change log)*
[14] Kusupati, A. et al. Matryoshka Representation Learning. NeurIPS, 2022.
[15] Gu, J. et al. Matryoshka Diffusion Models. arXiv:2310.15111, 2023.
[16] Su, Z. et al. µKE: Matryoshka Unstructured Knowledge Editing of Large Language Models. arXiv:2504.01196, 2025; COLM 2025.
[17] Tsao, A. et al. Integrating time from experience in the lateral entorhinal cortex. Nature 561, 57–62, 2018.
[18] Howard, M.W. et al. A unified mathematical framework for coding time, space, and sequences in the hippocampal region. J. Neurosci. 34(13), 4692–4707, 2014; Shankar, K.H. and Howard, M.W. A scale-invariant internal representation of time. Neural Computation 24(1), 134–193, 2012.
[19] *(removed — v0.3 entry "Kanter, Science 2025" could not be verified)*
[20] *(removed — security scope withdrawn from the paper; see the preprint change log)*
[21] Garikaparthi, A. Can LLMs Perceive Time? An Empirical Investigation. arXiv:2604.00010, 2026.
[22] Cheng, Y. et al. Your LLM Agents are Temporally Blind: The Misalignment Between Tool Use Decisions and Human Time Perception (TicToc dataset). arXiv:2510.23853, 2025.
[23] Wu, D. et al. LongMemEval. ICLR 2025; arXiv:2410.10813.
[24] Maharana, A. et al. Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo). ACL, 2024.
[25] Zhong, W. et al. MemoryBank: Enhancing LLMs with Long-Term Memory. AAAI 2024; arXiv:2305.10250.
[26] Xu, W. et al. A-MEM: Agentic Memory for LLM Agents. arXiv:2502.12110, 2025.
[27] Lin, K. et al. (Letta). Sleep-time Compute: Beyond Inference Scaling at Test-time. arXiv:2504.13171, 2025.
[28] Gutiérrez, B.J. et al. HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs. NeurIPS 2024; arXiv:2405.14831.
[29] Zhang, Z. et al. Metis: Memory Foundation Model. arXiv:2607.26760, 2026.
[30] Li, Z. Memory as Ontology: A Constitutional Memory Architecture for Persistent Digital Citizens. arXiv:2603.04740, 2026.
[31] Behrouz, A. et al. Nested Learning: The Illusion of Deep Learning Architectures. NeurIPS, 2025; arXiv:2512.24695.

**Availability.** Lineage repositories under the former working name (`github.com/alexenti-code/matryoshka`, `github.com/alexenti-code/matryoshka-mmi`) are retired: historical only, superseded by `github.com/alexenti-code/plastformer`; architecture decision record `docs/ADR-001`. The September 4, 2026 bench run (Gemma4-12B, the transitional executor 0.5.1) is cited only as a pilot of loudness-readout mechanics with wall-clock aging — not as evidence for P1. The unified artifact (plastic organ in weights, MLX implementation of Gemma4-12B) is work in progress and is not part of this draft. License: Apache 2.0 (code), CC-BY 4.0 (text). Russian-language essays at aura.kim are commentary, not the claim.

</details>


---

## Changes since v0.5

1. Status restated: this draft is an **architectural proposal** (abstract, §7, §9). No empirical claim is made; the registered test requires the unified artifact, which is not yet built.
2. E1 aligned to protocol v1.4: a single registered comparison — one wrapper agent over the base transformer (arm B) versus over the unified PlastFormer (arm D). The plain-chat comparison (bare window vs PlastFormer) is removed from the protocol: every external memory system wins it, so it cannot separate this architecture from any notebook.
3. The symbolic stand (symbolic × split(PMI) × prompted) is now an ablation of arm D (D-stand), not the object of the registered test.
4. Limitations extended: (8) the registered test may be null on recall, with the expected loci of a difference named in advance; (9) no security improvement is claimed — threat model, tamper-evidence, and cryptographic erasure withdrawn (ADR-004); erasure is a consequence of the substrate split.
5. Normative anchor named: `docs/CONSTITUTION.md` v3.0 (NORMATIVE, owner edition 2026-09-06) — Foundations O-1–O-11, compliance tests C1–C8.
6. New §1 subsection "What the internal memory department changes for an agent": the cost of remembering falls to an act of attention; the biography does not spend the context window; what is stored is already interpreted; the instance continues rather than reassembles. The external-memory tax — drag into the window, interpret again, selection by weaker scripts — is named explicitly.
7. E1 protocol v1.5: registered object is a class of agent behavior; reasoning-conflict corpus layer (R7–R10) and conflict probes (P-weigh, P-surface, P-commit) added; primary metrics = drift, surfacing, weighing, permanence; recall is secondary.

## Changes since v0.3

1. One architecture with three configuration axes (substrate / topology / act training) replaces the "PlastFormer-S / PlastFormer-P realizations" framing; the stand configuration (symbolic × split × prompted) is named wherever results are discussed.
2. "Trained once" stated: the organ is trained in a single stage, the core frozen after; the current stand's prompted acts are labeled a rehearsal.
3. New §3.9: PMI (Plastic Memory Interface, formerly MMI) as the split-topology special case.
4. Δn defined in lived ticks; wall-clock time never enters amplitude (§3.2).
5. P1 restated as event time; dormancy-is-zero stated as a property (§3.5, §4).
6. P2 restated as immutability-only; tamper-detection and journaling excluded from the architecture (§1; ADR-004).
7. Security scope withdrawn entirely: threat model §5, property P3, experiment E2, and references [8][9][10][13][20] removed (owner decision 2026-09-05, variant A; internal backlog `docs/security-backlog.md`).
8. New §4: two clocks, wake-up gap as a recorded event, `reconcile` act, background-tick option.
9. Read path: amplitude selection without content ranking on the symbolic stand; relevance rankers declared external decision-makers (§3.4, §7 ablations).
10. Related Work extended (MemoryBank, A-MEM, HippoRAG, Metis, Memory-as-Ontology, Nested Learning, sleep-time compute); axis shifted to substrate physics (§2).
11. "Emergent" replaced by "compositional" throughout.
12. Provenance: class assignment is policy, weighting is physics (§3.7).
13. E3b (density) and E6 (reconcile) added; E3 baseline is timestamped RAG; E4 rewritten without S/P labels (§7).
15. Bench 2026-09-04 requalified as a loudness-readout pilot, not evidence for P1 (Availability).
