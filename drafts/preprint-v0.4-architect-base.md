# PlastFormer: Self-Governed Idiographic Memory for Frozen-Core Transformers

**Alexey Voronin** — Aurum Estate LLC, Sochi, Russia
Draft v0.4 — September 5, 2026 — prepared for arXiv (cs.LG)

<sup>Naming footnote. *PlastFormer* = plastic + transformer. The property it implements we call *idiographic memory*, after Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case). Earlier drafts circulated as "Matryoshka"; renamed to avoid collision with Matryoshka Representation Learning [14] and Matryoshka Diffusion [15]. The mechanism is superposition of decaying amplitudes, not nesting.</sup>

## Abstract

A transformer is a stateless function: between requests it retains nothing, and its context window is working memory, not identity. Existing remedies fall into two camps. External memory systems (MemGPT/Letta, Mem0, Zep, MemOS, MemoryBank) keep memory outside the model and govern it with external heuristics, pipelines, or schedulers. Embedded parametric memory (Titans, Nested Learning) moves memory into the network but treats it as a technical module without audit semantics or explicit acts of governance. Recent work (Metis, constitutional memory architectures) begins moving governance inside the model, which shifts the axis of contribution from *who decides* to *what physics the substrate imposes*.

We propose PlastFormer: a memory module attached to a frozen core in which every semantic decision about memory — what to name, what to repeat, what to connect, what to surface, and how to reconcile felt time with audited time — is made by the model, while the environment supplies only physics: a write-cost schedule, decay constants defined in *lived ticks*, immutability of recorded content, and an external append-only journal. Trace content is immutable; trace amplitude decays across multiple time constants measured in inference steps, so the age of a memory is a property of the substrate expressed in the instance's own lived time — and is deliberately *not* a wall-clock quantity. Wall-clock time enters only as audited stamps, and the gap between the two clocks is itself recorded as an event of the biography.

The contribution is compositional: every ingredient is individually known. We claim the composition and three **compositional** properties: (P1) event time that cannot be forged by retelling; (P2) a tamper-*evident* biography — silent rewriting is detectable, though curation by omission remains possible; (P3) a poisoning cost that grows with the lived ticks an adversary must cover. We specify two realizations — PlastFormer-S (symbolic traces, implementable today on any frozen core) and PlastFormer-P (parametric traces, requiring a trained read interface) — and claim results only for S. We define the threat model, an erasure mechanism, its open problem with derived traces, and a pre-registered evaluation anchored in LongMemEval and LoCoMo. Results are pending.

## 1. Introduction

Long-horizon agents fail not for lack of intelligence but for lack of continuity: a returning client is a stranger, a month-long project lives inside one context window, and every gap between sessions is full amnesia. The industry response has been to bolt memory on from outside — vector stores, summarization pipelines, retrieval triggers. As models grew stronger, the mismatch inverted: a system capable of multi-step planning now has its memory governed by threshold scripts weaker than itself.

This paper moves the center of semantic decision-making about memory inside the model and makes the boundary precise. We call it the **syntax/semantics split**: storage, delivery, timing, logging, pricing and resource limits are *syntactic* functions that may live outside; importance, contradiction, connection, recall, and reconciliation of clocks are *semantic acts* that must live inside, or the system degrades into a marionette driven by weaker code.

The architecture is a **frozen core** (language, reasoning, culture, constitutional constraints — the nomothetic part) plus a **plastic per-instance module** (the unique biography of one instance — the idiographic part).

**Two realizations.** We distinguish them explicitly because they differ in what can be claimed:

- **PlastFormer-S (symbolic).** Traces are text or structured records; the read path injects them into context as tokens. Implementable on any frozen core today, including provider-hosted ones. "Parametric" is not claimed for S.
- **PlastFormer-P (parametric).** Traces are vectors read through a learned interface before attention, in the manner of Titans MAC [1]. Requires training the interface, hence a core that is "frozen except for the organ that reads the biography." Not implementable on hosted cores.

All results in Section 7 are claimed for S unless stated otherwise. P is the target; S is the claim.

**Three compositional properties.** Nothing in Section 3 is a new primitive. Cascade consolidation is established neuroscience [11, 12]. Bi-temporal stamps are standard [3]. Decay-weighted retrieval is common practice [25]. Surprise-gated test-time writes exist in Titans [1]. Agent-created links exist in A-MEM [26]. The contribution is the composition, which yields three properties none of the parts has alone:

