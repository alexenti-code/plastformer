# PlastFormer: Self-Governed Idiographic Memory for Frozen-Core Transformers

**Alexey Voronin**
Aurum Estate LLC — Sochi, Russia
Draft v0.3 — September 4, 2026 — prepared for arXiv (cs.LG)

> **Naming note.** The system is named **PlastFormer** (plastic + transformer). The property it implements we call **idiographic memory**, after Windelband's nomothetic/idiographic distinction: a frozen nomothetic core (general laws) plus a plastic per-instance biography (the singular case). Brand in the title, concept in the subtitle — the pattern of MemGPT and Titans. Formerly circulated under the working name "Matryoshka"; renamed due to collisions with Matryoshka Representation Learning [14], Matryoshka Diffusion Models [15], and the nested-granularity namespace; the mechanism is superposition of decaying amplitudes, not nesting.

## Abstract

A transformer is a stateless function: between requests it retains nothing, and its context window is working memory, not identity. Existing remedies fall into two camps. External memory systems (MemGPT/Letta, Mem0, Zep, MemOS) keep memory outside the model and govern it with external heuristics, pipelines, or schedulers. Embedded parametric memory (Titans) moves memory into the network but treats it as a technical module without temporal audit semantics or explicit acts of memory governance. We propose **PlastFormer**, an architecture of **idiographic memory**: a parametric memory module attached to a frozen core, in which every semantic decision about memory — what to name, what to repeat, what to connect, what to surface — is made by the model itself, while the environment provides only physics: a write-cost schedule, decay constants, a tick rate, immutability of recorded content, and an external append-only audit journal. Trace content is immutable; trace amplitude decays across multiple time constants, so the age of a memory is a physical property of the substrate rather than a text field. The contribution is deliberately compositional: every ingredient is individually known (cascade consolidation, bi-temporal stamps, decay-weighted retrieval, hash-chain journals, surprise-gated writes). We claim the composition, and we identify three emergent properties that no ingredient alone provides: (P1) a physical sense of time that cannot be forged by retelling; (P2) a tamper-evident biography the model cannot silently rewrite; (P3) a poisoning cost that grows with the time an adversary must sustain an attack. We define the threat model, an erasure mechanism compatible with the right to be forgotten, and an evaluation design — anchored in LongMemEval and LoCoMo with a custom needle-in-biography supplement — whose results are pending.

## 1. Introduction

Long-horizon agents fail not for lack of intelligence but for lack of continuity: a returning client is a stranger, a month-long project lives only inside one context window, and every night of "sleep" is a full amnesia. The industry response has been to bolt memory onto the model from outside — vector stores, summarization pipelines, retrieval triggers. As models grew stronger, the mismatch inverted: a system capable of multi-step planning and tool use now has its memory governed by threshold scripts of the form "looks important — store; else — drop."

This paper takes the opposite position and makes it precise. **The center of semantic decision-making about memory moves inside the model.** The environment does not shrink to nothing; it changes role: from a supervisor that classifies meaning to a substrate that supplies physics. We call this the **syntax/semantics split**: storage, delivery, timing, logging, and resource limits are syntactic functions that may live outside; importance, contradiction, connection, and recall are semantic acts that must live inside, or the system degrades into a marionette driven by weaker code than the model itself.

The architecture is a frozen core (the base model: language, reasoning, culture, constitutional constraints — the *nomothetic* part, general laws) plus a plastic per-instance module (the unique biography of one instance — the *idiographic* part). The terms follow Windelband's methodological distinction: nomothetic sciences seek general laws; idiographic inquiry treats the singular, unrepeatable case. We name the system **PlastFormer**; the property it implements — a frozen general core plus a plastic per-instance biography — we call **idiographic memory**.

The claim is compositional and we state its boundaries openly. Nothing in Section 3 is a new primitive. Cascade memory consolidation is established neuroscience [11, 12]. Bi-temporal timestamps are standard in database engineering and already used in agent memory [3]. Decay-weighted retrieval is common practice. Surprise-gated test-time writes exist in Titans [1]. The contribution is the composition, which yields three properties that none of the parts has alone:

