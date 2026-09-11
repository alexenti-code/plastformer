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

The nearest work: design and assemble the single file A = (K, Φ):

1. freeze the owner decisions: K/Φ proportion, storage precision, the Φ write mechanism;
2. prepare the file: K region = the current 4-bit core, Φ region initialized;
3. the one instruction pass embeds the Instruction (material v0.3, grammar v0.2.0) into the K region; freeze K;
4. verify: grammar ≥ 95 %, acts fire unprompted, reads from Φ work, no core degradation;
5. life: perception → Φ1 → acts → Φ2, writes into the Φ section of the file;
6. then the E1 examination (protocol to be rebuilt against A = (K, Φ) — the current `experiments/e1-protocol.md` is SUPERSEDED).

Assembly material (the raw material of the one instruction pass, the base checkpoint, the grammar v0.2.0) is kept under `experiments/o8-pass/` and `experiments/act-grammar/` as **assembly material**; it is not part of the artifact.

## 6. Commit discipline

- Version control is the agent's responsibility: commit and push the project's own work without asking. The owner does not track commit hashes, versions or CHANGELOG details.
- Before any push: read this repo's rules; push only the remote the owner named; never copy one project's push config to another.
- Ask the owner only in two cases: the repo has a written prohibition, or the push would include secrets or weight files.
- Public snapshots contain only released files (see ADR-002 boundary). When in doubt, keep local.
- Ideas from prior work are used with citation (Titans, MemoryBank, Zep, ...). Code entering this Apache-2.0 repo must be MIT/BSD/Apache-2.0 with attribution; GPL/AGPL must not be merged. Gemma-derived weights follow the Gemma Terms of Use.
