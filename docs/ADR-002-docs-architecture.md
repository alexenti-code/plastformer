# ADR-002 — Docs architecture: strict file semantics + public/internal split

**Status:** ACTIVE. **Date:** 2026-09-05. **Owner:** Alex. **Author role:** docs architect (agent).

> Note (2026-09-06): the P-numbers in the traceability tables below refer to the article numbering current when this ADR was written (CONSTITUTION v1.0/v2.0). In CONSTITUTION v2.1 (ADR-004) the journal article was removed and the numbering shifted; the current numbering is authoritative in `CONSTITUTION.md`.
**Builds on:** [ADR-001](ADR-001-plastformer-transition.md). **Enforces:** [CONSTITUTION.md](CONSTITUTION.md) v1.0.
**Scope note:** this ADR restructures documentation ONLY. The 15 content fixes from `drafts/constitution-audit.md` (Fix list 1–15) are NOT applied to preprint / E1 / code here; they come next, against the new CONSTITUTION.

## 1. Strict file semantics

| File | Semantics | May contain | Must NOT contain |
|---|---|---|---|
| `docs/THEORY.md` + `THEORY.ru.md` v4.0 | mechanisms description only | multi-tau decay, two clocks, reconcile, background tick as core-without-input, cascade anchors, descriptive act/time accounts | must/forbidden norms, "Violated if" tests, axioms, permissions, punishments |
| `docs/GLOSSARY.md` v4.0 | pure dictionary | term → definition (EN with RU term in brackets) | axioms, permissions, punishments, norms, "Violated if" |
| `docs/MANIFEST.md` v4.0 | outward declaration only | claim, positioning, lineage, working-name note, honest boundary, research questions | enforceable norms; old norms appear only as notes marked SUPERSEDED with a CONSTITUTION pointer |
| `docs/CONSTITUTION.md` v1.0 | binding norms | postulates P1–P10, each = statement + "Violated if" test + example; precedence header | mechanisms exposition, dictionary entries, lineage narrative |
| `AGENTS.md` (repo root, PUBLIC) | agent read order, file map, forbidden patterns, E1 reproduction, commit discipline | public, harmless instructions | secrets, internal paths, unpublished results |
| `docs/INTERNAL.md` (gitignored) | what NEVER goes public | keys/rodnik, private code classes, unpublished results, owner infra/data, session logs, investor materials, roadmap | — (never published) |

Precedence: **CONSTITUTION > ADR > preprint / E1 / SPEC / code**; MANIFEST and pre-ADR-002 GLOSSARY/THEORY norms are superseded (lineage only).

## 2. Norm migration table (nothing dropped silently)

Each row: one removed norm → its new home (CONSTITUTION postulate with test). "Old location" uses v3.0 file/section.

### From THEORY.md v3.0 → CONSTITUTION

| ID | Old location | Removed norm (gist) | New home |
|---|---|---|---|
| T1 | §1.3–1.4 | "No external logic classifies experience; external write command = forbidden adapter" | P2 (no external decider: gate/rank) + P5 (acts explicit/logged) |
| T2 | Axioms §1–9 block | Axioms 1–9 as theory statements (one subject, engine-of-memory, passive Φ, immutability, autobiography, nesting, bi-temporality, continuity, own time) | P1–P9 (P1 subject; P2 decider ban; P3 speeds; P6 ticks; P7 provenance; P8 journal; P9 training/governance; P5 acts) |
| T3 | §2.1 | "No thresholds, no content conditions, no rankers" (stand spec) | P2 (rank/gate ban) + P4 (content-blind dials) |
| T4 | §1.2 / §5 | "An external controller is forbidden" (write competence, write gates) | P2 + P5 |
| T5 | §2.2 | "Set by the owner; changed only by the owner; constitutional boundary: continuous quantities, no thresholds/content conditions" | P4 (enumerated pre-registered content-blind dials) |
| T6 | §2.2 | "temperature does not decide WHAT…" (dials decide nothing) | P4 |
| T7 | §5 read | "Any relevance ranker is an external decider, violation of axiom 2" | P2 |
| T8 | §5 write | "Every experience leaves a trace" auto-write + surprise-gate qualification | P5 (auto-write belongs in ablations; core-owned gate only) |
| T9 | §4 background/gap | Gap-fires-surprise-gate + `reconcile` as required act; substrate-self-linking excluded | P5 + P6 + P9 (background tick = core-without-input; substrate-self-linking = ablation) |
| T10 | §6–§7 | "Personal data live only in Φ" (permission), "copying creates a branch" (axiom 8), "continuity = Φ line" (axiom 8), review-table verdicts | P7 (provenance caps) + P8 (journal/memory separation) + P10 (copy-as-branch honesty label) |
| T11 | §4 | Dormancy/wall-clock handling ("looking at the calendar ages the traces" rejected; stamps weightless) | P6 (stamp firewall: wall seconds never enter amplitude) |

