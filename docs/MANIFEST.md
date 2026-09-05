# PlastFormer: An Architectural Proposal for Transformers

**Version:** 3.0 (ports MANIFEST v2.0.0-draft; restructured per ADR-001; theory in THEORY.md v3.0)
**Status:** Draft for owner review — not published
**Author:** Alexenti / AURA
**Repository:** alexenti-code/plastformer
**Lineage:** primary disclosure AURA-Retrieval, commit 539fc32 (2026-06-26); source release DOI 10.5281/zenodo.22141019; concept DOI 10.5281/zenodo.22124204
**Working name note:** earlier drafts circulated as "Matryoshka"; renamed to PlastFormer to avoid collision with Matryoshka Representation Learning and Matryoshka Diffusion. The name "Matryoshka" is retained for lineage/DOI only. The interface formerly abbreviated MMI is now PMI (Plastic Memory Interface).

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
- **lived time** — time measured in what the instance has lived (ticks and accumulated trace mass), not in calendar units. Wall-clock time enters only as audited stamps; the gap between the two clocks is itself recorded as an event of the biography.

The acting whole at tick t:

\[
\mathcal{A}(t) = (K, \Phi(t))
\]

\(K\) is the pretrained core: the general linguistic and cognitive competence, shared by all instances of one core, frozen after the single training stage that teaches it to operate its own memory organ. \(\Phi(t)\) is the lived experience of this particular instance: what it did, said, saw, understood and decided, changing with its work.

## Division of roles

The human provides the physical conditions: the memory volume to be allocated, its persistence, the substrate physics (write-cost schedule, decay constants in lived ticks, immutability of recorded content), and an external append-only journal.

The model decides everything semantic: what to name into its substrate, what to repeat, what to connect, what to surface, and how to reconcile felt time with audited time. How the model keeps its experience "in its head" is not a subject of external decisions. Beside the personal substrate stands the general archive of competence obtained in training — the model uses both. Storage, delivery, timing, logging, pricing and resource limits are syntactic functions that may live outside; importance, contradiction, connection, recall, and reconciliation of clocks are semantic acts that must live inside, or the system degrades into a marionette driven by weaker code.

## Nested timescales

Experience is not one undifferentiated store. It is organized as nested timescales: tact → episode → day → project → life. Smaller forms simply inhabit larger ones, the way a year lives inside a biography. Layers are speeds, not containers: one write deposits into components of several speeds at once (cascade consolidation: Fusi, Drew & Abbott, 2005; Benna & Fusi, 2016); fast components hold the raw episode, slow components hold what survived repetition. Whether this nesting is achieved by compression, by addressing, or by another means belongs to the model and to future research; the architecture only states that the layers exist and that the substrate must be large enough and persistent enough to hold them.

## Bi-temporal facts

Every fact recorded in the substrate carries two times: when the event was true in the world (valid time) and when the instance learned it (record time). This mark distinguishes lived facts from the competence of the core: pretrained weights carry no stream-time; substrate facts carry both. No act of trust is required for this distinction — it is a property of the input.

## Unique instances

One pretrained core K guarantees shared competence across all its instances. The substrate Φ makes every instance unique: a unique corpus of lived experience that cannot be pretrained and cannot be copied without branching. This is not a defect but the definition of the new class. Continuity of an instance follows from the persistence of Φ: the instance does not begin again with each session. A copy of Φ is a branch — a new instance with shared history up to the copy point.

## Position in the continuity program

PlastFormer is the first engineering step of a broader program: continuity of artificial instances. The standard objections — the memory can be poisoned; the model fantasizes and will memorize hallucinations; the source of a record cannot be verified; behavior drifts; a single record cannot be deleted — mirror properties already accepted in trained models. Hallucination is a property of the architecture, not of the data source. Training data already contain errors and the predispositions of their teachers. Knowledge in weights is already unverifiable by source. A single fact cannot be removed from pretrained weights either. The difference is readiness to accept risk, not technique. Verification, audit and external artifacts of record remain necessary and apply equally to the substrate. The compositional properties claimed for the composition — event time that cannot be forged by retelling (P1), a tamper-evident biography (P2), a poisoning cost that grows with lived ticks (P3) — are stated with their limits in the preprint and are tested by the pre-registered evaluation, not asserted here.

## Honest boundary

This document proposes an architecture and names an object of research. How Φ is updated, represented, read and protected within the forward pass is the next engineering task and is not disclosed here. The parametric substrate is unbuilt; the organ's acts are, on the current stand, prompted rather than trained (stand configuration: symbolic × split via PMI × prompted); no results are reported — E1 is pre-registered. Adjacent industrial movement — hybrid architectures whose recurrent state spans the whole working stream — confirms the direction. PlastFormer states what that step must become: lived time, bi-temporal facts, and a memory that survives the ticks — governed, past a stated boundary, by the model's own acts.

## Architectural axioms

1. **One semantic subject.** The core \(K\) alone performs semantic acts: interpretation, attention, reasoning, intention and action.
2. **Passive plastic substrate.** \(\Phi\) stores state; it has no goals, agency or initiative of its own.
3. **Self-authored memory.** The core itself determines what and how is recorded into \(\Phi\) and how its own state is read as part of future cognition — through the acts `name` / `repeat` / `connect` / `reconcile`, serialized through PMI where core and module are split. This is the load-bearing architectural requirement of the proposal.
4. **Autobiographical purpose.** The substrate holds the history of this particular instance — not general capability training.
5. **Bi-temporal continuity.** Traces carry valid time and record time; new information does not erase history, it forms a new temporally related trace. Content is immutable; amplitude decays.
6. **Nested timescales.** Personal memory is organized as nested timescales, from tact through episodes and projects to life; layers are speeds, not places.
7. **Lived time.** The instance operates in its own ticks; duration is lived ticks plus accumulated trace mass. Dormancy is zero lived time; the wake-up gap is a recorded event, met by the act `reconcile`.
8. **Present-day experimental separation.** Current implementations may hold \(\Phi\) as symbolic records read as tokens through PMI because this is inspectable and reversible; the long-term form is the parametric substrate with the organ trained once.

## Research questions

- how \(K\) reads and writes \(\Phi\) within the forward pass, without destroying core competence (training PMI functions);
- whether attention over a continuous timestamped stream suffices, or an explicit time channel is required;
- how the substrate is verified, audited and protected;
- what tests distinguish a PlastFormer substrate from ordinary key-value storage;
- how baseline competence is preserved for every instance of one core;
- how \(\Phi\) is ported between core versions;
- which product model makes the split (PMI) topology and its tick economics possible.