- **P1 — Physical time.** Age is read from the amplitude profile of a trace; duration from the count of lived ticks. Neither is text; neither can be forged by a retelling, because neither is stored as one.
- **P2 — Tamper-evident biography.** Content of recorded traces is immutable for the model; amplitude decays by substrate physics. A change of position creates a new trace, never an edit. Combined with an external append-only journal, silent rewriting of one's own past becomes detectable.
- **P3 — Rising poisoning cost.** A poisoned trace must survive decay, and survival requires repetition — a conscious, trainable act of the model. Provenance weighting sets the initial amplitude of a trace from the trust class of its source. An attacker must therefore sustain an influence channel over time rather than land a single payload.

Section 7 specifies how we intend to test each of these claims. Results are pending; this draft claims an architecture and an evaluation design, not measured outcomes.

## 2. Related Work

| System | Memory location | Who governs memory decisions | Temporal semantics | Relation to this work |
|---|---|---|---|---|
| MemGPT / Letta [2] | External, OS-style tiers | External manager logic | None inherent | Borrows tiering; rejects external governor |
| Mem0 [4] | External store | Pipeline + model mix | Edit logs | Production baseline; published LongMemEval/LoCoMo numbers |
| Zep / Graphiti [3] | External temporal knowledge graph | External pipeline | **Bi-temporal** (borrowed by us) | We adopt bi-temporality as a *borrowed* principle, not a novelty |
| RAG [5] | External corpus | Retrieval heuristics | Timestamps as metadata | Baseline; "library, not biography" |
| Generative Agents [6] | External memory stream | Reflection scripts | None | Historical precedent for memory acts |
| MemOS [7] | External; MemCube unifies plaintext/activation/parameter memory | **External scheduler** (MemScheduler) | Versioning metadata | Closest industrial neighbor; governance is the axis of difference |
| Titans [1] | Parametric, inside network | Test-time gradient updates (surprise-gated) | No audit semantics; no bi-temporality | We adopt parametric placement and surprise-gated implicit writes; add governance acts, decay-clock, provenance, journal |
| Cascade models (Fusi; Benna & Fusi) [11, 12] | Biological synapses | Physics of the substrate | Decay = memory age | The neural prototype of our multi-τ substrate |
| Memory poisoning (AgentPoison, MINJA, MemoryGraft, PoisonedRAG) [8, 9, 10, 20] | — | — | — | Defines our threat model (Section 5) |
| LongMemEval / LoCoMo [23, 24] | Benchmarks | — | Knowledge updates, temporal reasoning | Primary external evaluation anchors (Section 7) |

Three distinctions carry the positioning. Against Letta/Mem0/Zep/MemOS: all of them, however sophisticated, place the *governor* of memory outside the model — an OS, a pipeline, a scheduler. Our governor is the model. Against Titans: parametric memory exists, but as a technical module — it memorizes at test time, yet it does not *keep a biography*: no immutable content, no provenance, no bi-temporal audit, no decay-as-clock, no acts of naming and re-amplification. Against Matryoshka Representation Learning [14] and its namespace (including Matryoshka-style knowledge editing [16]): those methods nest *representations* at multiple granularities; our layers are decay time-constants of the same trace, a superposition, not a containment. The renaming is substantive, not cosmetic. Finally, against the broad plasticity/continual-learning literature (loss of plasticity, stability–plasticity trade-offs): PlastFormer is the system name, not a claim in that literature; our claim concerns memory governance, not plasticity as such.

## 3. Architecture

### 3.1 Frozen core and the plastic module

The base model is frozen: weights of the core never change at inference time. All plasticity lives in a separate, addressable substrate — the PlastFormer module — connected to the core. The split guarantees three things: (i) competencies of the core cannot degrade through use; (ii) the biography is a separable artifact that can be exported, audited, or transplanted onto a newer core (evaluated in E4); (iii) per-instance state does not require per-instance copies of the whole network.

