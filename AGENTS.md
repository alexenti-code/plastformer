# AGENTS.md — PlastFormer

**Status:** ACTIVE (v3, 2026-09-10, owner directive: split-architecture traces eliminated).

This file tells any agent how to read and extend this repository. It is binding.

## 1. What is being built

ONE MLX 4-bit weight file: **A = (K, Φ)**.

- **K** — the frozen core: 4-bit weights with the Instruction (the act grammar) embedded once. After the embedding pass K never changes.
- **Φ** — the plastic substrate of the same instance, living as a section inside the same file. Φ1 and Φ2 are two origins of records within one Φ — not separate stores, not separate files, not separate entities.
- Deleting the Φ section removes the biography; K survives. Copying the Φ section creates a copy of the memory line. Moving the file moves the instance. Outside the file there is no instance state: no state folder, no vector bank, no companion process, no separate Instruction file.

## 2. Source of norms

The single source of norms is [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md) (with the Russian twin `docs/CONSTITUTION.ru.md`). On any conflict, CONSTITUTION wins.

## 3. Read order

1. This file and [`README.md`](README.md) — the target form and the work object.
2. `docs/CONSTITUTION.md` — norms.
3. `docs/WHAT-IS-PLASTFORMER.md` — the plain-language description of the artifact.
4. `docs/ARCHITECTURE-FIXED-BRAIN-v1.md` — the assembly architecture of A = (K, Φ) (sections, pipeline, open questions).
5. `docs/ADR-005-registers-phi1-phi2.md` — Φ1/Φ2 registers inside one Φ (approved).
6. `docs/THEORY.md`, `docs/GLOSSARY.md`, `docs/MANIFEST.md` — mechanisms, dictionary, declaration.

Everything else — ADR-001/002/003, `docs/RESEARCH-LOG`, `preprint.md`, `experiments/e1-protocol.md`, `drafts/` — is history marked `LINEAGE-ONLY` or `SUPERSEDED`. It is not in the read order, it is not a source of ТЗ, and nothing in it is a live component.

## 4. Forbidden: the split architecture must not return

Do not recreate, repair, "improve" or resurrect the former split scheme ("model here, memory there", "core plus an external bank", "state folder", "model plus an adjacent system"). It was removed from the repository on 2026-09-10 and is not an object of further development. In particular:

- no external bank of vectors, no `vectors*.npy` / `amplitudes*.npy` / `.npz` projector files, no `meta.jsonl` state, no `section-phi/` directory;
- no state folder next to the model; every save writes the single file A = (K, Φ);
- no separate Instruction file or launch path of the form "core + external Φ";
- no adapter/LoRA/base+adapter pair as a form of the artifact — the Instruction lives inside K;
- no `adapter_path` / `adapters_alpha` in any launch path of the artifact;
- no harness / stand / executor / wrapper as an architectural entity (development instrumentation that runs the physics is allowed, but it is never part of the artifact and never appears in launch instructions of the model);
- no "PMI", "MMI", "split topology", "symbolic surrogate", "trained" as an architecture state (the canonical act-state value is **instructed**).

History survives only in git history and in files headed `LINEAGE-ONLY` / `SUPERSEDED`; such files are outside the read order, and their historical terms never act as a source of ТЗ.

## 5. If you find separate Φ files

If you encounter separate Φ files, a `vectors.npy`/`amplitudes.npy` bank, a `section-phi/` directory, an `adapter_path` in a launch config, or any other split-era artifact: do NOT repair, restore, port, rename or modernize them. Classify them as removable legacy and delete them (or leave them only in git history). Report the deletion.

## 6. Current work

The nearest work: design and assemble the single file A = (K, Φ):

1. freeze the owner decisions: K/Φ proportion, storage precision, the Φ write mechanism;
2. prepare the file: K region = the current 4-bit core, Φ region initialized;
3. the one instruction pass embeds the Instruction (material v0.3, grammar v0.2.0) into the K region; freeze K;
4. verify: grammar ≥ 95 %, acts fire unprompted, reads from Φ work, no core degradation;
5. life: perception → Φ1 → acts → Φ2, writes into the Φ section of the file;
6. then the E1 examination (protocol to be rebuilt against A = (K, Φ) — the current `experiments/e1-protocol.md` is SUPERSEDED).

Assembly material (the raw material of the one instruction pass, the base checkpoint, the grammar v0.2.0) is kept under `experiments/o8-pass/` and `experiments/act-grammar/` as **assembly material**; it is not part of the artifact.

## 7. Commit discipline

- Do NOT commit. Do NOT push without the owner's explicit command in this session.
- Before any push: read this repo's rules; push only the remote the owner named; never copy one project's push config to another.
- Public snapshots contain only released files (see ADR-002 boundary). When in doubt, keep local.
- Ideas from prior work are used with citation (Titans, MemoryBank, Zep, ...). Code entering this Apache-2.0 repo must be MIT/BSD/Apache-2.0 with attribution; GPL/AGPL must not be merged. Gemma-derived weights follow the Gemma Terms of Use.