### From GLOSSARY.md v3.0 → CONSTITUTION

| ID | Old location | Removed norm (gist) | New home |
|---|---|---|---|
| G1 | Axioms 1–9 | All nine axioms as glossary norms | P1–P9 (same mapping as T2) |
| G2 | Permissions 1–2 | "Personal data permitted; live only in Φ" | P7 + P8 |
| G3 | Permission 3 | "Dedicated region permitted; owner allocates volume, preservation, ticks" | P4 (volume/clock-mode dials) + P6 (stand counts, model owns) |
| G4 | Permission 4 | "Copying Φ permitted; copy creates a branch" | P10 (+ P8) |
| G5 | Term PMI | "Not an external mechanism/adapter…" | P1 + P2 |
| G6 | Term Memory act | "Conscious act; not a side effect, not automatic" | P5 |
| G7 | Term Stand | "Write commands come from the model; stand only executes" | P2 + P5 |
| G8 | Term Journal | "Never written by the model; guarantees integrity" | P8 |

### From MANIFEST.md v3.0 → CONSTITUTION (kept as SUPERSEDED lineage notes)

| ID | Old location | Removed norm (gist) | New home |
|---|---|---|---|
| M1 | Declaration/Proposal | "continuous existence in time" / calendar continuity | P6 (+ P10 supersede note) |
| M2 | Division of roles | "the human provides … physical time" / owner gives ticks | P6 (stand counts storing acts; model owns ticks) |
| M3 | Nested timescales | "layers exist" as places (container reading) | P3 |
| M4 | Unique instances | "cannot be copied" | P10 (copy = branch) |
| M5 | Bi-temporal facts | "No act of trust is required…" | P7 |
| M6 | Architectural axioms 1–8 | All eight axioms as manifesto norms | P1–P10 (P1 subject, P2 decider, P3 speeds, P4 dials, P5 acts, P6 ticks, P7 provenance, P8 journal, P9 training, P10 labels) |
| M7 | Division of roles | "importance/contradiction/connection/recall/reconciliation must live inside" as manifesto rule | P1 + P2 + P9 |

## 3. Public/internal boundary

Substance carried over from `/Users/alex/matryoshka/RESEARCH_SCOPE.md`:

- **Public:** conceptual architecture, terms, core distinctions, high-level evaluation direction, limited experimental code for controlled refutation tests.
- **Never public unless explicitly published in a later signed release:** exact parametric-update mechanisms; learning objectives/loss/update schedules; topologies/tensor layouts/layer placement; temporal-binding/interference/consolidation mechanisms; proprietary datasets, private evaluation records, commercial deployment data; production infra, credentials, integrations, client info, operational policies; trade-secret / patent-subject implementation details.
- **PlastFormer additions:** keys/rodnik, run-secret manifests (`runs/*-secret*`), session logs, investor materials, future roadmap, `docs/INTERNAL.md`, `drafts/*-private*`, `*.local`, `.env`.

Rule: when in doubt, keep local; the public mirror contains only released snapshots. Enforcement: `.gitignore` covers `docs/INTERNAL.md`, `drafts/*-private*`, `*.local`, `.env`, `runs/*-secret*`.

## 4. What this ADR does NOT do

- No content fixes to `preprint.md`, `experiments/e1-protocol.md`, or code (audit Fix list 1–15 untouched).
- No terminology changes beyond the ADR-001 renames (PlastFormer, PMI, plastic module Φ).
- No publication step: MANIFEST v4.0 remains "Draft for owner review — not published".
