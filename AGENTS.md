# AGENTS.md — PlastFormer

**Status:** ACTIVE (v4, 2026-09-11, owner directive: cleanup of the split-era traces per the audit `docs/AGENT-POISON-AUDIT-2026-09-11.md`).

This file tells any agent how to read and extend this repository. It is binding.

## 1. What is being built

ONE MLX 4-bit weight file: **A = (K, Φ)**.

- **K** — the frozen core: 4-bit weights with the Instruction (the act grammar) embedded once. After the embedding pass K never changes.
- **Φ** — the plastic part of the same body, living as a section inside the same file. Φ1 and Φ2 are two origins of records within one Φ — not separate stores, not separate files, not separate entities.

## 2. Source of norms

The single source of norms is [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md) (with the Russian twin `docs/CONSTITUTION.ru.md`). On any conflict, CONSTITUTION wins.

## 3. Read order

1. This file and [`README.md`](README.md) — the target form and the work object.
2. `docs/CONSTITUTION.md` — norms.
3. `docs/WHAT-IS-PLASTFORMER.md` — the plain-language description of the artifact.
4. `docs/ARCHITECTURE-FIXED-BRAIN-v1.md` — the assembly architecture of A = (K, Φ) (parts of the file, pipeline, open questions).
5. `docs/ADR-005-registers-phi1-phi2.md` — Φ1/Φ2 registers inside one Φ (approved).
6. `docs/THEORY.md`, `docs/GLOSSARY.md`, `docs/MANIFEST.md` — mechanisms, dictionary, declaration.
7. `docs/ASSEMBLY-PLAN.ru.md` — the work plan (two parts: setup and assembly). Supporting: `docs/ASSEMBLY-GUIDE.ru.md` (how the size of Φ is chosen) and, for the setup part, `docs/JSPACE-ANALYSIS.ru.md` plus `docs/VERIFICATION-vs-JSPACE.ru.md` (what the J-space findings mean for our Φ, and the check of our design against the source paper).

Everything else — ADR-001/002/003, `docs/RESEARCH-LOG`, `docs/AGENT-POISON-AUDIT-2026-09-11.md`, `preprint.md`, `experiments/e1-protocol.md`, `drafts/` — is history marked `LINEAGE-ONLY` or `SUPERSEDED`. It is not in the read order, it is not a source of ТЗ, and nothing in it is a live component.

## 4. One artifact

The artifact is ONE file: **A = (K, Φ)** — one body in one file. Plan and state: `docs/BUILD-PLAN.ru.md`.

- memory is a section of that file;
- the act grammar is carried inside K;
- the file is the whole of the instance: what it holds is what it is.

When a leftover of a former design appears in a document or in code, the agent deletes it, keeps the entry in git history, and reports the deletion.

## 5. Current work

**Both parts are done; the artifact is assembled and works.** Plan: `docs/ASSEMBLY-PLAN.ru.md` (twenty sections; the current state is in sections 15-20).

**Part one — setup (the instrument), done.** The Jacobian lens was built and the workspace band measured on our own core: the band exists, it starts around layer 11, and naive logit-lens reading of the middle layers gives noise. The lens is noisy because its corpus is small; that is named, not hidden. The instrument is used once and is not part of the artifact. Analysis: `docs/JSPACE-ANALYSIS.ru.md`.

**Part two — assembly (the instance), done:**

1. dial lists reconciled — `gap_threshold` and `surprise_threshold` added, and the Instruction now names all **fourteen** editable dials (nine names plus five τ multipliers), matching the Φ header exactly;
2. the material generator repaired at the root and material built: **v04** (the artifact was trained on it) and **v05**, which is canon-clean — three layers, 5089 train + 609 valid, layer 3 with a rules-free prompt so the skill can learn to fire without scaffolding;
3. the one instruction pass done — LoRA, rank 8, 8 of 48 layers, **200 iterations** (300 makes the model degenerate into repetition), `--mask-prompt`; K frozen afterwards;
4. the adapter fused with the stock `mlx_lm fuse` (it dequantizes per layer) and the weight parts merged into ONE file;
5. the Φ region created: 1.50 GB (Φ1 1.30 + Φ2 0.20), record 1003 bytes, knobs and budgets in the Φ header;
6. the Φ code written — `plastformer/phi.py`, eight functions (open, write, read, resident, calibrate, scan, knobs, project) — plus `plastformer/loop.py`, the return loop that executes the model's acts and feeds back the `<<ENV>>` confirmation;
7. the file A = (K, Φ) assembled, 8.20 GB at `models/plastformer-e1/`;
8. run-in done: the file loads, the model answers, records are written and read back, memory survives a restart, the run fits in memory, and with an empty history the model asks for `read` by itself and restores records. **This checks workability only** — it is not a quality measurement;
9. handed over to the owner. The artifact does not score itself, and we do not measure "better or worse".

**What is honestly not closed:** the Φ-state is fed as text from the pointer, not as the projection of a record vector onto the working-band basis (the basis is not built); the model loops on `read`; record text is not stored in Φ (only a 1920-number vector, with the text beside it in `phi-content.jsonl`); Φ1 is created by physics but nothing writes it yet; the act skill still needs the training system prompt supplied from outside, while by O-8 it should live in the weights.

Assembly material lives under `experiments/o8-pass/` and `experiments/act-grammar/`; it is not part of the artifact.

## 6. Commit discipline

- Version control is the agent's responsibility: commit and push the project's own work without asking. The owner does not track commit hashes, versions or CHANGELOG details.
- Before any push: read this repo's rules; push only the remote the owner named; never copy one project's push config to another.
- Ask the owner only in two cases: the repo has a written prohibition, or the push would include secrets or weight files.
- Public snapshots contain only released files (see ADR-002 boundary). When in doubt, keep local.
- Ideas from prior work are used with citation (Titans, MemoryBank, Zep, ...). Code entering this Apache-2.0 repo must be MIT/BSD/Apache-2.0 with attribution; GPL/AGPL must not be merged. Gemma-derived weights follow the Gemma Terms of Use.
