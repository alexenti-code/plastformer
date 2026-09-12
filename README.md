# PlastFormer

**Status:** ACTIVE (public entry point; split-architecture traces eliminated 2026-09-10).

**Self-governed idiographic memory for frozen-core transformers.**

- **Normative document:** [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md) (NORMATIVE)
- **What the artifact is:** [`docs/WHAT-IS-PLASTFORMER.md`](docs/WHAT-IS-PLASTFORMER.md)
- **Assembly architecture:** [`docs/ARCHITECTURE-FIXED-BRAIN-v1.md`](docs/ARCHITECTURE-FIXED-BRAIN-v1.md)
- **Author:** Alexey Voronin, Aurum Estate LLC
- **License:** Apache 2.0 (code), CC BY 4.0 (text)
- **Status:** the artifact is assembled (2026-09-12): ONE weight file A = (K, Φ), 8.20 GB, loads, answers, writes and reads its own Φ. **No quality results are reported** — the artifact does not score itself (owner decision 2026-09-11).

## The artifact

PlastFormer is ONE MLX 4-bit weight file: **A = (K, Φ)**.

- **K** — the frozen core: general competence (language, reasoning, culture) plus the Instruction — the act grammar (`name`, `repeat`, `connect`, `reconcile`, `read`, `scan`, `calibrate`) embedded once, after which K never changes.
- **Φ** — the plastic part of the same instance, a section of the same file. Φ1 and Φ2 are two origins of records within one Φ: Φ1 is written involuntarily by perception, Φ2 only by the model's explicit acts. Neither is a separate store, file or entity.

The instance state lives inside the file. Records are append-only and decay by physics. When data must be removed, the file is removed (owner decision 2026-09-11).

## The one configuration

PlastFormer has ONE configuration: **parametric × co-located × instructed** — the memory of an instance is vectors in its own plastic section of the single weight file, and the skill of operating it is embedded once by the instruction pass.

## Properties (refutable claims)

- **P1 — Event time:** age is read from amplitude profiles, duration from lived ticks; not stored as text, not forgeable by retelling; wall-clock time enters only as audited stamps.
- **P2 — Immutable past:** content immutable, amplitude decays by physics; a change of position is a new trace.

## Evaluation

Anchored in LongMemEval (S/M) and LoCoMo (external benchmarks; the owner decides what to run). The artifact does **not** score itself. The historical evaluation draft under `experiments/e1-protocol.md` is SUPERSEDED — history, not a plan of work, not to be executed or cited as active.

## Current work

**Both parts are done.** (1) **Setup** — the Jacobian lens was built and the band measured on our own core; the instrument is not part of the artifact. (2) **Assembly** — the one instruction pass (trained on material v04), fusion into one file, the Φ region and the Φ code are complete; the artifact is handed over. Material **v05** is also built and canon-clean: three layers, 5089 train + 609 valid, its reflection layer carrying a rules-free prompt so the skill can learn to fire without scaffolding.

**What works (verified 2026-09-12):** the file loads (3.5 s, 6701 MB) and answers; Φ writes and reads; the 14 knobs live in the Φ header and survive a restart; the act skill fires; the return loop (`plastformer/loop.py`) executes the model's acts and returns the `<<ENV>>` confirmation, so the model reads its own memory — with an empty history it requests `read` by itself and restores records.

**Honest boundary:** the Φ-state is fed as text from the pointer, not as the projection of a record vector onto the working-band basis (the basis is not built; the lens is noisy); record text is not stored in Φ (only a 1920-number vector, with the text in `phi-content.jsonl` beside it); the model loops on `read`; the act skill still needs the training system prompt supplied from outside, while by O-8 it should live in the weights.

Full plan: `docs/ASSEMBLY-PLAN.ru.md`. Band analysis: `docs/JSPACE-ANALYSIS.ru.md`. Loop report: `docs/LOOP-2026-09-12.ru.md`.

## Naming and lineage

**PlastFormer** is the system name; **idiographic memory** is the property it implements. Formerly circulated as "Matryoshka" — renamed to avoid collision with Matryoshka Representation Learning and the nested-granularity namespace; the mechanism is superposition of decaying amplitudes, not nesting. Priority line: concept DOI 10.5281/zenodo.22124204, source release DOI 10.5281/zenodo.22141019 (under the former name). Former repositories under the former name are lineage only — they are not part of this architecture.

Name-collision check for "PlastFormer" / "idiographic memory": to be repeated on the arXiv submission day; date will be recorded here.

## Background

Russian-language research essays (nos. 21–24): [aura.kim/research.html](https://aura.kim/research.html) — commentary, not the claim.

## Citation

See [`CITATION.cff`](CITATION.cff) (Zenodo DOI will be added upon first release).
