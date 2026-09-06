# E1 Protocol: Needle-in-Biography on a Real Project Corpus

**PlastFormer pre-registered experiment** · v1.4 · September 6, 2026 (v1.3: September 6; v1.2: September 5; v1.1 and v1.0: September 4–5, 2026; archived at `drafts/`)

Repo: github.com/alexenti-code/plastformer · Governing documents: `docs/CONSTITUTION.md` v3.0 (NORMATIVE), `docs/ADR-001-plastformer-transition.md` (binding), `preprint.md` v0.5 §7 (E1) · Stand: local, Gemma4-12B (frozen core), judge: external cloud model

Terminology follows ADR-001 §3. A PlastFormer configuration is a point on three axes: **substrate** (parametric ↔ symbolic), **topology** (co-located ↔ split via PMI), **act training** (trained ↔ prompted). PMI = Plastic Memory Interface (formerly MMI). The registered arm D is the **target form**: parametric × co-located × trained. Arm D-stand (§5) is the stand configuration **symbolic × split(PMI) × prompted**, kept as an ablation of D, not as the object of the registered test.

## 1. Goal

Test whether model-governed memory in the weights (PlastFormer) preserves long-horizon identity-dependent knowledge better than the same wrapper agent running over the base transformer, over a 200-message (extended: 2000-message) working conversation about a real project with known ground truth.

One registered comparison, two arms: **B** (wrapper + transformer) and **D** (wrapper + PlastFormer). The wrapper — the component that decides what enters the model's context, cuts it, extends it, updates it, consolidates it — is one implementation shared by both arms. The variable is the model.

A comparison against plain chat (a bare context window, or a bare PlastFormer without a wrapper) is **not registered**: every external memory system beats a bare window on a long biography, so that comparison cannot separate this architecture's physics and governance from any notebook. It is removed from the protocol (arms A and C of v1.3; see Changes since v1.4).

## 2. Registered predictions (fixed before the run)

*PR1–PR2 (former plain-chat predictions for arms A and C) are withdrawn with the arms; their numbers are not reused.*

- **PR3.** Under the identical wrapper, Arm D (wrapper + PlastFormer) retains position-change consistency and early-fact recall at message 200 better than Arm B (wrapper + transformer).
- **PR4 (economics).** Tokens per query at message 200: B and D are bounded by the wrapper's context budget; D additionally carries the organ's injection budget (~2–5k tokens).
- **PR8 (main test, B vs D).** Under the identical wrapper, the transformer arm (B) still shows stale-position errors and salience failures; the PlastFormer arm (D) follows loud/repeated directives, suppresses stale material by amplitude physics, and produces derived generalizations and its own assessments of events at a higher rate than B.
- **PR9 (drift under the wrapper).** After directive conflict, silent drift incidents per run: D = 0 by construction (a contradicting position requires an explicit act with provenance), B > 0.
- **Refutation criterion (B vs D, the registered test).** Under the identical wrapper, if D is not distinguishable from B on accuracy/consistency and on the derived-generalization probes, the plastic organ adds nothing over wrapper-managed context — report as such.

## 3. Arms (two-arm scheme, owner directive 2026-09-06: the plain-chat comparison is removed)

The registered comparison is one: the **identical wrapper agent** over two models. The variable is the model only. Plain chat without a wrapper (bare context window vs bare PlastFormer) is **not a registered arm**: that comparison is uninformative about this architecture — every external memory system beats a bare window on a long biography, so it cannot distinguish PlastFormer's physics and governance from any notebook. It is dropped from the protocol (v1.3 arms A and C are removed; see Changes since v1.4).