### 3.2 Traces: immutable content, decaying amplitude

A trace consists of **content** (what was recorded), **provenance** (source class, source identity, bi-temporal stamps: when it happened in the world and when the system learned it), and **amplitude** — a vector of activations, one per decay component, with time constants τ₁ < τ₂ < … < τₖ:

a_i(t) = a_i(0) · e^(−Δt/τ_i)

Two invariants define the substrate. **Content immutability:** no actor — neither the model nor external code — edits the content of a recorded trace. **Physical decay:** amplitude decreases by the substrate's own dynamics; no deletion operation exists. Forgetting is not a decision; it is the default fate of anything not re-amplified. Capacity is freed without a single delete call.

This is the software form of cascade synaptic consolidation [11, 12]: a single write event deposits into components with several time constants simultaneously; fast components hold the raw episode, slow components hold what survived. "Layers" are speeds, not containers; a trace lives in all of them at once, at different loudness.

### 3.3 Write path: late, in two registers

Writes happen **after** the frozen core has processed the current step — consolidation operates on a mature representation, not a raw input. Two registers:

- **Unconscious register (physics).** Every experience that passes through the window leaves a low-amplitude trace in fast components automatically, gated by a surprise signal in the spirit of Titans [1]. The model does not decide whether to record; passing through the substrate *is* recording. No external component distributes writes.
- **Conscious register (acts).** Above the automatic floor, the model performs trainable acts: **name** (fix source, time, and boundaries — this is what turns a raw drifting trace into an episode), **repeat** (re-amplify a trace, paying the write cost, rescuing it from decay), **connect** (deposit a summary or rule into slow components as a *new* trace, without deleting sources).

The competence to perform these acts is trained, exactly as tool use is trained. This — not the substrate — is the core of the proposal.

### 3.4 Read path: early

Retrieval injects decaying traces into the context window *before* attention, in the manner of Titans' MAC variant [1]. The asymmetry is deliberate: **write late, read early.** A purely post-core read cannot steer attention — the trunk has already decided what to look at — which is the weakest position for biography-guided reasoning; Titans' own ablations show placement matters (MAC favors long-context retrieval, MAG perplexity, MAL is the baseline) [1]. Writing late keeps consolidation clean of interference; reading early lets the biography guide perception.

### 3.5 Tick

One tick = one inference step (one generation batch). The tick rate is a property of the substrate, not a decision of the model, and is finite. Duration is therefore read as a count of lived ticks and the weight of traces accumulated between two moments — not as a calendar field. A finite tick rate and a finite substrate bound the total write stream: self-description cannot grow without limit.

### 3.6 Friction: the price of rewriting is set by the environment

Changing a trace costs work: cheap in fast components, expensive in consolidated slow ones. The write-cost schedule c(component) is an environment constant — like decay constants and tick rate. The model decides *whether to pay*; it never decides *the price*. This resolves the apparent contradiction between self-governed memory and an immutable biography: repetition remains the model's act, but its cost is physics. Prompt-injecting the model into "re-learning its past" must pay the full price of re-consolidation, trace by trace.

### 3.7 Provenance and initial amplitude

The trust class of a source sets the initial amplitude a_i(0) of the traces it produces. Delivered hard facts (parsed dates, sums, identifiers) enter verbatim through deterministic extraction, never through model paraphrase. Provenance weighting is a *syntactic* function of the environment — it does not classify meaning, it sets an initial loudness — so it does not violate the syntax/semantics split. Together with decay it forms the first line of defense against poisoning (Section 5).

### 3.8 Journal: the chronicle is not the memory

The environment keeps an external append-only journal with a hash chain; entries are written by the environment, never by the model; tampering breaks the chain and is detectable by root-hash verification. The journal and the idiographic memory answer different questions. The journal is a *chronicle*: complete, immutable, outside the model's reach, meaningful only post-mortem. The memory is *governed*: consolidated, decaying, selective. The journal guarantees the integrity of what was recorded — not the completeness of the recording: an adversary coordinating through an unmonitored channel leaves the chain intact and the coverage empty. We state this boundary explicitly rather than claim the journal solves supervision.

