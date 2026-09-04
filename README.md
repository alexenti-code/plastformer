# PlastFormer

**Self-governed idiographic memory for frozen-core transformers.**

- **Paper (draft v0.3):** [`preprint.md`](preprint.md)
- **Naming:** PlastFormer — the system; idiographic memory — the property it implements (frozen nomothetic core + plastic per-instance biography, after Windelband)
- **Author:** Alexey Voronin, Aurum Estate LLC
- **License:** Apache 2.0
- **Status:** architecture + pre-registered evaluation design; no measured results yet

## What this is

A transformer memory architecture in which every semantic decision about memory — what to name, what to repeat, what to connect, what to surface — is made by the model itself, while the environment provides only physics: write-cost schedule, decay constants, tick rate, immutability of recorded content, and an external append-only audit journal.

The core split (after Windelband): a frozen **nomothetic core** (general laws: language, reasoning, culture) plus a plastic **idiographic module** — the unique biography of one instance.

## Emergent claims (falsifiable)

- **P1 — Physical time:** age is read from amplitude profiles, duration from tick counts; not stored as text, not forgeable by retelling.
- **P2 — Tamper-evident biography:** content immutable, amplitude decays by physics; rewriting one's past costs full re-consolidation under an environment-set price.
- **P3 — Rising poisoning cost:** poison must survive decay; survival requires repetition — a conscious, trainable act.

## Evaluation (planned)

Anchored in LongMemEval (S/M) and LoCoMo, plus custom experiments E1–E5. See Section 7 of the preprint. Results pending — by design, this draft claims an architecture, not outcomes.

## Naming

**PlastFormer is the system name; idiographic memory is the concept term — brand in the title, differentiator in the subtitle** (the pattern of MemGPT and Titans). Formerly circulated under the working name "Matryoshka" — renamed to avoid collision with Matryoshka Representation Learning and the nested-granularity namespace; the mechanism is superposition of decaying amplitudes, not nesting. The first dated public artifact (Sept 4, 2026) lives in [`alexenti-code/idiographic-memory`](https://github.com/alexenti-code/idiographic-memory); this repository is the canonical home. Former prototype repositories: `matryoshka` (theory, experiments), `matryoshka-mmi` (module prototype) — to be consolidated here.

## Background

Russian-language research essays (nos. 21–24) documenting the architectural reasoning: [aura.kim/research.html](https://aura.kim/research.html) — commentary, not the claim.

## Citation

See [`CITATION.cff`](CITATION.cff) (Zenodo DOI will be added upon first release).
