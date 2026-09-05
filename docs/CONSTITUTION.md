# PlastFormer — CONSTITUTION v1.0

**Version:** 1.0 (from `drafts/constitution-audit.md` draft P1–P10; created per ADR-002)
**Status:** NORMATIVE — binding on all PlastFormer documents, protocol, spec, and code
**Related documents:** [ADR-001](ADR-001-plastformer-transition.md) · [ADR-002](ADR-002-docs-architecture.md) · [THEORY.md](THEORY.md) · [GLOSSARY.md](GLOSSARY.md) · [MANIFEST.md](MANIFEST.md) · [preprint v0.5](../preprint.md) · `experiments/e1-protocol.md` v1.1

## Precedence

On any conflict: **CONSTITUTION.md v1.0 > ADR-001 / ADR-002 > preprint / E1 protocol / PMI SPEC / code.** Earlier norms in GLOSSARY (axioms 1–9, permissions 1–4), MANIFEST (architectural axioms 1–8, continuous-calendar-existence, owner-provides-time, cannot-be-copied, layers-as-places, no-trust-needed), and THEORY (all must/forbidden language) are **superseded as norms** and retained as lineage only. The migration table is in ADR-002. Content fixes to preprint/E1/code against this CONSTITUTION are a separate step and are NOT applied here.

---

### P1. One semantic subject.
Statement: only the core K performs semantic acts: interpretation, attention, reasoning, intention, action. Φ stores state and does nothing semantic.
Violated if: any non-K component's output determines WHAT a record means, WHETHER it is kept/surfaced, or HOW it is paraphrased — including "deterministic" classifiers, extractors, or pre-filters.
Example: a regex that routes dates/sums to verbatim records without a model act violates; the same regex as a proposal the model confirms by `name` does not.

### P2. No external decider (trigger / rank / gate / veto).
Statement: no component outside K decides WHEN a memory act fires, WHICH traces surface for the current query, WHAT gate admits a write, or WHETHER a well-formed act executes. The executor executes; it never selects by meaning, never refuses by meaning.
Violated if: a reminder is pushed before a turn the model did not request; records are ordered/filtered by relevance, similarity, keywords, or query-dependence; a write is refused or rewritten for its content; an embedding/similarity symbol exists in the main-run path.
Example: loudest-N block appended to a `read` response the model called is compliant; the same block pasted before every user turn unasked is a violation (belongs in ablations as `loudest-N-auto on`).

### P3. Layers are speeds, not places.
Statement: a layer names a decay time constant τ, never a container, mailbox, or permission zone. All writes deposit across the speed spectrum per the registered τ set; no logic branches on layer-as-location; no veto, quota, or visibility rule keys on layer except the τ value itself.
Violated if: code routes, hides, prices, or refuses by layer name for any reason other than its τ; a default layer is silently assigned and then cited in layer-based claims.
Example: `layer="episode"` default that the executor fills in violates unless recorded as `unspecified (harness default)` and excluded from τ-based conclusions; friction tariff `c(τ)` is compliant, `c(layer-name-as-place)` is not.

### P4. Temperature-class dials only (enumerated, pre-registered, content-blind).
Statement: the owner may set ONLY the dials listed here, each continuous or scalar, each fixed before a run and frozen in the manifest: memory volume (bytes), forgetting tempo (record-age), τ set + τ-scale, friction meter schedule `c(τ)`, provenance cap table, injection N-cap, clock mode. No dial inspects content, assigns meaning, or takes a per-trace decision.
Violated if: a run uses an unlisted knob; a dial value changes mid-run unlogged; any dial's computation reads record content (beyond byte size / timestamps / counters); a "physics" claim has no manifest entry.
Example: `MMI_TAU_TICKS=50,200,1000` frozen pre-run is compliant; an operator retuning τ mid-run to rescue accuracy is a violation (new run required).

### P5. Acts of the model (explicit, complete, logged).
Statement: the ONLY writes to Φ are the model's explicit acts `name / repeat / connect / reconcile` plus explicit `read`; each act is a logged tool call with actor=K. Silence is not consent: missing parameters are errors or recorded `unspecified`, never silently completed by the executor. Every auto-anything (auto-write, auto-remind, auto-link, auto-extract) is NOT an act and belongs in ablations.
Violated if: any Φ record exists without a corresponding logged model act; any "unconscious" write fires without the core's own gate signal; any background process issues `connect`.
Example: dormancy replay that proposes candidates the core then `connect`s by act is compliant; a substrate process writing CONNECT records by itself violates (P1/P2).