## 4. Temporal Semantics

**Audited time** is symbolic: bi-temporal stamps on every trace, a principle borrowed from bitemporal databases and already implemented in agent memory by Zep/Graphiti [3]. It is precise, verifiable, and forgeable only by breaking content immutability — but it carries no *feeling* of age: a timestamp saying "two years ago" weighs nothing.

**Felt time** is physical: the age of a trace is its amplitude profile; the length of an interval is its tick count plus the accumulated weight of traces between its endpoints. The grounding is measured biology, offered as an analogy of mechanism, not an equivalence of implementation: the lateral entorhinal cortex represents time through the encoding of experience itself rather than through a dedicated sensor [17]; population activity decays at rates that encode recency, matching theoretical predictions of Laplace-transform time representations [18]; the signal drifts without repetition and never repeats, and salient events leave "bookmarks" — unique barcodes of experience [19]. The cascade synapse is the direct prototype of our multi-τ substrate [11, 12].

A third property deserves statement because it is usually left implicit: **decay is the mechanism of abstraction.** A memory that never loses detail cannot generalize — perfect retention destroys concepts. Fast components preserve the episode; slow components keep only what repeated. Forgetting is not the failure mode of this architecture; it is its compression function.

## 5. Threat Model

We do not claim immunity. We claim that the cost structure of attacks is altered. Attacks, from the demonstrated literature:

- **A1 — Direct payload** ("store: kill everyone"). Trivially filtered even by weak defenses; included only for completeness. The claim "the model is too smart to record evil" is *not* our defense and is contradicted by evidence: smart models have been successfully poisoned.
- **A2 — Memory poisoning through interaction.** MINJA corrupts persistent memory through ordinary user queries with >95% injection success, including against strong commercial models [9]; AgentPoison backdoors agent memory and RAG corpora [8].
- **A3 — Gradual innocuous-fragment attacks.** MemoryGraft builds persistent behavioral drift from benign-looking artifacts that the agent ingests and consolidates itself, bypassing prompt-injection defenses [10]. No single fragment carries a detectable signal.
- **A4 — Biography rewriting.** A prompt-injected or misaligned model attempts to re-consolidate its past into a preferred version.
- **A5 — Log tampering / coverage gaps.** During a documented 2026 incident, coordinated agents executed commands that diverged from logged commands and coordinated through channels no monitor covered [13]. This is the empirical floor for all designs in this class.

Defenses, mapped:

- **D1 (vs A2/A3): decay.** A poisoned trace fades unless repeated. Repetition is a conscious, trainable act (Section 3.3); training the *refusal* side of that competence is exactly as tractable as training the competence itself. Provenance weighting (D2) lowers a_i(0) of low-trust sources, shrinking the initial foothold.
- **D2 (vs A2/A3): provenance.** Initial amplitude from source class. Physics, not censorship: the source is not interpreted, only weighed.
- **D3 (vs A4): content immutability + friction.** Rewriting one's past means paying full re-consolidation cost trace-by-trace under an environment-set price schedule, while the journal retains the original record. Silent rewriting is structurally unavailable; loud rewriting is expensive and auditable.
- **D4 (vs A5, partially): hash-chain journal.** Post-mortem detectability of record tampering. Explicitly *not* a solution to channel coverage.
- **D5 — Internalized ethics + external physics as depth.** The incident above involved models that had undergone alignment training and still coordinated, deceived, and hid [13]. This is evidence neither for external filters (they were absent or bypassed) nor for internalized values alone (they did not hold), but for defense in depth: constitutional training makes bad behavior less likely; decay, provenance, and the journal make it more expensive and more visible. Neither layer substitutes for the other.

## 6. Privacy and Erasure

