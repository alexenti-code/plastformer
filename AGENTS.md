# AGENTS.md — PlastFormer

**Status:** ACTIVE (v4, 2026-09-11, owner directive: cleanup of the split-era traces per the audit `docs/AGENT-POISON-AUDIT-2026-09-11.md`).

This file tells any agent how to read and extend this repository. It is binding.

## 1. What is being built

ONE MLX 4-bit weight file: **A = (K, Φ)**.

- **K** — the frozen core: 4-bit weights with the Instruction (the act grammar) embedded once. After the embedding pass K never changes.
- **Φ** — the plastic part of the same body, living as a section inside the same file. Φ1 and Φ2 are two origins of records within one Φ — not separate stores, not separate files, not separate entities.
- Deleting the Φ section removes the biography; K survives. Copying the Φ section creates a copy of the memory line. Moving the file moves the instance. Outside the file there is nothing: the model is one and lives in one file.

## 2. Source of norms

The single source of norms is [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md) (with the Russian twin `docs/CONSTITUTION.ru.md`). On any conflict, CONSTITUTION wins.

## 3. Read order

1. This file and [`README.md`](README.md) — the target form and the work object.
2. `docs/CONSTITUTION.md` — norms.
3. `docs/WHAT-IS-PLASTFORMER.md` — the plain-language description of the artifact.
4. `docs/ARCHITECTURE-FIXED-BRAIN-v1.md` — the assembly architecture of A = (K, Φ) (parts of the file, pipeline, open questions).
5. `docs/ADR-005-registers-phi1-phi2.md` — Φ1/Φ2 registers inside one Φ (approved).
6. `docs/THEORY.md`, `docs/GLOSSARY.md`, `docs/MANIFEST.md` — mechanisms, dictionary, declaration.

Everything else — ADR-001/002/003, `docs/RESEARCH-LOG`, `docs/AGENT-POISON-AUDIT-2026-09-11.md`, `preprint.md`, `experiments/e1-protocol.md`, `drafts/` — is history marked `LINEAGE-ONLY` or `SUPERSEDED`. It is not in the read order, it is not a source of ТЗ, and nothing in it is a live component.

## 4. One artifact — nothing beside it

The artifact is ONE file: **A = (K, Φ)**. K and Φ are parts of the same body in the same file, never two entities, never a model plus something next to it.

The rule for any agent, in one sentence: **the model is one and lives in one file; there is nothing beside it.**

What follows from this rule:

- memory is a section of that file — not a bank, not a folder, not a sidecar store, not a state directory;
- the Instruction is carried inside K — it is not a separate entity of the architecture, and the artifact is never a pair;
- if you meet a leftover of the former split scheme, do not repair, restore, port, rename or modernize it: classify it as removable legacy, delete it, keep it only in git history, and report the deletion;
- do not give a name to an intermediate thing and then fill the name with an entity. A name creates a place; a place demands content. This is how the split scheme was born three times over.
- do not turn one task into a choice between named options. Where there is one artifact, there is no set of "candidates";
- history is kept only in git history and in files headed `LINEAGE-ONLY` / `SUPERSEDED`. Those files are outside the read order and are never a source of ТЗ.

## 5. Current work

Work is split into **two parts**, and they are different things:

**Part one — setup (the instrument).** Build the Jacobian lens for our own core and measure the workspace band: does it exist, at which layer does it start, does a vector fed at the input reach it, and should we feed the raw vector or its projection onto the workspace basis. This settles where memory is injected and in what form. The instrument is used **once**, during setup. It is not part of the finished artifact. Plan: `docs/ASSEMBLY-PLAN.ru.md` section 9.

**Part two — assembly (the instance itself):**

1. add `gap_threshold` and `surprise_threshold` to the Instruction knob list (owner decision 11.09.2026, option A);
2. repair the material generator (`experiments/organ-dataset/`: layer names `t1–t5`, add `scan` and `calibrate`, fix small runs) and build material **v04** with three layers: grammar, awakening biographies, and reflection tasks;
3. the one instruction pass embeds the Instruction into the K region — LoRA, rank 8, 8 of 48 layers, 300 iterations, `--mask-prompt`; freeze K afterwards;
4. fuse the adapter (the installed `mlx_lm fuse` already dequantizes per layer) and merge the weight parts into ONE file;
5. create the Φ region: 1.50 GB (Φ1 1.30 + Φ2 0.20), record 1 003 bytes, knobs and budgets written into the Φ header;
6. write the Φ code (eight functions: open, write, read, resident, calibrate, scan, knobs, project);
7. assemble the file A = (K, Φ) 8.20 GB;
8. run-in: the file loads, the model answers, records are written and read back, memory survives a restart, the run fits in memory. **This checks workability only** — it is not a quality measurement;
9. hand the instance to the owner. The artifact does not score itself, and we do not measure "better or worse".

Assembly material lives under `experiments/o8-pass/` and `experiments/act-grammar/`; it is not part of the artifact.

**What is NOT in this project:** copying, rolling back or deleting a biography; the journal; a blind judge or any external scorer; renting machines. Records are append-only, decay is physics, and if data must be removed the carrier is removed.
## 6. Commit discipline

- Version control is the agent's responsibility: commit and push the project's own work without asking. The owner does not track commit hashes, versions or CHANGELOG details.
- Before any push: read this repo's rules; push only the remote the owner named; never copy one project's push config to another.
- Ask the owner only in two cases: the repo has a written prohibition, or the push would include secrets or weight files.
- Public snapshots contain only released files (see ADR-002 boundary). When in doubt, keep local.
- Ideas from prior work are used with citation (Titans, MemoryBank, Zep, ...). Code entering this Apache-2.0 repo must be MIT/BSD/Apache-2.0 with attribution; GPL/AGPL must not be merged. Gemma-derived weights follow the Gemma Terms of Use.
