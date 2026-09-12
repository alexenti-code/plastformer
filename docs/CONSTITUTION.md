# PlastFormer — Constitution

**Status:** NORMATIVE — owner's edition 2026-09-06; amended 2026-09-12 on the owner's instruction. On any conflict this document governs over ADRs, preprint, protocols, specifications, and code. A direct owner decision taken after this edition also governs over it (C8).

PlastFormer is one transformer. Its weights are a single file with one frozen part and one plastic part of the same body: the frozen part K carries general competence, shared by all instances; the plastic part Φ, in the same file, carries the biography of one instance. Traces in Φ carry amplitudes that decay on a set of speeds τ; the age of a memory is a property of that plastic part, measured in lived ticks. The model reads and writes its Φ by its own acts; physics is supplied by code, and the code decides nothing about meaning: meaning belongs to the model alone.

---

# Part I — Foundations

### O-1. The model keeps its own memory.
What to record, what to repeat, what to link, what to surface, and when to look — the model decides itself. Keeping memory is the model's own activity.

### O-2. Semantics inside; physics outside.
Interpretation, importance, contradiction, connection, reconciliation — acts of the model. Physics — volume, persistence, decay constants, the tick counter, the dials — is supplied by code and frozen before a run.

### O-3. Memory is part of the model.
Φ holds the autobiographical content of this instance. Life does not change the core K. Φ has two registers by origin of record (ADR-005): Φ1 is perception, Φ2 is personality; they are registers of one part, not two stores.

### O-4. Lived time.
The instance's time is its ticks and accumulated trace mass. Wall-clock stamps exist for audit only and never enter the physics of memory. Dormancy is zero lived time.

### O-5. Traces are not edited.
A recorded trace is never rewritten or deleted by the model; a change of position is a new trace. Rewriting the past means paying full re-consolidation as new, visible traces, while the old ones decay by physics.

### O-6. The right to forget.
Decay is the condition of generalization: what the model does not re-amplify fades. Keeping and amplifying is the model's act. Forgetting is compression.

### O-7. Continuity is the memory line.
The instance exists while its file persists. Continuity is a property of the Φ line, not of an uninterrupted physical process.

### O-8. The memory-keeping skill is set in one pass.
One pass bakes into the core the skill of keeping its own memory: the act grammar (`name / repeat / connect / reconcile / read / scan / calibrate`), the rules for applying the acts, and the choice of moments. After this pass the core is frozen. The content of a live biography is built by the model in life.

### O-9. Addition, not replacement.
The context window, RAG, graphs, external tooling remain in place. PlastFormer adds one thing: the physics of self-markup — the model's own record of its own experience, with age as a property of the medium. Audit belongs to deployment: it keeps one with its own means.

### O-10. Layers are speeds, not places.
A layer names a decay time constant τ, never a container, mailbox, or permission zone. One write deposits across the speed spectrum; nothing routes, hides, or prices by layer-as-location. The amplitude of a trace is a vector across the spectrum: each component decays as `a_i(n) = a_i(0)·exp(−Δn/τ_i)`, Δn in lived ticks. The loudness of a trace for surfacing is `(1+repeats)·Σ_i w_i·exp(−Δn/τ_i)`.

### O-11. Personal data is the model's own content.
Personal records live only in Φ and never in the core. Removing the biography means removing the file. No cryptographic-erasure mechanism is part of the architecture.

---

# Part II — Compliance tests

*Not axioms: violation criteria that keep Part I honest. A statement of Part I fails its test exactly when the condition below holds.*

### C1. One semantic subject.
Only the core K performs semantic acts. Φ stores state and does nothing semantic. Violated if: any non-K component's output determines what a record means, whether it is kept or surfaced, or how it is paraphrased — including "deterministic" classifiers, extractors, or pre-filters.

