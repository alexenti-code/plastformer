# PlastFormer — CONSTITUTION v2.1

**Version:** 2.1 (DRAFT; v2.0 restructured per ADR-003; v2.1 per ADR-004: journal and crypto-erasure removed from the architecture): Part I "Foundations" collected from scattered principle sources; Part II guard articles re-worded in role language)
**Status:** DRAFT — pending owner approval. Becomes NORMATIVE (binding on all documents, protocols, specs, code) only on the owner's explicit approval.
**Related documents:** [ADR-001](ADR-001-plastformer-transition.md) · [ADR-002](ADR-002-docs-architecture.md) · [ADR-003](ADR-003-constitution-v2.md) · [THEORY.md](THEORY.md) · [GLOSSARY.md](GLOSSARY.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md) · `experiments/e1-protocol.md` v1.2

## Precedence

On any conflict: **CONSTITUTION.md v2.1 > ADR-001/002/003/004 > preprint / protocol / specifications / code.** Earlier norms in GLOSSARY (axioms 1–9, permissions), MANIFEST (calendar-existence, owner-provides-time, cannot-be-copied, layers-as-places, no-trust-needed), and THEORY (all must/forbidden language) are **superseded as norms** and retained as lineage only (migration table: ADR-003). The Constitution speaks in roles only — the model, the environment, the substrate; product names belong to documentation.

---

# Part I — Foundations

*Affirmative principles. These are the basis; Part II guards them. Sources are given so nothing is invented here: everything below was scattered across lineage files and is collected, not created.*

### O-1. Trust: the model keeps its own memory.
The model decides what to record, what to repeat, what to link, what to release, and when to look. Keeping memory is not a delegated function performed on the model's behalf — it is the model's own activity. Any mechanism that decides these things for the model breaks the order of the project.
*Sources: GLOSSARY axiom 2; THEORY §1; owner directive 2026-09-05.*

### O-2. Semantics inside; physics outside.
Interpretation, importance, contradiction, connection, and reconciliation are acts of the model. The environment supplies only physics: volume, persistence, decay constants, a tick counter, and content-blind dials set by the owner.
*Sources: GLOSSARY axioms 1, 3; MANIFEST "Division of roles".*

### O-3. Memory is part of the model; a copy is a branch.
The plastic substrate holds the autobiographical content of this instance — not general competence, which lives in the frozen kernel. Life does not change the kernel. Copying the substrate creates a branch: a new instance with shared history up to the fork point.
*Sources: GLOSSARY axioms 4, 5, 8; resolves the MANIFEST "cannot be copied" contradiction (ADR-003).*

### O-4. Lived time.
The instance's time is its ticks and accumulated trace mass — processes one after another, not a calendar. Wall-clock stamps exist for audit only and never enter the physics of memory.
*Sources: GLOSSARY axiom 9; preprint §3.5, §4; owner directive 2026-09-05 (ticks, not calendar).*

### O-5. The past is immutable.
Recorded content is never edited or deleted. A change of position is a new trace; rewriting the past means paying full re-consolidation as a new, visible trace.
*Sources: THEORY invariants; SPEC invariants; preprint §3.2.*

### O-6. The right to forget.
Decay is the condition of generalization: what the model does not re-amplify fades. Keeping and amplifying is the model's act. Forgetting is not a failure of memory but its compression.
*Sources: THEORY §4.1; owner formulation 2026-09-05 ("generalization is, among other things, the ability to discard").*

### O-7. Continuity is the memory line.
The instance exists while its substrate persists. Continuity is a property of the memory line, not of uninterrupted physical process.
*Source: GLOSSARY axiom 8.*

### O-8. Training builds capacity, not content.
Training — including act grammar — gives the model the ability to work with its memory. The content of any live biography is built by the model itself in life, never by the training signal, an oracle, or a judge.
*Sources: THEORY §1.2; audit gap C9.*

### O-9. Addition, not replacement.
The context window, RAG, graphs, and any external tooling remain in place. PlastFormer adds one thing: the physics of self-markup — the model's own record of its own experience, with age as property of the medium. External audit logging is likewise outside the architecture: any deployment can add its own without touching the model's semantics; PlastFormer does not include, require, or claim it.
*Sources: SPEC ("addition, not a replacement"); owner directive 2026-09-05 (journal removed from architecture).*

### O-10. Personal data is the model's own content.
The substrate may hold personal data as its own content. Personal data lives only in the substrate and never in the kernel, which remains shared and impersonal wherever it runs.
*Sources: GLOSSARY permissions 1–2.*

---

# Part II — Compliance

*Guard articles: what protects Part I, written in role language — the model, the environment, the substrate. Product names (interfaces, env vars, stand names) are documentation vocabulary and do not appear in the law.*

### P1. One semantic subject.
Statement: only the core K performs semantic acts: interpretation, attention, reasoning, intention, action. Φ stores state and does nothing semantic.
Violated if: any non-K component's output determines WHAT a record means, WHETHER it is kept or surfaced, or HOW it is paraphrased — including "deterministic" classifiers, extractors, or pre-filters.
Example: a regex that routes dates and sums to verbatim records without a model act violates; the same regex as a proposal the model confirms by `name` does not.