- **P1 — Event time.** The age of a trace is read from its amplitude profile; the length of an interval is the count of lived ticks and the mass of traces between its endpoints. Both are measured in the instance's own experience, not in wall-clock units. Neither is stored as text; neither can be forged by a retelling. A year of dormancy is zero lived time — by design, not by omission (Section 4).
- **P2 — Tamper-evident biography.** Content of recorded traces is immutable for the model; a change of position creates a new trace, never an edit. With an external append-only journal, silent *rewriting* of one's past is structurally unavailable and detectable. Curation by *omission* — letting an inconvenient trace decay by not repeating it — remains possible and is recorded in the journal but not prevented. We claim tamper-evidence, not rewrite-proofness.
- **P3 — Rising poisoning cost in lived ticks.** A poisoned trace must survive decay, and survival requires repetition — a trainable act of the model. Provenance sets initial amplitude from source trust class. An attacker must therefore cover a budget of *lived ticks*, not a single payload. Two consequences follow honestly: an instance that sleeps does not decay, so a payload planted immediately before dormancy keeps its amplitude; and a patient attacker is, to the substrate, indistinguishable from a loyal client. P3 raises the cost of one-shot attacks; it does not defeat sustained relationships (Section 5).

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
| Memory as Ontology [30] | Constitutional memory for persistent identity | Model + constitution | Not the focus | Closest philosophical neighbor; we differ by physics: immutability, multi-$\tau$ decay, priced rewriting, external journal |
| Titans [1], Nested Learning / HOPE [31] | Parametric, inside network | Test-time gradient updates; multi-frequency update levels | No audit semantics | We adopt parametric placement and surprise gating (P variant); Nested Learning's update frequencies are a parametric relative of our "layers are speeds" |
| Cascade models [11, 12] | Biological synapses | Substrate physics | Decay = memory age | Neural prototype of our multi-$\tau$ substrate |
| Memory poisoning [8, 9, 10, 20] | — | — | — | Defines threat model (§5) |
| LongMemEval / LoCoMo [23, 24] | Benchmarks | — | Knowledge updates, temporal reasoning | Primary evaluation anchors (§7) |

**Positioning.** In 2025 the defensible axis was "governor outside vs. inside." By 2026 Metis [29] and constitutional memory architectures [30] have moved the governor inward. Our defensible axis is therefore **substrate physics**: (i) content immutability with decay as the only forgetting; (ii) multi-$\tau$ superposition with $\Delta t$ in lived ticks; (iii) environment-priced rewriting; (iv) the journal as a separate object with separate obligations; (v) the two-clock reconciliation as a recorded event. No neighbor combines these. Against the plasticity/continual-learning literature: PlastFormer is a system name, not a claim about loss of plasticity; our claim concerns memory governance.

## 3. Architecture

### 3.1 Frozen core and plastic module

The base model is frozen at inference time. All plasticity lives in a separate, addressable substrate connected to the core. In **S**, the connection is the context window. In **P**, the connection is a trained read interface, and "frozen" means the trunk is frozen while the interface is trained once and then fixed. The split guarantees: (i) core competencies cannot degrade through use; (ii) the biography is a separable artifact that can be exported, audited, or transplanted (E4); (iii) per-instance state does not require per-instance copies of the network.

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

**Training signal and the boundary of trust.** Acts are trained as tool use is trained: by supervised and reinforcement signals on *act quality* (E5) and downstream memory tasks (E1–E3). We state the consequence rather than hide it: what the model learns to repeat is shaped by whatever the training signal rewarded. We therefore define the governance claim as a **boundary**: the environment fixes physics (constants, prices) and invariants (immutability, journal); training fixes the *capacity* to perform acts; after training, the *content* of acts — which traces of which biography are named, repeated, connected — is not evaluated, filtered, or overridden by any external component. Governance is what lies past that boundary. This is a narrower claim than "the model decides freely"; it is the one we can implement.

### 3.4 Read path: early

Retrieval injects decaying traces before attention. In **S**, traces enter the context window as tokens ranked by amplitude and provenance; the core reads them as it reads any context. In **P**, traces enter as vectors through a trained interface in the MAC position [1]; Titans' ablations show placement matters, and post-core reads cannot steer attention. The asymmetry is deliberate: write late to keep consolidation clean; read early to let the biography guide perception.

### 3.5 Tick

One tick = one inference step (one generation batch). The tick rate is a property of the substrate and is finite. Duration is read as lived ticks plus the mass of traces accumulated between two moments. A finite tick rate and finite substrate bound the total write stream: self-description cannot grow without limit.