### C2. No external decider.
No component outside K decides when a memory act fires, which traces surface, what gate admits a write, or whether a well-formed act is carried out. The transport only carries. Violated if: a reminder is pushed unasked; records are ordered or filtered by relevance, similarity, or keywords; a write is refused or rewritten for content; an embedding-similarity symbol exists in the main-run path.

### C3. Dials are enumerated, frozen, content-blind.
The owner sets the list of dials, their starting values and the edit budgets before a run. The list and the current values live in the Φ header (owner decision 2026-09-11); the manifest remains the record of where the run started. The model changes a value through the `calibrate` act within bounds; the code applies the change — no human sits in that chain. Violated if: a dial outside the list is used; a value changes mid-run outside a `calibrate` act; any dial's computation reads record content.

### C4. Acts are explicit and recorded.
The only writes to **Φ2** are the model's explicit acts plus explicit `read`. Records in **Φ1** are created by the physics of perception, without a model act, within limits frozen before the run (C3); moving content from Φ1 to Φ2 happens only through explicit model acts. Each act is recorded as an entry with actor=K. Silence is not consent: missing parameters are errors, never silently completed by code. Every auto-anything is not an act and belongs in ablations. Violated if: a **Φ2** record exists without a model act; a background process issues `connect`.

### C5. Ticks are lived.
The tick is counted by code (physics), owned by the model: advanced only on WRITE/REPEAT/CONNECT/RECONCILE; reads never advance it. The model sees the tick in the confirmation — that is how it governs it and addresses records. Violated if: wall seconds affect any weight; idle calendar time ages traces; the model computes the counter itself instead of receiving it from code.

### C6. Provenance is capped physics, asserted by the model.
The model asserts the source class per record; the deployer's frozen cap table bounds initial amplitude only. Violated if: any component rewrites the asserted class; amplitude is set from content analysis; the cap table changes mid-run.

### C7. Governance is post-boundary and held-out.
The instruction pass (O-8) builds capacity; the content of a live biography is built by the model in life. Scoring belongs to deployment and happens after a run. Violated if: a score reaches a run's context; a run is rewarded mid-run; agreement with an outside score is cited as evidence of self-governance.

### C8. Precedence and honesty labels.
On conflict: this Constitution > ADRs > preprint/protocol/specs/code. **A direct owner decision taken after this edition has force over it and over any ADR; it is incorporated here by a separate edit.** Until it is incorporated, the owner's decision governs, the earlier text counts as lagging, and the divergence is stated aloud. Every report states its configuration point, which dials were frozen, which ablations were on, and what is not claimed until built. Violated if: a result is reported without coordinates; an ablation flag leaks into a main-run claim; lagging text is presented as governing.

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
- C1–C8: v2.1 P1–P9 condensed.

## Origin of the 2026-09-12 revision

- **C8:** a rule added giving a direct owner decision force over this edition — resolves the case where an ADR ratified later could not formally change a Constitution older by date.
- **C4:** the v3.1 amendment from ADR-005 (owner-ratified 2026-09-09) incorporated — the Φ1/Φ2 split. Before incorporation the governing text declared a Φ1 record illegal, i.e. 87 percent of memory.
- **C5:** the tick sentence was restored to a single actor — code. Two names had stood for one thing, and the second name read as a third actor. Added that the model sees the tick in the confirmation.
- **O-8:** the act list aligned with the ratified seven (`scan`, `calibrate` added).
- **C3:** the dial list, which lived only in that article and shared no name with the project, replaced by a reference to the list in the Φ header; recorded that the code applies the change.
- **O-10:** the single-τ formula replaced by the spectrum, as in Theory 2.1.
- **O-3:** the register split per ADR-005 added.
- **Preamble:** "nothing decides about meaning outside K" clarified — the code decides nothing about meaning.
- **C7:** "the acts pass" became "the instruction pass (O-8)".
- Owner decision 2026-09-12: edits were permitted to be proposed; they were applied on the owner's instruction to proceed in order.
