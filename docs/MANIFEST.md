# PlastFormer: An Architectural Proposal for Transformers

**Version:** 4.0 (restructured per ADR-002; norms moved to CONSTITUTION.md v3.0)
**Status:** Draft for owner review — not published
**Author:** Alexenti / AURA
**Repository:** alexenti-code/plastformer
**Lineage:** primary disclosure AURA-Retrieval, commit 539fc32 (2026-06-26); source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204
**Working name note:** earlier drafts circulated as "Matryoshka"; renamed to PlastFormer to avoid collision with Matryoshka Representation Learning and Matryoshka Diffusion. The name "Matryoshka" is retained for lineage/DOI only. The interface formerly abbreviated MMI is now PMI (Plastic Memory Interface).
**Normative anchor:** this file declares a position and states no enforceable rules. Enforceable statements and tests live in [CONSTITUTION.md](CONSTITUTION.md); the migration table is in [ADR-002](ADR-002-docs-architecture.md).

## Declaration

PlastFormer is an architectural proposal for transformer-based language models.

It proposes that a working language-model instance be given, as a matter of architecture, **one thing**:

1. its own plastic module Φ governed by its own trained acts — `name` / `repeat` / `connect` / `reconcile` — acquired in a single training stage, after which the core is frozen.

This is a proposal of one architecture for all transformers: a frozen core plus a plastic per-instance substrate plus the model's own acts, trained once. It is not a memory file format, not an algorithm, not a retrieval wrapper, not a second reasoning agent, not a prompt assembly system, not an orchestration layer, and not a mechanism for altering the pretrained core. Substrate form (parametric ↔ symbolic), topology (co-located ↔ split via PMI), and act state (trained ↔ prompted) are configuration axes, not different systems.

## The starting situation

A transformer today is a pure function: request, then response. Between calls, no time exists for the model. Positional encoding places tokens within a window, not in a calendar; hidden state dies with the window; a day between sessions equals zero. Everything the model knows was fixed during training. Everything a working instance does, says, sees, understands and decides in its life evaporates when the session ends.

## The proposal

Give the instance, architecturally:

- **a plastic module Φ of its own** — writable, persistent, carried with the instance across its sessions, with immutable content and multi-timescale decay measured in lived ticks; and
- **lived time** — time measured in what the instance has lived (ticks and accumulated trace mass), not in calendar units. Wall-clock time enters as audited stamps; the gap between the two clocks is itself recorded as an event of the biography.

The acting whole at tick t:

\[
\mathcal{A}(t) = (K, \Phi(t))
\]

\(K\) is the pretrained core: the general linguistic and cognitive competence, shared by all instances of one core, frozen after the single training stage that teaches it to operate its own memory organ. \(\Phi(t)\) is the lived experience of this particular instance: what it did, said, saw, understood and decided, changing with its work.

## Division of roles (declaration)

The human provides the physical conditions: the memory volume to be allocated, its persistence, the substrate physics (write-cost schedule, decay constants in lived ticks and immutability of recorded content).

The model supplies everything semantic: what to name into its substrate, what to repeat, what to connect, what to surface, and how to reconcile felt time with audited time. Beside the personal substrate stands the general archive of competence obtained in training — the model uses both.

## Nested timescales (declaration)

Experience is not one undifferentiated store. It is organized as nested timescales: tact → episode → day → project → life. Smaller forms simply inhabit larger ones, the way a year lives inside a biography. Layers are speeds, not containers: one write deposits into components of several speeds at once (cascade consolidation: Fusi, Drew & Abbott, 2005; Benna & Fusi, 2016); fast components hold the raw episode, slow components hold what survived repetition.

## Bi-temporal facts (declaration)

Every fact recorded in the substrate carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). This mark distinguishes lived facts from the competence of the core: pretrained weights carry no stream-time; substrate facts carry both.

## Unique instances (declaration)

One pretrained core K guarantees shared competence across all its instances. The substrate Φ makes every instance unique: a unique corpus of lived experience that cannot be pretrained. Duplicating Φ is plain duplication — a new instance that shares history with the original up to the moment of duplication and diverges afterwards (CONSTITUTION O-3).

## Position in the continuity program

PlastFormer is the first engineering step of a broader program: continuity of artificial instances. Verification and external artifacts of record remain necessary and apply equally to the substrate. The compositional properties claimed for the composition — event time (P1) and the immutable past (P2) — are stated with their limits in the preprint and are tested by the pre-registered evaluation, not asserted here.

## Honest boundary

This document proposes an architecture and names an object of research. How Φ is updated, represented, read within the forward pass is the next engineering task and is not disclosed here. The parametric substrate is unbuilt; the organ's acts are, on the current stand, prompted rather than trained (stand configuration: symbolic × split via PMI × prompted); no results are reported — E1 is pre-registered. Adjacent industrial movement — hybrid architectures whose recurrent state spans the whole working stream — confirms the direction. PlastFormer states what that step becomes: lived time, bi-temporal facts, and a memory that survives the ticks — governed, past a stated boundary, by the model's own acts.

## Superseded lineage notes (not norms)

The following sentences appeared as norms in MANIFEST v2.0–v3.0 and are **SUPERSEDED** — retained here as lineage only. The binding wording is in CONSTITUTION:

- SUPERSEDED (→ CONSTITUTION O-4): "continuous existence in time" / "continuous calendar existence" as a requirement. Binding position: continuity is a property of the Φ line in lived ticks; dormancy is zero lived time.
- SUPERSEDED (→ CONSTITUTION O-4): "the human/owner provides physical time" / "physical time is given, measured by a clock from the moment of launch". Binding position: the stand counts storing acts; the model owns working ticks; wall-clock stamps never enter amplitude.
- SUPERSEDED (→ CONSTITUTION O-10): "the architecture only states that the layers exist" read as containers/places. Binding position: layers are speeds (τ constants), never containers or permission zones.
- SUPERSEDED (→ CONSTITUTION O-3): "a unique corpus … that cannot be copied". Binding position: duplicating Φ is plain duplication — a new instance that shares history with the original up to the moment of duplication and diverges afterwards.
- SUPERSEDED (→ CONSTITUTION C6): "No act of trust is required for this distinction — it is a property of the input." Binding position: source-class handling is capped physics asserted by the model; class policy is a deployment choice and an attack surface.
- SUPERSEDED (→ CONSTITUTION O-1–O-11 and C1–C8): the "Architectural axioms" §1–8 of MANIFEST v3.0 in full. Binding position: CONSTITUTION v3.0 — Foundations O-1–O-11 and compliance tests C1–C8.

## Research questions

- how \(K\) reads and writes \(\Phi\) within the forward pass, without destroying core competence (training PMI functions);
- whether attention over a continuous timestamped stream suffices, or an explicit time channel is required;
- how the substrate is verified, audited and protected;
- what tests distinguish a PlastFormer substrate from ordinary key-value storage;
- how baseline competence is preserved for every instance of one core;
- how \(\Phi\) is ported between core versions;
- which product model makes the split (PMI) topology and its tick economics possible.