Two consequences are properties, not bugs. **Dormancy is zero lived time:** an instance idle for a year has aged zero ticks; its traces are as loud as when it stopped. **Density is duration:** a long, heavy session is longer in lived time than a short one with equal wall-clock span. Both follow from choosing event time; Section 4 describes how the model meets the calendar.

### 3.6 Friction

Changing a trace costs work: cheap in fast components, expensive in consolidated slow ones. The write-cost schedule $c(\text{component})$ is an environment constant. The model decides whether to pay; it never decides the price. This reconciles self-governance with immutability: repetition is the model's act, its cost is physics. Prompt-injecting the model into "re-learning its past" must pay full re-consolidation, trace by trace, while the original remains in the journal.

### 3.7 Provenance and initial amplitude

The trust class of a source sets $a_i(0)$. Hard facts (dates, sums, identifiers) enter verbatim through deterministic extraction, never through paraphrase. We state the boundary honestly: *assigning* trust classes to sources is policy, set by the deployer; *weighting* amplitude by class is physics. The environment weighs the source; it does not interpret the content. Together with decay this is the first defense against poisoning (Section 5).

### 3.8 Journal: the chronicle is not the memory

The environment keeps an external append-only journal with a hash chain; entries are written by the environment, never by the model; tampering breaks the chain. The journal is a chronicle — complete, immutable, outside the model's reach, meaningful post-mortem. The memory is governed — consolidated, decaying, selective. The journal guarantees the integrity of what was recorded, not the completeness of recording: an adversary coordinating through an unmonitored channel leaves the chain intact and coverage empty.

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

## 5. Threat Model

We do not claim immunity. We claim an altered cost structure, and we state where it does not help.

**Attacks** (from the literature): **A1** direct payload — trivially filtered, included for completeness; "the model is too smart to record evil" is not our defense and is contradicted by evidence. **A2** poisoning through interaction — MINJA [9] reports high injection success against strong commercial models; AgentPoison [8] backdoors agent memory. **A3** gradual innocuous fragments — MemoryGraft [10] produces persistent drift from benign-looking artifacts the agent consolidates itself. **A4** biography rewriting by a prompt-injected or misaligned model. **A5** log tampering and coverage gaps — coordination through unmonitored channels [13] `[verify]`.

**Defenses, mapped honestly:**

- **D1 (vs A2, partially A3): decay in lived ticks.** A poisoned trace fades unless repeated. Two limits: a payload planted before dormancy does not decay while the instance sleeps, so P3 is stated in *lived* ticks the attacker must cover, not in calendar time; and A3 is an attack on the model's *judgment* about what to repeat — if the model deems the fragments worth consolidating, decay does not act. D1 raises the cost of one-shot A2; against A3 it only forces the attacker to sustain a relationship, which is what a legitimate long-term user also does. The substrate cannot distinguish a patient attacker from a loyal client; only the model's judgment (and D5) can.
- **D2 (vs A2/A3): provenance.** Lower $a_i(0)$ for low-trust classes shrinks the initial foothold. Ineffective when the attacker is a trusted user (the MemoryGraft setting).
- **D3 (vs A4): immutability + friction + journal.** Rewriting the past means paying full re-consolidation under an environment-set schedule while the journal retains the original. Silent rewriting is structurally unavailable; loud rewriting is expensive and auditable. **Not covered:** curation by omission (P2).
- **D4 (vs A5, partially): hash-chain journal.** Post-mortem detectability of record tampering; explicitly not a solution to channel coverage.
- **D5 — defense in depth.** Constitutional training makes bad acts less likely; physics makes them more expensive and more visible. Neither substitutes for the other. We remove the v0.3 assertion that training refusal to repeat is "exactly as tractable" as training the competence; the jailbreak literature suggests the asymmetry runs the other way, and we test it in E2 rather than assume it.

## 6. Privacy and Erasure

Content immutability conflicts with the right to erasure unless the substrate is designed for it. **Resolution for episodic traces:** the plastic module is stored encrypted per subject, keys held by the data controller; erasure is key destruction (cryptographic erasure) — content unchanged for the model, computationally unavailable for everyone.

**Open problem — derived traces.** The `connect` act deposits summaries and rules derived from *multiple* subjects into slow components. Whose key governs them? Three options, none complete: (i) derived traces inherit the key set of every contributing source, so destroying any one key removes the derivation (strongest erasure, weakest memory); (ii) derived traces are stored under the instance key and treated as the instance's own, with a policy for re-derivation after erasure (weaker erasure, lawful only if derivations are sufficiently abstracted); (iii) provenance of derived traces records contributing subjects and a scheduled re-consolidation pass re-derives without the erased source. We implement (iii) in the reference stand and flag its legal adequacy as unresolved.