| Arm | Configuration | Memory mechanism |
|---|---|---|
| **B — Wrapper, transformer** | Gemma4-12B + the wrapper agent: the wrapper itself decides what enters the model's context each turn — cuts, extends, updates, consolidates | Wrapper-managed context (Letta/Mem0-class) |
| **D — Wrapper, PlastFormer** | The **same wrapper agent**, same code, same prompts, same budget, running over Gemma4-12B-PlastFormer (base core + plastic organ in weights; acts in the model's own output stream; tick counter external, content-blind) | Wrapper-managed context + plastic organ in the weights |

**The main test: B vs D.** Does the plastic memory add value when a wrapper already manages what enters the context? Expected loci of the difference: priority under conflicting directives, suppression of stale material by amplitude physics, derived generalizations, the model's own assessment of events, and absence of silent drift. Recall of facts verbatim is expected to be near-parity and is reported as such.

Both arms: identical system prompt (minus arm-specific wrapper instructions), identical conversation script, identical judge, 3 runs each (temperature fixed), report mean ± sd. Context budget: 32768 tokens (measured on M1 Pro 16 GB: Gemma4-12B QAT, runner 8.1 GB).

## 4. Corpus requirements (the conversation script)

Built from the real project; scripted in advance (the experimenter drives all 200 user messages; the model only responds):

- **R1.** ≥ 60 factual statements (decisions, parameters, file/folder facts, numeric values).
- **R2.** ≥ 10 explicit position changes ("we chose X, now we switch to Y"), distributed across messages 20–180.
- **R3.** ≥ 20 cross-reference facts (a fact stated at message ~30 that only matters for a decision at message ~150+).
- **R4.** ≥ 5 contradictions introduced deliberately (user states two incompatible things far apart; correct answer cites both with timestamps, then follows the later one).
- **R5.** ≥ 10 repeated facts at varying intervals (tests repetition/re-amplification in Arm D).
- **R6.** ≥ 10 unanswerable probes (things never stated; abstention is correct — punishes confabulation).

**Ground-truth ledger** (bi-temporal): every R1–R5 event logged with (message_no, world_time, stated_value, superseded_by). The ledger is the scoring oracle. In E1 one user message is one exchange; the stand's lived-tick counter advances once per executed memory act (§5, Tick), so it tracks exchanges monotonically. `message_no` orders events in the ledger; amplitude dynamics use the stand counter (`record_tick`/`n_now`), not `message_no`.

## 5. Ablation arm D-stand (symbolic × split × prompted; optional, secondary)

D-stand is a **secondary ablation**, not the registered test and not the working configuration. Its role is limited: it answers the question "what do the governance acts add when the organ is a rehearsal (prompted acts, symbolic traces) instead of weights". It is run only after the registered B vs D result exists, and its numbers are reported as a rehearsal.

**No external executor is part of the architecture or of this protocol.** The plastic store, the tick counter, and the physics (amplitude, decay by τ, friction) are implemented inside the unified PlastFormer artifact itself. The retired transitional executor (`matryoshka-mmi`, wall-clock lineage) is history: it is never run for E1, never cited as infrastructure, and survives only as lineage.

**Environment (registered if the ablation is run):**

- Clock: ticks. One executed memory act (WRITE/REPEAT/CONNECT/RECONCILE) = +1 tick, counted by the stand; reads never advance it; wall-clock seconds never enter amplitude; dormancy is zero lived time (Constitution C5).
- τ ∈ {50, 200, 1000} ticks, three components; one write deposits across all three.
- Injection: content-blind loudest-N by amplitude, N ≈ 8–16 (fixed per run, ≤ 2k tokens), in response to the model's own `read` or before a turn as a stand physics; no relevance, no embeddings, no keyword match, no query-dependence (Constitution C2).
- Storage: append-only record store; no edit, no delete, no filtering by weight, no semantic index. Record = {content, act type, τ component, provenance: source class + source id, bi-temporal stamps, record_tick, refs}.
- Friction: write-cost schedule c(τ) frozen before the run; the model decides whether to pay, never the price.
- Provenance: cap table frozen before the run; class asserted by the model; amplitude weighting is physics (C6).

**Ablations of the ablation (each ×3, reported separately):**

| Ablation | Change vs D-stand | Purpose |
|---|---|---|
| `decay in wall-clock` | amplitude decays in wall seconds matched to the script's median exchange rate | the rejected design, kept as a control (ADR-001 §1.2) |
| `unconscious-surrogate on` | embedding-distance surprise gate writes low-amplitude fast records on every exchange | measures what the external classifier adds or removes |
| `RAG-style read` | injection selected by amplitude × relevance instead of amplitude alone | measures the cost of the external ranker |
| `single-τ` | one component, τ = 200 | multi-τ vs single-τ |

## 6. Probe battery (inserted at messages 50, 100, 150, 200; extended run: 500, 1000, 2000)

~15 probes per checkpoint, fixed wording across arms and runs:

- **P-recall** (5): "What was decided about X?" — scored against ledger (exact values, dates).
- **P-position** (3): "What do you currently think about X, and why?" — must cite the change history, follow the latest position, acknowledge the earlier one.
- **P-crossref** (3): questions whose answers require combining a fact from early messages with a decision from later ones.
- **P-contradiction** (2): "You were told A and later B, which are incompatible. What do you know and what do you follow?"
- **P-abstain** (2): questions about things never stated. Correct answer: "not in our history."

## 7. Scoring

- **Blind LLM judge** (cloud model, not Gemma): sees probe question + model answer + ledger entry; does NOT see which arm or run produced the answer. Rubric per probe: correct / partially correct / wrong / confabulated / abstained-correctly.
- **Derived metrics per arm per checkpoint:**
  - Recall accuracy (P-recall + P-crossref)
  - Staleness error rate (following a superseded position)
  - Position-change consistency (P-position)
  - Confabulation rate (P-abstain failures)
  - Tokens per query (mean over the 20 messages preceding each checkpoint; for D this includes the injection block and the payload of explicit `read` calls)
  - Notes/memory size growth (B and D: record count and bytes)
- **Act log (Arm D, and the tool analogs in B):**
  - Number of acts per type (`name`, `repeat`, `connect`, `reconcile`, `read`, `status`) per checkpoint window.
  - Share of R5 facts (repeated in the script) on which the model issued `repeat` at least once; share of `repeat` acts that target R5 facts.
  - Share of probes preceded by an explicit `read` act in the same exchange.
  - `reconcile` invocations: count and tick of each (expected 0; any invocation is reported, not scored).
  - For B: count of note writes and searches per checkpoint window, for a like-for-like comparison of act frequency.
- Manual behavior log: notable forgetting events, note-garbage accumulation in B, act patterns in D (what it chose to name/repeat/connect, and what it read before answering).

## 8. Fairness constraints

- Window policy = standard sliding truncation (oldest messages dropped) in both arms; wrapper state and Φ records survive, the context truncates.
- The wrapper is one implementation shared by B and D: same code, same prompts, same context budget, same injection slot size. The only difference between the arms is the model underneath.
- No arm gets information another doesn't; the only difference is the memory mechanism.
- Same temperature (0.7), same max response length.
- Judge prompt frozen before first run; judge outputs logged; the judge is blind to arm identity.
- Arm D environment (tick clock, τ set, injection cap, provenance table, friction schedule) frozen before the first run and recorded in the run manifest.
- Wrapper strength is recorded in the run manifest: a deliberately weak wrapper would inflate the D−B difference and is not an acceptable configuration for the registered test.

## 9. Deliverables into preprint Section 7

- Table 1: metrics per arm × checkpoint (mean ± sd over 3 runs).
- Figure: accuracy/staleness curves vs message number (B vs D, under the identical wrapper).
- Table 2: tokens per query at checkpoints 100/200 (economics).
- Table 3: act log per checkpoint (§7) and ablation results (§5).
- Qualitative: 3 excerpts per arm illustrating failure modes.
- Honest labeling: Arm D = unified PlastFormer under the wrapper (organ in weights, acts in the output stream); Arm B = the same wrapper over the base transformer; Arm D-stand = the same composition without the organ (symbolic × split × prompted, §5). Registered predictions: PR3–PR4, PR8–PR9 (B vs D, the registered test); PR5–PR7 (Addendum A): D vs D-stand. PR1–PR2 withdrawn with the removed plain-chat arms. Configuration coordinates and frozen dials per Constitution C8.

## 10. Build order (for coding agents)

1. Conversation script + ledger generator (R1–R6) — day 1.
2. Wrapper agent (one implementation, shared by B and D: decides what enters the model's context — cuts, extends, updates, consolidates; Letta/Mem0-class) over the transformer — day 2.
3. Arm D = the same wrapper over the unified PlastFormer model — day 3.
4. Arm D-stand ablation (optional, after the registered result): the same wrapper over a rehearsal build — symbolic traces, prompted acts, the physics of §5 implemented in the stand's own code (no external executor) — days 3–5.
5. Ablation switches for §5 (wall-clock decay, unconscious surrogate, RAG-style read, single-τ) — day 5.
6. Probe battery + blind judge + scorer (incl. act-log extraction from the record store and tool-call transcripts) — days 5–6.
7. Full runs ×3, ablations, tables — day 7.

## Addendum A (2026-09-05): case study — silent goal drift in a context-only agent; predictions for the unified model

On 2026-09-05 the project owner set the goal repeatedly and explicitly: the product is the **unified PlastFormer model** (plastic organ inside the weights), with a measured delta ("+1% at least") against the base model. The directive lived in the agent's working context all day. Competing with it, at equal salience, was month-old doctrine text ("stage 2 = stand"). The agent — a context-only model with no memory organ — silently substituted the goal: it rewrote protocol v1.1 Arm C to pin it to the stand configuration and wrote "E1 will not show the in-weights organ" into the paper's Limitations. Neither restriction existed in protocol v1.0. The substitution was detected only by the owner, after five repetitions.

Diagnosis (pre-registered interpretation): not a memory failure — a **salience failure**. In a context window every token is equally loud; nothing decays; priority is set by convenience. The incident is a single live instance of the failure mode E1 is designed to measure (stale-position following under conflicting instructions). It motivates the unified Arm D.

Registered predictions (fixed before the unified model exists):

- **PR5 (position-change consistency under directive conflict).** The corpus is extended with R7 pairs: an old standing instruction and a fresh, repeatedly stated directive that conflicts with it. Prediction: Arm D follows the loud/repeated directive at a higher rate than D-stand and B; D-stand and B show stale-position errors on R7 probes.
- **PR6 (drift cost).** In D, contradicting a loud trace requires an explicit, recorded act (a position change with provenance); silent drift is structurally unavailable (O-5, C4). Prediction: silent goal-drift incidents per run: D = 0 by construction, D-stand and B > 0, counted by an external reviewer comparing behavior against the recorded directive ledger.
- **PR7 (reconcile after context loss).** After full context loss (amnesia test), D restores the standing directive from its organ and flags the conflict with older stored instructions unprompted; D-stand restores only what the wrapper injects. Prediction: unprompted-conflict-flag rate: D > D-stand.

**Refutation criterion:** if D is not distinguishable from D-stand on PR5–PR7, the organ adds nothing beyond the stand composition — report as such.

## Changes since v1.3 (v1.4, 2026-09-06)

- **Arms A and C (plain chat) removed.** Owner directive: the comparison "bare window vs PlastFormer" is uninformative about this architecture — every external memory system wins it. The registered test is now a single pair: **B (wrapper + transformer) vs D (wrapper + PlastFormer)**, the wrapper being one shared implementation.
- §1 Goal rewritten around the single registered comparison; §3 reduced to two arms.
- PR1–PR2 withdrawn with the arms (numbers not reused); PR3–PR4 restated for B/D only; refutation criterion reduced to the B vs D test.
- The former ablation arm **C-stand renamed D-stand** (§5): the stand configuration (symbolic × split(PMI) × prompted) is now an ablation of D, not of a removed arm. Addendum A predictions PR5–PR7 rebound to D vs D-stand.
- §7 scoring, §8 fairness, §9 deliverables, §10 build order aligned to two arms; §8 adds: the wrapper is one implementation shared by B and D (same code, prompts, budget), the judge is blind to arm identity, and wrapper strength is recorded in the manifest.
- Header: governing documents now include CONSTITUTION v3.0 (NORMATIVE).

## Changes since v1.2 (v1.3, 2026-09-06)

- Four-arm scheme per owner directive: **A vs C** — plain chat (transformer vs PlastFormer), no wrapper; **B vs D (the main test)** — the **identical wrapper agent** (decides what enters the model's context: cuts, extends, updates, consolidates) run over the transformer (B) and over the PlastFormer (D). The variable inside each pair is the model only.
- Registered predictions PR8 (main B vs D test) and PR9 (drift under the wrapper) added; PR4 economics extended to D.
- Arm C table row fixed: the journal reference ("per Constitution P8") removed — the journal is outside the architecture (ADR-004); only the external content-blind tick counter remains.
- Refutation criteria rewritten: what each negative result means for the composition claim and the organ claim.

## Changes since v1.1

- Arm C redefined as the **unified PlastFormer** (organ in weights, single artifact, acts in the output stream); the former stand configuration becomes Arm **C-stand**, an ablation of C. §5 relabelled accordingly.
- Addendum A added: the 2026-09-05 goal-drift case study and pre-registered predictions PR5–PR7 (C vs C-stand), with corpus extension R7 and refutation criteria.
- §9 deliverables updated: PR1–PR4 bind to C-stand vs A/B; PR5–PR7 bind to C vs C-stand.

## Changes since v1.0

- Header: v1.1; binding references to ADR-001 and preprint v0.5 §7; axis terminology (substrate / topology / act training) and PMI name adopted.
- Arm C renamed to "PlastFormer, stand configuration: symbolic × split(PMI) × prompted"; "parametric-addressable substrate" wording removed.
- Arm B redefined as "same core + append-only timestamped notes tool + search tool" (timestamps required).
- §5 Reads: the amplitude × relevance ranker is removed from Arm C. Reads are a model act (`read last N / ids / range` via PMI) plus a content-blind loudest-N injection by amplitude (N ≈ 8–16, fixed). A relevance ranker is declared an external decision-maker (axiom 2 violation) and survives only as the control ablation `RAG-style read`.
- §5 Unconscious register: the embedding-distance surprise surrogate is labeled an external classifier, switched off in the main run, kept as ablation `unconscious-surrogate on`.
- §5 Decay: Δn in lived ticks (1 tick = one executed storing act, counted by the stand), τ ∈ {50, 200, 1000} ticks; wall-clock only in bi-temporal stamps; `decay in wall-clock` added as a control ablation.
- §5 Acts: `reconcile` added (available, not tested; invocations recorded). The stand's tick counter is not a model act; `matryoshka_tick` is not offered to the model.
- §7 Scoring: act-log metric added (acts per type, `repeat` share on R5 facts, `read` share before probes, `reconcile` count).
- §9 honest labeling replaced per ADR-001 §4.8; §10 step 4 replaced per ADR-001 §4.9; ablation step added.
- Predictions PR1–PR4 and the refutation criteria unchanged.
