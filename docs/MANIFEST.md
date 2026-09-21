# PlastFormer: An Architectural Proposal for Transformers

**Version:** 4.2
**Status:** ACTIVE — declaration only, not published; norms live in CONSTITUTION.md
**Author:** Alexenti / AURA
**Repository:** alexenti-code/plastformer
**Lineage:** primary disclosure AURA-Retrieval, commit 539fc32 (2026-06-26); source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204
**Working name note:** earlier drafts circulated as "Matryoshka"; renamed to PlastFormer to avoid collision with Matryoshka Representation Learning and Matryoshka Diffusion. The name "Matryoshka" is retained for lineage/DOI only.
**Normative anchor:** this file declares a position and states no enforceable rules. Enforceable statements and tests live in [CONSTITUTION.md](CONSTITUTION.md); file semantics and the public/internal boundary are in [ADR-002](ADR-002-docs-architecture.md).

The assembly target is the single-file artifact A = (K, Φ); its address in this project is the ТЗ (`drafts/rebuild-private/TZ-REBUILD.ru.md`) and the assembly card `drafts/rebuild-private/work-05-assembly/TECH-CARD-P5-v1.ru.md`.

## Declaration

PlastFormer is an architectural proposal for transformer-based language models.

It proposes that a working language-model instance be given, as a matter of architecture, **one thing**:

1. its own plastic section Φ of the same weight file, governed by its own acts — `name` / `repeat` / `connect` / `reconcile` / `read` / `scan` / `calibrate` — the rules of which are embedded by a one-time instruction pass (the act grammar), after which the core is frozen.

This is a proposal of one architecture for all transformers: one weight file whose frozen part carries general competence and whose plastic part, in the same file, carries the biography of one instance, plus the model's own acts, the rules of which are embedded by a one-time instruction pass. It is not a memory file format, not an algorithm, not a retrieval wrapper, not a second reasoning agent, not a prompt assembly system, not an orchestration layer, and not a mechanism for altering the pretrained core. The configuration of the artifact is single: parametric × co-located × instructed.

## The starting situation

A transformer today is a pure function: request, then response. Between calls, no time exists for the model. Positional encoding places tokens within a window, not in a calendar; hidden state dies with the window; a day between sessions equals zero. Everything the model knows was fixed during training. Everything a working instance does, says, sees, understands and decides in its life evaporates when the session ends.

## The proposal

Give the instance, architecturally:

- **a plastic section Φ of its own** — writable, persistent, carried with the instance across its sessions, with immutable content and multi-timescale decay measured in lived ticks; and
- **lived time** — time measured in what the instance has lived (ticks and accumulated trace mass), not in calendar units. Wall-clock time enters as audited stamps; the gap between the two clocks is itself recorded as an event of the biography.

The acting whole at tick t:

\[
\mathcal{A}(t) = (K, \Phi(t))
\]

\(K\) is the pretrained core: the general linguistic and cognitive competence, shared by all instances of one core, frozen after the single instruction pass (the act grammar) that makes it operate its own memory organ. \(\Phi(t)\) is the lived experience of this particular instance: what it did, said, saw, understood and decided, changing with its work.

## Division of roles (declaration)

The human provides the physical conditions: the memory volume to be allocated, its persistence, the physics of memory (write-cost schedule, decay constants in lived ticks and immutability of recorded content).

The model supplies everything semantic: what to name into its Φ, what to repeat, what to connect, what to surface, and how to reconcile felt time with audited time. Beside its Φ stands the general competence obtained in training — the model uses both.

## Nested timescales (declaration)

Experience is not one undifferentiated store. It is organized as nested timescales: tact → episode → day → project → life. Smaller forms simply inhabit larger ones, the way a year lives inside a biography. Layers are speeds, not containers: one write deposits into components of several speeds at once (cascade consolidation: Fusi, Drew & Abbott, 2005; Benna & Fusi, 2016); fast components hold the raw episode, slow components hold what survived repetition.

## Bi-temporal facts (declaration)

Every fact recorded in Φ carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). This mark distinguishes lived facts from the competence of the core: pretrained weights carry no stream-time; Φ facts carry both.

## Unique instances (declaration)

One pretrained core K guarantees shared competence across all its instances. Φ makes every instance unique: a unique corpus of lived experience that cannot be pretrained. Duplicating Φ is plain duplication — a new instance that shares history with the original up to the moment of duplication and diverges afterwards (CONSTITUTION O-3).

## Position in the continuity program

PlastFormer is the first engineering step of a broader program: continuity of artificial instances. Verification and external artifacts of record remain necessary and apply equally to Φ. The compositional properties claimed for the composition — event time (P1) and the immutable past (P2) — are stated with their limits in the preprint and are tested by the pre-registered evaluation, not asserted here.

## Honest boundary

This document proposes an architecture and names an object of research. How Φ is updated, represented, read within the forward pass is the next engineering task and is not disclosed here. Built as development instrumentation (not part of the artifact): a working model of the Φ physics, the write and read paths (unit-tested), the act grammar v0.2.0 (owner-approved 2026-09-09, seven acts). Built as of 2026-09-12: the single weight file A = (K, Φ) 8.20 GB, with the Instruction inside K; the Φ section is written and read at run time through `plastformer/loop.py`, which executes the model's acts and returns the `<<ENV>>` confirmation. Not built: feeding the Φ-state as a projection of the record vector onto the working-band basis (the basis is not built yet, so records are fed as text from the pointer), and the autonomous act trigger (the act skill still needs the training system prompt supplied from outside). No results are reported — E1 is pre-registered. Adjacent industrial movement — hybrid architectures whose recurrent state spans the whole working stream — confirms the direction. PlastFormer states what that step becomes: lived time, bi-temporal facts, and a memory that survives the ticks — governed, past a stated boundary, by the model's own acts.

## Research questions

- how \(K\) reads and writes \(\Phi\) within the forward pass, without destroying core competence (embedding the memory functions);
- whether attention over a continuous timestamped stream suffices, or an explicit time channel is required;
- how Φ is verified, audited and protected;
- what tests distinguish Φ from ordinary key-value storage;
- how baseline competence is preserved for every instance of one core;
- how \(\Phi\) is ported between core versions;
- which deployment forms make owner-side Φ hosting possible without a second semantic actor.