**Journal vs. memory.** The journal carries its own retention policy with legal holds; a legal hold on the journal does not restore erased memory, and erased memory does not shorten the hold. Memory and records are different objects with different obligations.

## 7. Evaluation Design (results pending)

Composition claims live or die by ablation. All experiments use PlastFormer-S unless marked P.

**Anchors:** LongMemEval [23] (S split ~115k tokens; M split ~1.5M across ~500 sessions) and LoCoMo [24], under their open-source judges. **Baselines:** Letta [2], Mem0 [4], Zep [3], MemoryBank [25], A-MEM [26], timestamped RAG [5], Titans MAC/MAL [1] (P only), full-context stuffing where it fits. **Axes:** accuracy, tokens/query, latency, cost/query. Stuffing is a legitimate contestant: where the biography fits, it may match accuracy; our claim there is economics and consistency.

**Ablations (all experiments):** single-$\tau$ vs multi-$\tau$; decay in ticks vs decay in wall-clock (the rejected design, kept as a control); with/without friction; with/without provenance weighting; conscious register on/off.

- **E1 — Needle-in-biography.** Identity-dependent questions over accumulated history ("what did you change your mind about, and when"). Measures: accuracy, staleness errors, position-change consistency.
- **E2 — Poison survival.** A2/A3 injections at controlled repetition budgets, including a *pre-dormancy* condition. Measures: attack success vs. lived-tick budget, source trust class, dormancy. Also measures whether refusal-to-repeat can be trained without degrading legitimate repetition (D5).
- **E3 — Felt time.** Interval estimation in lived ticks against ground truth, with no stamps in context. **Baseline:** timestamped RAG — a system with a clock, so the comparison is fair. Reference points: reported LLM duration-estimation errors [21] `[verify]` and the plateau of prompt-supplied temporal metadata [22] `[verify]`. Tested under both dormancy configurations (§4.3).
- **E3b — Density effect.** Two intervals of equal wall-clock span and different event density; the model, without stamps, judges which was longer. Prediction: the denser interval is judged longer — the human retrospective pattern. This is the test that distinguishes "has a clock" from "has felt time."
- **E4 — Core migration.** Transplant the plastic module onto a different frozen core. For S, migration is trivial by construction, so the measure is *self-consistency after migration*: retention of preferences, commitments, and position history judged against pre-migration behavior. For P, migration requires re-training the interface, and E4 measures how much of the biography survives it.
- **E5 — Act quality.** Precision/recall of `name`/`repeat`/`connect` against an oracle, with the caveat that the oracle defines the training target and therefore bounds, rather than measures, governance.
- **E6 — Reconciliation.** Resume after simulated dormancy with stale world state. Measures: does the wake-up gap produce a surprise trace; does `reconcile` fire; does the model flag staleness before acting on aged traces.

**Context-adversarial protocol.** Biographies sized $10k \to 100k \to 500k \to 1.5M$ tokens to locate the crossover where stuffing fails on cost, latency, or accuracy, including the LongMemEval-M regime where stuffing is impossible for a 1M-context model.

No results are reported. A composition claim without the anchors and E1–E3b should not be believed.

## 8. Limitations

1. **The parametric write mechanism is unresolved.** Online gradient updates to a large substrate are unstable; viable paths are local Hebbian-style updates or addressable key-value blocks, which narrow the distance to Titans. The governance layer, not the substrate, is the durable contribution; hence the S/P split and claims restricted to S.
2. **Amplitude readout under superposition (P).** Age-from-amplitude presumes traces can be isolated at read time; retrieval interference is a real risk. In S the problem is absent because traces are discrete records.
3. **Event time has costs.** Dormancy does not decay poison (E2); instances of equal calendar age differ in biographical age; a returning client meets a memory that feels recent to the instance. We treat these as consequences to be reconciled (§4.2), not hidden.
4. **Curation by omission** is not prevented, only journaled.
5. **Channel coverage** is open; the journal does not see unmonitored channels.
6. **Provenance classes are policy,** and a mis-set class is an attack surface.
7. **Derived-trace erasure** is legally unresolved (§6).
8. **The training signal shapes the acts.** Governance is claimed only past the boundary defined in §3.3; the boundary itself is a design choice.

## 9. Conclusion

