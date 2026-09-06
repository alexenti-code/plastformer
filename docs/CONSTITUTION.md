# PlastFormer — Constitution

**Status:** NORMATIVE — owner's edition, 2026-09-06. On any conflict this document governs over ADRs, preprint, protocols, specifications, and code.

PlastFormer is a transformer of two parts: a frozen core K (general competence, shared by all instances) and a plastic substrate Φ (the biography of one instance). Traces in Φ carry amplitudes that decay on a set of speeds τ; the age of a memory is a property of the medium, measured in lived ticks. The core reads and writes Φ by its own acts; the environment supplies physics and decides nothing about meaning.

---

# Part I — Foundations

### O-1. The model keeps its own memory.
What to record, what to repeat, what to link, what to surface, and when to look — the model decides itself. Keeping memory is the model's own activity.

### O-2. Semantics inside; physics outside.
Interpretation, importance, contradiction, connection, reconciliation — acts of the model. The environment supplies physics: volume, persistence, decay constants, a tick counter, dials fixed before a run.

### O-3. Memory is part of the model.
The substrate Φ holds the autobiographical content of this instance. Life does not change the core K. Duplicating Φ produces a new instance that shares history with the original up to the moment of duplication and diverges afterwards — nothing more mystical than that.

### O-4. Lived time.
The instance's time is its ticks and accumulated trace mass. Wall-clock stamps exist for audit only and never enter the physics of memory. Dormancy is zero lived time.

### O-5. Traces are not edited.
A recorded trace is never rewritten or deleted by the model; a change of position is a new trace. Rewriting the past means paying full re-consolidation as new, visible traces, while the old ones decay by physics.

### O-6. The right to forget.
Decay is the condition of generalization: what the model does not re-amplify fades. Keeping and amplifying is the model's act. Forgetting is compression.

### O-7. Continuity is the memory line.
The instance exists while its substrate persists. Continuity is a property of the Φ line, not of an uninterrupted physical process.

### O-8. The memory-keeping skill is set in one pass.
One pass bakes into the core the skill of keeping its own memory: the act grammar (`name / repeat / connect / reconcile / read`), the rules for applying the acts, and the choice of moments. After this pass the core is frozen. The content of a live biography is built by the model in life.

### O-9. Addition, not replacement.
The context window, RAG, graphs, external tooling remain in place. PlastFormer adds one thing: the physics of self-markup — the model's own record of its own experience, with age as a property of the medium. External audit logging stays outside the architecture: the deployment decides on it.

### O-10. Layers are speeds, not places.
A layer names a decay time constant τ, never a container, mailbox, or permission zone. One write deposits across the speed spectrum; nothing routes, hides, or prices by layer-as-location. The amplitude of a trace obeys `weight=(1+repeats)·exp(−Δn/τ)`, Δn in lived ticks.

### O-11. Personal data is the model's own content.
Personal data lives only in the substrate and never in the core. Erasure of the biography = deletion of the substrate (or of its subject's section); the core survives. No cryptographic-erasure mechanism is part of the architecture.

---

# Part II — Compliance tests

*Not axioms: violation criteria that keep Part I honest. A statement of Part I fails its test exactly when the condition below holds.*

### C1. One semantic subject.
Only the core K performs semantic acts. Φ stores state and does nothing semantic. Violated if: any non-K component's output determines what a record means, whether it is kept or surfaced, or how it is paraphrased — including "deterministic" classifiers, extractors, or pre-filters.

### C2. No external decider.
No component outside K decides when a memory act fires, which traces surface, what gate admits a write, or whether a well-formed act is carried out. The transport only carries. Violated if: a reminder is pushed unasked; records are ordered or filtered by relevance, similarity, or keywords; a write is refused or rewritten for content; an embedding-similarity symbol exists in the main-run path.

### C3. Dials are enumerated, frozen, content-blind.
The owner may set only the dials listed before a run and frozen in the manifest: memory volume, forgetting tempo, τ set and scale, friction schedule c(τ), provenance cap table, injection N-cap, clock mode. Violated if: an unlisted knob is used; a value changes mid-run unlogged; any dial's computation reads record content.

### C4. Acts are explicit and recorded.
The only writes to Φ are the model's explicit acts plus explicit `read`; each act is recorded as a Φ entry with actor=K. Silence is not consent: missing parameters are errors, never silently completed by the environment. Every auto-anything is not an act and belongs in ablations. Violated if: a Φ record exists without a model act; a background process issues `connect`.

### C5. Ticks are lived.
The tick is counted by the environment, owned by the model: advanced only on WRITE/REPEAT/CONNECT/RECONCILE; reads never advance it. Violated if: wall seconds affect any weight; idle calendar time ages traces.

### C6. Provenance is capped physics, asserted by the model.
The model asserts the source class per record; the deployer's frozen cap table bounds initial amplitude only. Violated if: any component rewrites the asserted class; amplitude is set from content analysis; the cap table changes mid-run.

### C7. Governance is post-boundary and held-out.
The acts pass builds capacity; it must not decide the content of any live biography. Oracles, ledgers, and judges never enter Φ, context, or notes during a run; they score post-hoc only. Violated if: judge output reaches a run's context; a run is rewarded mid-run by oracle score; oracle overlap is cited as self-governance evidence.

### C8. Precedence and honesty labels.
On conflict: this Constitution > ADRs > preprint/protocol/specs/code. Every report states its configuration point, which dials were frozen, which ablations were on, and what is not claimed until built. Violated if: a result is reported without coordinates; an ablation flag leaks into a main-run claim.

---

## Origin (lineage of the Foundations)

- O-1, O-2: GLOSSARY axioms 1–3; THEORY §1; owner directive 2026-09-05.
- O-3: GLOSSARY axioms 4, 5, 8; ADR-003 (copy-as-branch wording replaced by plain duplication wording 2026-09-06).
- O-4: GLOSSARY axiom 9; preprint §3.5, §4.
- O-5: THEORY invariants; SPEC; preprint §3.2; security framing withdrawn per owner decision 2026-09-05 (variant A).
- O-6: owner formulation 2026-09-05 ("generalization is, among other things, the ability to discard").
- O-8: replaces "Training builds capacity" (v2.1 O-8) per owner directive 2026-09-06: one instruction pass, not retraining.
- O-9: SPEC ("addition, not a replacement"); owner directive 2026-09-05.
- O-10: promoted from Compliance P3 per owner directive 2026-09-06 (a foundational postulate, not a test); THEORY §2.1; GLOSSARY Ax.6.
- O-11: GLOSSARY permissions 1–2; ADR-004.
- C1–C8: v2.1 P1–P9 condensed; weight formula promoted to O-10.