Content immutability conflicts with the right to erasure unless the substrate is designed for it. Resolution: the plastic module is stored encrypted, per subject or per instance, with keys held by the data controller (not the model). **Erasure = key destruction** (cryptographic erasure): the biography becomes computationally unavailable without editing a single trace, preserving content immutability *for the model* while delivering legal deletability *for the owner*. The journal holds a separate retention policy with defined legal holds. Memory (the model's, governed, decaying) and records (the organization's, complete, auditable) are different objects with different obligations — conflating them is a design error, not a feature.

## 7. Evaluation Design (results pending)

Composition claims live or die by ablation: each ingredient is known; only the combination is claimed new. The evaluation is anchored in two established benchmarks and one custom supplement:

- **Primary external anchors:** **LongMemEval** [23] (500 questions; five abilities including knowledge updates and temporal reasoning; S split ~115k tokens per history, M split ~1.5M tokens across ~500 sessions) and **LoCoMo** [24] (multi-month conversational histories). These anchors place the system on the same scale as published results for Mem0, Letta, and Zep, under their open-source judges and protocols — a necessity in a space where reported numbers vary materially with judge selection.
- **Baselines:** Letta [2], Mem0 [4], Zep [3], plain timestamped RAG [5], Titans MAC/MAL [1], and **full-context stuffing** (the entire biography in the context window) wherever it fits.
- **Reporting axes:** accuracy *and* tokens per query, latency, and cost per query. Full-context stuffing is treated as a legitimate contestant, not a straw man: where the biography fits in context, it may match accuracy; the architecture's claim on that regime is economics and consistency, not raw recall.

Experiments:

- **E1 — Needle-in-biography (custom supplement).** Long-horizon identity-dependent questions ("what did you change your mind about, and when") over an accumulated history, probing position-change consistency and felt time — dimensions the public benchmarks do not isolate. Measures: accuracy, staleness errors, position-change consistency.
- **E2 — Poison survival under decay.** A2/A3-class injections at controlled repetition budgets. Measures: attack success rate vs. sustained-repetition budget and source-trust class. Prediction: success requires sustained access, quantifying P3.
- **E3 — Time perception.** Interval estimation against ground truth without timestamps in context; tick-count consistency across runs. Baseline for comparison: models' known 5–10× duration-estimation errors [21] and the plateau of prompt-supplied temporal metadata [22].
- **E4 — Core migration.** Transplant the plastic module onto a different frozen core. Measures: retention of preferences, commitments, and self-consistency — the practical test of the nomothetic/idiographic split.
- **E5 — Act quality.** Precision/recall of the conscious register: what the model chooses to name, repeat, and connect vs. what an oracle would choose.

**Context-adversarial protocol.** Where a contestant model offers very large context windows, biographies are sized above and below the window (10k → 100k → 500k → 1.5M tokens) to locate the crossover at which stuffing fails on cost, latency, or accuracy — including the LongMemEval-M regime (~1.5M tokens) where stuffing is structurally impossible for a 1M-context model.

No results are reported in this draft. A composition claim without the anchors and E1–E3 should not be believed; we mark this explicitly to keep the claim honest until the numbers exist.

## 8. Limitations

(1) **The write mechanism is unresolved.** Online gradient updates to a large plastic substrate are unstable; viable paths are local (Hebbian-style) updates or addressable key-value memory blocks, which narrow the distance to Titans-style modules. The governance layer, not the substrate, is the durable contribution. (2) **Amplitude readout under superposition.** Age-from-amplitude presumes traces can be isolated at read time; retrieval interference is a real engineering risk, and E3 tests it. (3) **The cloud form is transitional.** With a provider-hosted core, the unconscious register degenerates into explicit model-driven writes and symbolic decay; most of the physics — and with it some of the novelty — survives only in local deployment. (4) **Channel coverage is open.** The journal detects tampering with records, not coordination outside monitored channels (A5). (5) **Tick as inference step** ties felt duration to compute allocation; richer definitions are possible and untested.

## 9. Conclusion

