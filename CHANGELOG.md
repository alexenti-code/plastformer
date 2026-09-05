# Changelog

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