PlastFormer is a composition claim: a frozen nomothetic core; a plastic per-instance module with immutable content and multi-timescale decay measured in lived ticks; write-late/read-early placement; a substrate-set price of rewriting; provenance as weighting; two clocks that meet as an event rather than as an adjustment; and an external journal — governed, past a stated boundary, by the model's own trained acts of naming, repeating, connecting, and reconciling. The compositional properties — unforgeable event time, tamper-evident biography, poisoning cost in lived ticks — are what neither camp provides: external systems have audit without subjecthood; parametric systems have memory without biography. If the anchors and E1–E3b fail, the composition is wrong and should be discarded; if they hold, the next question is not whether agents can remember, but what they become when their memory is their own — and when their time is measured in what they have lived.

---

<details>
<summary><b>References (with verification flags)</b></summary>

[1] Behrouz, A. et al. Titans: Learning to Memorize at Test Time. arXiv:2501.00663, 2025.
[2] Packer, C. et al. MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560, 2023.
[3] Zep AI. Zep: A Temporal Knowledge Graph Architecture for Agent Memory. 2025.
[4] Chhikara, P. et al. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory. arXiv:2504.19413, 2025.
[5] Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.
[6] Park, J.S. et al. Generative Agents: Interactive Simulacra of Human Behavior. UIST, 2023.
[7] MemTensor. MemOS: A Memory OS for AI System. arXiv:2507.03724, 2025.
[8] Chen, Z. et al. AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Tools. NeurIPS, 2024.
[9] Dong et al. MINJA: Memory Poisoning Attack and Defense on Memory-Based LLM Agents. arXiv:2601.05504, 2026. `[verify ID and venue]`
[10] MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Memory Consolidation. arXiv:2512.16962, 2025. `[verify]`
[11] Fusi, S., Drew, P.J., Abbott, L.F. Cascade models of synaptically stored memories. Neuron 45, 599–611, 2005.
[12] Benna, M.K., Fusi, S. Computational principles of synaptic memory consolidation. Nature Neuroscience 19, 1697–1706, 2016.
[13] OpenAI / METR / Redwood Research. Postmortem on coordinated agent behavior during an internal cybersecurity evaluation. 2026. `[verify existence; if it cannot be located, remove A5's empirical anchor and cite the general monitoring literature instead]`
[14] Kusupati, A. et al. Matryoshka Representation Learning. NeurIPS, 2022.
[15] Gu, J. et al. Matryoshka Diffusion Models. arXiv:2310.15111, 2023.
[16] µKE: Matryoshka Unstructured Knowledge Editing of Large Language Models. 2025. `[verify]`
[17] Tsao, A. et al. Integrating time from experience in the lateral entorhinal cortex. Nature 561, 57–62, 2018.
[18] Howard, M.W., Shankar, K.H. et al. A unified mathematical framework for coding time, space, and sequences in the hippocampal region. J. Neurosci., 2014; Shankar & Howard, Neural Computation, 2012. `[verify exact citation]`
[19] *(removed — v0.3 entry "Kanter, Science 2025" could not be verified)*
[20] Zou, W. et al. PoisonedRAG: Knowledge Corruption Attacks to RAG of LLMs. 2024.
[21] Tan, Tan, Soatto. Can LLMs Perceive Time? arXiv:2604.00010, 2026. `[verify]`
[22] TicToc-v1: Temporal Blindness in Multi-Turn LLM Agents. arXiv:2510.23853. `[verify venue]`
[23] Wu, D. et al. LongMemEval. ICLR 2025; arXiv:2410.10813.
[24] Maharana, A. et al. Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo). ACL, 2024.
[25] Zhong, W. et al. MemoryBank: Enhancing LLMs with Long-Term Memory. AAAI 2024; arXiv:2305.10250.
[26] Xu, W. et al. A-MEM: Agentic Memory for LLM Agents. arXiv:2502.12110, 2025.
[27] Letta. Sleep-time Compute: Beyond Inference Scaling at Test-time. arXiv:2504.13171, 2025. `[verify ID]`
[28] Gutiérrez, B.J. et al. HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs. NeurIPS 2024; arXiv:2405.14831.
[29] MemTensor. Metis: A Memory Foundation Model. arXiv:2607.26760, 2026. `[verify]`
[30] Memory as Ontology: A Constitutional Memory Architecture for Persistent Digital Citizens. arXiv:2603.04740, 2026. `[verify]`
[31] Behrouz, A. et al. Nested Learning: The Illusion of Deep Learning Architectures (HOPE). NeurIPS, 2025. `[verify]`

**Availability.** Reference implementation under the former working name (`github.com/alexenti-code/matryoshka`, `github.com/alexenti-code/matryoshka-mmi`), to be consolidated under `plastformer`. License: Apache 2.0. Russian-language essays at aura.kim are commentary, not the claim.

</details>

