# PlastFormer

**Self-governed idiographic memory for frozen-core transformers.**

- **Paper (draft v0.5):** [`preprint.md`](preprint.md)
- **Pre-registered experiment E1 (v1.2):** [`experiments/e1-protocol.md`](experiments/e1-protocol.md)
- **Architecture decision record (transition from the working name "Matryoshka"):** [`docs/ADR-001-plastformer-transition.md`](docs/ADR-001-plastformer-transition.md)
- **Author:** Alexey Voronin, Aurum Estate LLC
- **License:** Apache 2.0 (code), CC BY 4.0 (text)
- **Status:** architecture + pre-registered evaluation design; no measured results yet

## What this is

PlastFormer is **one architecture**: a transformer with a frozen core and a plastic per-instance module, trained once to operate its own memory organ through acts — `name`, `repeat`, `connect`, `reconcile`. After that single training step the core is frozen. Every semantic decision about memory is the model's; the environment supplies only physics: write-cost schedule, decay constants in *lived ticks*, immutability of recorded content, and an external append-only journal.

The core split (after Windelband): a frozen **nomothetic core** (general laws: language, reasoning, culture) plus a plastic **idiographic module** — the unique biography of one instance.

## Three configuration axes

| Axis | Values |
|---|---|
| Substrate | parametric (vectors/weights, read through a trained interface) ↔ symbolic (records, read as tokens) |
| Topology | co-located (module inside the model) ↔ split via **PMI** — Plastic Memory Interface (core at a provider, module at the owner) |
| Act training | trained (organ trained once, core frozen after) ↔ prompted (acts given by system prompt) |

Target form: parametric × co-located × trained. Stand configuration used in E1: symbolic × split(PMI) × prompted. Both are PlastFormer; they differ in coordinates, not in architecture. **PMI** (formerly MMI) is the special case along the topology axis, not a different system.

## Compositional claims (falsifiable)

- **P1 — Event time:** age is read from amplitude profiles, duration from lived ticks; not stored as text, not forgeable by retelling; wall-clock time enters only as audited stamps.
- **P2 — Tamper-evident biography:** content immutable, amplitude decays by physics; silent rewriting is detectable; curation by omission is journaled, not prevented.
- **P3 — Rising poisoning cost in lived ticks:** poison must survive decay; survival requires repetition — a trainable act.

## Evaluation (planned)

Anchored in LongMemEval (S/M) and LoCoMo, plus E1–E6 and E3b. See preprint Section 7 and `experiments/`. Results pending — this draft claims an architecture, not outcomes.

## Naming and lineage

**PlastFormer** is the system name; **idiographic memory** is the property it implements. Formerly circulated as "Matryoshka" — renamed to avoid collision with Matryoshka Representation Learning and the nested-granularity namespace; the mechanism is superposition of decaying amplitudes, not nesting. Priority line: concept DOI 10.5281/zenodo.22124204, source release DOI 10.5281/zenodo.22141019 (under the former name). Former repositories: [`matryoshka`](https://github.com/alexenti-code/matryoshka) (theory, parametric stand — frozen, research scope), [`matryoshka-mmi`](https://github.com/alexenti-code/matryoshka-mmi) (PMI reference executor — transitional). Consolidation plan: `docs/ADR-001`.

Name-collision check for "PlastFormer" / "idiographic memory": to be repeated on the arXiv submission day; date will be recorded here.

## Background

Russian-language research essays (nos. 21–24): [aura.kim/research.html](https://aura.kim/research.html) — commentary, not the claim.

## Citation

See [`CITATION.cff`](CITATION.cff) (Zenodo DOI will be added upon first release).