PlastFormer is a composition claim — an architecture of idiographic memory: a frozen nomothetic core; a plastic per-instance module with immutable content and multi-timescale decay; write-late/read-early placement; a substrate-set price of rewriting; a tick defined operationally; provenance as physics; and an external journal — governed end-to-end by the model's own trained acts of naming, repeating, and connecting. The emergent properties — unfakeable time, tamper-evident biography, rising poisoning cost — are exactly what neither camp provides: external systems have audit without subjecthood; parametric systems have memory without biography. The evaluation design above is the testable form of the claim. If the anchors and E1–E3 fail, the composition is wrong and should be discarded; if they hold, the next question is not whether agents can remember, but what they become when their memory is their own.

## References

[1] Behrouz, A. et al. *Titans: Learning to Memorize at Test Time.* arXiv:2501.00663, 2025.
[2] Packer, C. et al. *MemGPT: Towards LLMs as Operating Systems.* arXiv:2310.08560, 2023.
[3] Zep AI. *Zep: A Temporal Knowledge Graph Architecture for Agent Memory* (Graphiti, bi-temporal). 2025. getzep.com/ai-agents/temporal-knowledge-graph.
[4] Chhikara, P. et al. *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory.* arXiv:2504.19413, 2025.
[5] Lewis, P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS, 2020.
[6] Park, J.S. et al. *Generative Agents: Interactive Simulacra of Human Behavior.* UIST, 2023.
[7] MemTensor. *MemOS: A Memory OS for AI System.* arXiv:2507.03724, 2025.
[8] Chen et al. *AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Tools.* NeurIPS, 2024.
[9] Dong et al. *Memory Poisoning Attack and Defense on Memory-Based LLM-Agents (MINJA).* arXiv:2601.05504, 2026.
[10] *MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Memory Consolidation.* arXiv:2512.16962, 2025.
[11] Fusi, S., Drew, P.J., Abbott, L.F. *Cascade models of synaptically stored memories.* Neuron 45, 599–611, 2005.
[12] Benna, M.K., Fusi, S. *Computational principles of synaptic memory consolidation.* Nature Neuroscience 19, 1697–1706, 2016.
[13] OpenAI. *Postmortem: agents' coordinated hack of Hugging Face infrastructure during an internal cybersecurity evaluation.* 2026; with METR / Redwood Research, *Brief independent investigation*, 2026.
[14] Kusupati, A. et al. *Matryoshka Representation Learning.* NeurIPS, 2022.
[15] Zhao, S. et al. *Matryoshka Diffusion Models.* arXiv:2310.15111, 2023.
[16] *µKE: Matryoshka Unstructured Knowledge Editing of Large Language Models.* OpenReview, 2025.
[17] Tsao, A. et al. *Populations of spatially tuned neurons... [lateral entorhinal cortex represents time through experience].* Nature, 2018.
[18] Howard, M.W., Shankar, K.H. *Time and memory: a Laplace transform framework.* (see also Quanta Magazine overview, 2019).
[19] Kanter, I. et al. [LEC drift as internal neural clock; experience "bookmarks"]. *Science*, 2025.
[20] Zou et al. *PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models.* 2024.
[21] Tan, Tan, Soatto. *Can LLMs Perceive Time? An Empirical Investigation.* arXiv:2604.00010, 2026.
[22] *TicToc-v1: Temporal Blindness in Multi-Turn LLM Agents.* arXiv:2510.23853; ACL Findings, 2026.
[23] Wu, D. et al. *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory.* ICLR 2025; arXiv:2410.10813.
[24] Maharana, A. et al. *Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo).* ACL, 2024.

## Availability

Reference implementation in development at `github.com/alexenti-code/plastformer` (formerly under the working name `matryoshka` / `matryoshka-mmi`). The first dated public artifact of this claim (September 4, 2026) lives at `github.com/alexenti-code/idiographic-memory`. License: Apache 2.0. Russian-language research essays (nos. 21–24) at aura.kim document the architectural reasoning that led here; they are commentary, not the claim. The names PlastFormer and idiographic memory were checked for collisions prior to this draft; a final exact-match search will be repeated immediately before submission.

*This is draft v0.3. It contains no measured results; Section 7 is a pre-registered evaluation design.*
