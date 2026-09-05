# AGENTS.md — PlastFormer (PUBLIC)

This file is public and harmless. It tells any agent how to read and extend this repository without breaking the architecture or the public/internal boundary.

## 1. Read order

1. `docs/CONSTITUTION.md` v1.0 FIRST — binding norms P1–P10 with "Violated if" tests. On any conflict, CONSTITUTION wins.
2. `docs/ADR-001-plastformer-transition.md`, then `docs/ADR-002-docs-architecture.md` (file semantics + norm migration table + public/internal boundary).
3. `docs/THEORY.md` (mechanisms only) + `docs/GLOSSARY.md` (dictionary only) + `docs/MANIFEST.md` (declaration only).
4. `preprint.md` v0.5 (§1 split, §3.3, §3.7, §4.3, §7 E5) and `experiments/e1-protocol.md` v1.1 (§5, §7–8) — claims under test, not norms.
5. `docs/INTERNAL.md` MUST NOT exist in public snapshots (gitignored; see ADR-002). If you see it locally, its contents never leave the machine.

## 2. File map

| Path | Semantics | Normative? |
|---|---|---|
| `docs/CONSTITUTION.md` | enforceable postulates P1–P10, each with statement + "Violated if" test + example | YES — highest |
| `docs/ADR-001*`, `docs/ADR-002*` | decisions, file semantics, migration table, boundary | decisions bind; history does not |
| `docs/THEORY.md` / `THEORY.ru.md` | mechanisms description only (multi-tau decay, two clocks, reconcile, background tick, cascade anchors) | NO |
| `docs/GLOSSARY.md` | dictionary term→definition (EN with RU term in brackets) | NO |
| `docs/MANIFEST.md` | outward declaration (claim, positioning, lineage, working-name note) | NO |
| `preprint.md`, `experiments/e1-protocol.md` | claims + pre-registered evaluation | under CONSTITUTION, not above it |
| `docs/PMI-SPEC.md` (when present), code | implementation | lowest; must satisfy CONSTITUTION |
| `docs/INTERNAL.md`, `drafts/*-private*`, `*.local`, `.env`, `runs/*-secret*` | internal only, gitignored | NEVER public |

## 3. Forbidden patterns (main run)

Text and code patterns that violate CONSTITUTION in the main run. Each belongs in a named ablation only, default off, manifest-logged:

- **No embeddings/similarity in the main path.** No `embedding`, `similarity`, relevance ranking, keyword match, or query-dependent selection for reads. Read physics is amplitude-only loudest-N in response to the model's own `read`. (P2)
- **No auto-write.** No "every experience leaves a trace" rule on the symbolic stand. Only the model's explicit `name / repeat / connect / reconcile` write to Φ. Core-gated unconscious register is parametric-future only. (P5)
- **No auto-remind / pre-turn push.** The stand never injects `<<PMI>>` before a user turn unasked. Loudest-N context is a `read` response field only. Auto-injection lives only in ablation `loudest-N-auto on` with opt-out and act-log accounting. (P2)
- **No auto-link / auto-extract.** No background process issues `connect`; no deterministic pre-extractor writes to Φ or sets amplitude. Proposals require model confirmation by act. (P1/P5/P7)
- **No silent defaults (including layer).** Missing parameters are errors or recorded `unspecified`, never silently completed. `layer="episode"` as a silent default is forbidden; fallbacks must be labeled and excluded from layer-based claims. (P3/P5)
- **Tick rule.** 1 stand tick = 1 executed storing act (WRITE/REPEAT/CONNECT/RECONCILE), counted by the stand. READ/STATUS/`tick` calls never advance it. Wall-clock seconds never enter amplitude. Dormancy is zero lived time; background tick = core running with no user input, every act journaled as the core's. (P6)
- **Dials frozen pre-run in manifest.** Only the P4 enumerated dials (volume, forgetting tempo, τ set + scale, friction meter schedule, provenance cap table, injection N-cap, clock mode). No mid-run retuning; no content-reading dial. (P4)
- **Judge/ledger never feed back into runs.** Oracle/ledger/judge score post-hoc only; they never enter Φ, context, notes, or journal and never trigger/filter acts. E5 bounds capacity, it does not measure governance. (P9)
- **Refs carry sources.** `connect`/`reconcile` records carry `refs` to source records; sources are never mutated; archive moves preserve ids/fields/ticks; `last`-reads-active-only is disclosed in `read` help and STATUS. (P8)

## 4. How to reproduce E1

1. Read `experiments/e1-protocol.md` v1.1 fully (§5 stand TZ, §7–8 scoring/isolation).
2. Freeze the P4 dial set in a run manifest before the run (clock mode `ticks`, τ set, N-cap, provenance caps, friction schedule); record axis coordinates `symbolic × split(PMI) × prompted`.
3. Run the main configuration with all ablations OFF (`RAG-style read` off, `unconscious-surrogate` off, `decay-in-wall-clock` off, `loudest-N-auto` off, `verbatim-extractor` off, `friction-veto` off). Main-run code path must contain no `embedding`/`similarity` symbol.
4. Report per P10: coordinates, frozen dials, ablations on/off, act log (counts/types of acts), and what is NOT claimed (parametric substrate, trained acts, hash chain, $a_0$ weighting) until built.

## 5. Copying and attribution

- Ideas: free to use from prior work (Titans, MemoryBank, Zep, ...) — with citation in the paper and docs. Claiming a copied idea as our own violates P10 and scientific ethics; the paper already declares the compositional claim and cites ingredients.
- Code: only MIT/BSD/Apache-2.0 sources may enter this Apache-2.0 repo, with copyright + license preserved and noted in NOTICE/CREDITS. GPL/AGPL code must not be merged. No license = no use.
- Models: Gemma derivatives (our unified artifact) are governed by Gemma Terms of Use — re-read them before any public distribution of model weights.
- Our own code is Apache-2.0: anyone may copy it. Our defense is priority (DOI, arXiv timestamps) and citation, per ADR-001 lineage.

## 6. Commit discipline (public, harmless)

- Do NOT commit. Do NOT push without the owner's explicit command in this session.
- Before any push: read this repo's README/ADR rules; push only the remote the owner named; never copy one project's push config to another.
- Public snapshots contain only released files (see ADR-002 boundary). When in doubt, keep local.
