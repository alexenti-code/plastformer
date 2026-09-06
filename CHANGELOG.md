# Changelog

## [0.6] — 2026-09-06

### Changed
- `docs/CONSTITUTION.md` / `docs/CONSTITUTION.ru.md` → **v3.0, NORMATIVE (owner edition 2026-09-06)**: postulates-first structure — ontology intro, Foundations O-1–O-11, compliance tests C1–C8, lineage appendix. Copy-as-branch wording replaced by plain duplication; the memory-keeping skill is set in one pass (no retraining framing); layers-as-speeds and the weight formula promoted to Foundations; no negative argumentation.
- `experiments/e1-protocol.md` v1.2 → **v1.3**: four-arm scheme per owner directive — **A vs C** (plain chat: transformer vs PlastFormer, no wrapper) and **B vs D** (the identical wrapper agent over both models; the variable inside each pair is the model only). Main test: **B vs D**. Predictions PR8–PR9 added; PR1–PR4 realigned; refutation criteria restated positively; context budget 32768 tokens.
- `preprint.md` §7 Evaluation: E1 references updated to protocol v1.3 and the four-arm scheme.
- Cross-document renumbering to CONSTITUTION v3.0 (P1–P10 → O-1–O-11 / C1–C8): `docs/THEORY.md`, `docs/THEORY.ru.md`, `docs/MANIFEST.md`, `docs/GLOSSARY.md`, `AGENTS.md`, `experiments/organ-dataset/README.md`, `experiments/e1-protocol.md`. Mapping recorded in ADR-002.
- `docs/ADR-003-constitution-v2.md`: approval status updated (v3.0 supersedes the v2.x numbering).
- Wording: "falsifier"/"falsifiable" replaced by "refutation criterion"/"refutable" across active documents (owner directive 2026-09-06).
- Earlier in 0.6: erasure = deletion of the Φ section (core survives), crypto-erasure demoted to an optional protection; journal excluded from the architecture (ADR-004); tamper-evidence claims withdrawn; derived-traces topic removed (one plastic section = one subject); security scope withdrawn (threat model §5, P3, E2).

## [0.5] — 2026-09-05

### Changed
- `preprint.md` v0.3 → v0.5. One architecture, three configuration axes (substrate / topology / act training) replace the "S/P realizations" framing. PMI (Plastic Memory Interface, formerly MMI) defined as the split-topology special case (§3.9). Δn in lived ticks; two clocks and `reconcile` (§4); "compositional" replaces "emergent"; P2 restated as tamper-evident; P3 in lived ticks; Related Work extended (MemoryBank, A-MEM, HippoRAG, Metis, Memory-as-Ontology, Nested Learning, sleep-time compute); E3b and E6 added; unverified references flagged `[verify]`.
- `experiments/e1-protocol.md` v1.0 → v1.1. Arm C labelled as stand configuration (symbolic × split(PMI) × prompted); relevance-ranked read removed from the main run (kept as ablation); embedding-surprise surrogate off in the main run; decay in ticks; `reconcile` act added; Arm B gets timestamped notes; act-log metrics.
- `README.md`, `CITATION.cff` synchronized.

### Added
- `docs/ADR-001-plastformer-transition.md` — decision record for the transition from the working name "Matryoshka": what in the theory is kept, what changes, document map, work orders for the E1 protocol and the PMI executor v0.6.
- `drafts/` — preserved v0.3 preprint, v0.4 architect base, v1.0 E1 protocol.

## [0.3] — 2026-09-04
- Initial preprint v0.3 and E1 protocol v1.0.