### P6. Ticks are lived, counted by the stand, owned by the model.
Statement: abstract tick = one inference step of the instance. Stand counter = one executed storing act (sparse sampling of abstract ticks), advanced ONLY by the stand on WRITE/REPEAT/CONNECT/RECONCILE; READ/STATUS/`tick` calls never advance it. Dormancy is zero lived time unless the core itself works (background tick = core running with no user input, every act journaled as the core's). Wall-clock stamps NEVER enter amplitude.
Violated if: wall seconds affect any weight; `message_no`/exchange count is substituted for the stand counter; idle calendar time ages traces; a manual `tick` call advances the counter in tick mode.
Example: `weight=(1+repeats)·exp(−Δn/τ)`, `Δn=n_now−record_tick` is compliant; `exp(−dt_seconds/τ)` anywhere except the preregistered `decay-in-wall-clock` control ablation violates.

### P7. Provenance is capped physics, asserted by the model.
Statement: per-record source class is asserted by the model in the act call. The deployer's pre-registered cap table bounds initial amplitude only (`a(0) ≤ cap[class]`, uniform until implemented); the executor never reclassifies content and never infers class from content. Class assignment policy is a deployment choice, disclosed, and itself an attack surface.
Violated if: any component rewrites the model's asserted class; amplitude is set from content analysis; the $a_0$ table changes mid-run; a paper claims $a_0$ weighting the executor does not implement.
Example: model asserts `source=user`, executor applies `min(1.0, cap[user])` — compliant; extractor upgrades/downgrades class by scanning dates — violation.

### P8. Journal is append-only, hash-chained, separate from memory.
Statement: the journal is a complete chronological record, written by the environment, never by the model, never edited, never deleted; each entry hash-links the previous; archive moves preserve ids/fields and extend the chain; reads span active+archive by `ids`/`range` (recency-`last` covers active only, disclosed in `read` help and STATUS). Memory (selective, decaying, governed) and journal (complete, immutable, post-mortem) have separate retention/erasure rules.
Violated if: any mutation/deletion of a journal entry; archive move alters fields/ids/ticks; hash chain absent while P2 tamper-evidence is claimed as built; `last`-only blindness undisclosed to the model.
Example: current reference executor (no hash chain) is compliant ONLY while P2 is claimed "modulo host trust"; claiming cryptographic tamper-evidence on it violates.

### P9. Training shapes capacity; governance is post-boundary + held-out.
Statement: training (including oracle-shaped rewards) builds the CAPACITY to perform acts; it MUST NOT decide the CONTENT of any live biography. The oracle/ledger/judge never enter Φ, context, notes, or journal during a run and never trigger/filter acts; they score post-hoc only. Governance is demonstrated on held-out biographies with no oracle present (E1–E3 on novel corpora), never by oracle overlap (E5 bounds, not measures, governance).
Violated if: ledger/judge output reaches any arm's context or Φ; a run is rewarded/filtered mid-run by oracle score; E5 precision/recall is cited as self-governance evidence; training corpora leak into test biographies unreported.
Example: "E5=0.9, therefore self-governed" violates; "E5=0.9 capacity; E1–E3 held-out show governed behavior past the boundary" complies.

### P10. Precedence and honesty labels.
Statement: on conflict, CONSTITUTION.md v1.0 > ADR-001 > preprint/E1/SPEC/code. MANIFEST "continuous calendar existence," "owner provides time," "layers exist as places," "cannot be copied," and "no trust needed" are superseded as norms (retained as lineage). Every report states its configuration point (substrate × topology × act-training), which dials were frozen, which ablations were on, and what is NOT claimed (parametric substrate, trained acts, hash chain, $a_0$ weighting) until built.
Violated if: a result is reported without its axis coordinates and frozen manifest; an ablation flag leaks into a main-run claim; a wall-clock/surrogate/RAG control is cited as PlastFormer behavior.
Example: "Arm C (symbolic × split × prompted, ticks, τ=50/200/1000, N=12, $a_0$=uniform, friction metered-not-refused, surrogate off, RAG-read off) retained X" complies; "memory works" without coordinates violates.