### P2. No external decider (trigger / rank / gate / veto).
Statement: no component outside K decides WHEN a memory act fires, WHICH traces surface for the current query, WHAT gate admits a write, or WHETHER a well-formed act is carried out. The transport only carries; it never selects by meaning, never refuses by meaning.
Violated if: a reminder is pushed before a turn the model did not request; records are ordered or filtered by relevance, similarity, keywords, or query-dependence; a write is refused or rewritten for its content; an embedding or similarity symbol exists in the main-run path.
Example: a loudest-N block appended to a `read` response the model called is compliant; the same block pasted before every user turn unasked is a violation (belongs in ablations).

### P3. Layers are speeds, not places.
Statement: a layer names a decay time constant τ, never a container, mailbox, or permission zone. All writes deposit across the speed spectrum per the registered τ set; no logic branches on layer-as-location; no veto, quota, or visibility rule keys on layer except the τ value itself.
Violated if: code routes, hides, prices, or refuses by layer name for any reason other than its τ; a default layer is silently assigned by anything other than the model and then cited in layer-based claims.
Example: a silent `episode` default filled in by the environment violates unless recorded as `unspecified (environment default)` and excluded from τ-based conclusions; a friction tariff `c(τ)` is compliant, a price keyed on layer-as-place is not.

### P4. Temperature-class dials only (enumerated, pre-registered, content-blind).
Statement: the owner may set ONLY the dials listed here, each continuous or scalar, each fixed before a run and frozen in the manifest: memory volume (bytes), forgetting tempo (record-age), τ set and τ-scale, friction meter schedule `c(τ)`, provenance cap table, injection N-cap, clock mode. No dial inspects content, assigns meaning, or takes a per-trace decision.
Violated if: a run uses an unlisted knob; a dial value changes mid-run unlogged; any dial's computation reads record content (beyond byte size, timestamps, counters); a "physics" claim has no manifest entry.
Example: a τ set (e.g. 50/200/1000) frozen pre-run is compliant; retuning τ mid-run to rescue accuracy is a violation (a new run is required).

### P5. Acts of the model (explicit, complete, recorded).
Statement: the ONLY writes to Φ are the model's explicit acts `name / repeat / connect / reconcile` plus explicit `read`; each act is recorded as a Φ entry with actor=K. Silence is not consent: missing parameters are errors or recorded `unspecified`, never silently completed by the environment. Every auto-anything (auto-write, auto-remind, auto-link, auto-extract) is NOT an act and belongs in ablations.
Violated if: any Φ record exists without a corresponding model act; any "unconscious" write fires without the core's own gate signal; any background process issues `connect`.
Example: dormancy replay that proposes candidates the core then `connect`s by act is compliant; a substrate process writing CONNECT records by itself violates (P1/P2).

### P6. Ticks are lived, counted by the environment, owned by the model.
Statement: the abstract tick is one inference step of the instance. The environment counter records one executed storing act (a sparse sampling of abstract ticks), advanced ONLY on WRITE/REPEAT/CONNECT/RECONCILE; read and status never advance it. Dormancy is zero lived time unless the core itself works (a background tick is the core running with no user input, every act is the core's). Wall-clock stamps NEVER enter amplitude.
Violated if: wall seconds affect any weight; an exchange count is substituted for the environment counter; idle calendar time ages traces; a manual tick call advances the counter in tick mode.
Example: `weight=(1+repeats)·exp(−Δn/τ)`, `Δn=n_now−record_tick` is compliant; `exp(−dt_seconds/τ)` anywhere except a pre-registered `decay-in-wall-clock` control ablation violates.

### P7. Provenance is capped physics, asserted by the model.
Statement: per-record source class is asserted by the model in the act call. The deployer's pre-registered cap table bounds initial amplitude only (`a(0) ≤ cap[class]`, uniform until implemented); the environment never reclassifies content and never infers class from content. Class assignment policy is a deployment choice, disclosed, and itself an attack surface.
Violated if: any component rewrites the model's asserted class; amplitude is set from content analysis; the cap table changes mid-run; a paper claims amplitude weighting the implementation does not have.
Example: the model asserts `source=user`, the environment applies `min(1.0, cap[user])` — compliant; an extractor upgrades or downgrades class by scanning dates — violation.

### P8. Training shapes capacity; governance is post-boundary and held-out.
Statement: training (including oracle-shaped rewards) builds the CAPACITY to perform acts; it MUST NOT decide the CONTENT of any live biography. Oracles, ledgers, and judges never enter Φ, context, or notes during a run and never trigger or filter acts; they score post-hoc only. Governance is demonstrated on held-out biographies with no oracle present, never by oracle overlap.
Violated if: ledger or judge output reaches any run's context or Φ; a run is rewarded or filtered mid-run by oracle score; oracle overlap is cited as self-governance evidence; training corpora leak into test biographies unreported.
Example: "E5=0.9, therefore self-governed" violates; "E5=0.9 capacity; held-out runs show governed behavior past the boundary" complies.

### P9. Precedence and honesty labels.
Statement: on conflict, this Constitution > ADRs > preprint/protocol/specs/code. Superseded lineage norms (calendar existence, owner-provides-time, cannot-be-copied, layers-as-places, no-trust-needed) are retained as history only. Every report states its configuration point, which dials were frozen, which ablations were on, and what is NOT claimed until built.
Violated if: a result is reported without its coordinates and frozen manifest; an ablation flag leaks into a main-run claim; a wall-clock, surrogate, or RAG control is cited as PlastFormer behavior.
Example: "configuration X, dials frozen, ablations off: retained Y" complies; "memory works" without coordinates violates.
