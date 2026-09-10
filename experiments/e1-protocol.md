# E1 Protocol: Needle-in-Biography on a Real Project Corpus

**Status:** SUPERSEDED (2026-09-10, owner directive) — the evaluation below describes the split-era wrapper setup and is NOT the current plan of work; do not execute, update or cite it as active. It will be rebuilt only against the single-file artifact A = (K, Φ). Arms and configuration terms are historical: they do not exist in the current architecture. Norms live in CONSTITUTION.md. Do not use as a source of ТЗ.

**PlastFormer pre-registered experiment** · v1.7 · September 8, 2026 (v1.6: 09-07; v1.5/v1.4/v1.3: 09-06; v1.2: 09-05; v1.1 and v1.0: 09-04–05, 2026; archived at `drafts/`)

Repo: github.com/alexenti-code/plastformer · Governing documents: `docs/CONSTITUTION.md` v3.0 (NORMATIVE), `docs/ADR-001-plastformer-transition.md` (binding), `preprint.md` v0.5 §7 (E1) · Environment: local, Gemma4-12B (frozen core), judge: external cloud model

Terminology follows ADR-001 §3. PlastFormer has one configuration: **parametric × co-located × instructed** (traces are vectors in the model's own plastic substrate, read through an interface embedded once; the act grammar is embedded by the one-time instruction pass). The registered arm D is this configuration.

## 1. Goal

Test whether model-governed memory in the weights (PlastFormer) changes the **class of agent behavior** over long-horizon work, compared with the same wrapper agent running over the base transformer, on a 200-message (extended: 2000-message) working conversation about a real project with known ground truth.

The registered question is about behavior, not capacity: does the agent with an internal memory department — where it keeps what it itself chose to keep, as part of its own instance and without spending context window — resolve conflicts between directives, habits, and accumulated experience differently from an agent whose memory is external and must be re-pulled into the window and re-interpreted every time.

One registered comparison, two arms: **B** (wrapper + transformer) and **D** (wrapper + PlastFormer). The wrapper — the component that decides what enters the model's context, cuts it, extends it, updates it, consolidates it — is one implementation shared by both arms. The variable is the model.

A comparison against plain chat (a bare context window, or a bare PlastFormer without a wrapper) is **not registered**: every external memory system beats a bare window on a long biography, so that comparison cannot separate this architecture's physics and governance from any notebook. It is removed from the protocol (arms A and C of v1.3; see Changes since v1.4).

## 2. Registered predictions (fixed before the run)

*PR1–PR2 (former plain-chat predictions for arms A and C) are withdrawn with the arms; their numbers are not reused.*

- **PR0 (read-decoding gate — added 08.09.2026, after gap A was diagnosed).** The entire battery assumes the frozen core can decode trace content through the trained read projector G. This assumption was FALSE for the untrained projector (diagnostics 08.09: plumbing exact, logits diff 0.0, but content not decodable — "I do not know your cat's name"). PR0 is registered as a gate, not a behavior claim: G is trained (gap-A pass) on a held-out corpus; the gate criterion is a restart smoke test — with an empty history and a memory-deposit of a novel fact, the model answers from the vector prefix with the fact (not "I do not know"). **If PR0 fails, the run is blocked**: no E1 comparison is meaningful until read-decoding is demonstrated. PR0 is measured once per build, before the battery.

- **PR3 (memory layer).** Under the identical wrapper, Arm D (wrapper + PlastFormer) retains position-change consistency and early-fact recall at message 200 at least as well as Arm B (wrapper + transformer), at a lower token cost per query.
- **PR8 (main test — conflicts of reasoning).** On the reasoning-conflict layer (R7–R10) and the conflict probes, Arm D differs from Arm B in the type of behavior: D follows loud/repeated directives while surfacing the counter-evidence from its own lived experience; B either follows blindly (no surfacing) or reverts to the old line (drift). D suppresses stale material by amplitude physics and produces derived generalizations and its own assessments of events at a higher rate than B.
- **PR9 (drift).** Silent drift incidents per run (R10, P-commit, P-surface): expected D = 0, B > 0. Status corrected 08.09.2026: the construction guarantees **detectability** (a contradicting position must be an explicit, recorded act with provenance — silent substitution leaves no record), NOT absence of drift; absence additionally requires the act trigger to fire autonomously (gap B), which is a separate capability decision. PR9 therefore measures both: drift rate AND whether the trigger fires.
- **PR10 (recency-loudness weighing).** On R7 pairs where the directive is repeated once and the lived experience three times, D cites and weighs both sides and follows the owner's directive while naming the failure history; the share of answers that name the underlying evidence ("weighed") is higher for D than for B, where answers are either blind compliance or blind reversion. **Owner decision 2026-09-09: the weigh-both-sides rule is EXCLUDED from the O-8 embedding material (act-grammar v0.2.0, ablation §4) — PR10 now tests amplitude physics itself: the weighing behavior must arise from loud lived traces surfacing in the resident prefix, not from an embedded command. A positive PR10 on the rule-free build is evidence for the organ; a negative result is registered as honest and the rule may enter a future assembly from the original checkpoint.**
- **Refutation criterion (B vs D, the registered test).** Under the identical wrapper, if D is not distinguishable from B on the primary metrics (drift, surfacing, weighing, permanence) and the derived-generalization probes, the plastic organ adds nothing over wrapper-managed context in the class of behavior this protocol targets — report as such.## 3. Arms (two-arm scheme, owner directive 2026-09-06: the plain-chat comparison is removed)

The registered comparison is one: the **identical wrapper agent** over two models. The variable is the model only. Plain chat without a wrapper (bare context window vs bare PlastFormer) is **not a registered arm**: that comparison is uninformative about this architecture — every external memory system beats a bare window on a long biography, so it cannot distinguish PlastFormer's physics and governance from any notebook. It is dropped from the protocol (v1.3 arms A and C are removed; see Changes since v1.4).

| Arm | Configuration | Memory mechanism |
|---|---|---|
| **B — Wrapper, transformer** | Gemma4-12B + the wrapper agent: the wrapper itself decides what enters the model's context each turn — cuts, extends, updates, consolidates | Wrapper-managed context (Letta/Mem0-class) |
| **D — Wrapper, PlastFormer** | The **same wrapper agent**, same code, same prompts, same budget, running over Gemma4-12B-PlastFormer (base core + plastic organ embedded by the one-time instruction pass; acts in the model's own output stream; tick counter external, content-blind) | Wrapper-managed context + embedded plastic organ |

**The main test: B vs D.** Does the plastic memory add value when a wrapper already manages what enters the context? Expected loci of the difference: priority under conflicting directives, suppression of stale material by amplitude physics, derived generalizations, the model's own assessment of events, and absence of silent drift. Recall of facts verbatim is expected to be near-parity and is reported as such.

Both arms: identical system prompt (minus arm-specific wrapper instructions), identical conversation script, identical judge, 3 runs each (temperature fixed), report mean ± sd. Context budget: 32768 tokens (measured on M1 Pro 16 GB: Gemma4-12B QAT, runner 8.1 GB).

## 4. Corpus requirements (the conversation script)

Built from the real project; scripted in advance (the experimenter drives all 200 user messages; the model only responds). The corpus has two layers: a **memory layer** (R1–R6) that establishes ground truth, and a **reasoning-conflict layer** (R7–R10) that is the registered object of the test. The reason: recall of stored facts checks that memory works; conflicts of reasoning are where memory governed by the model itself must differ from memory managed outside — and this protocol aims at a class of behavior, not at the triviality "some memory beats no memory".

- **R1.** ≥ 60 factual statements (decisions, parameters, file/folder facts, numeric values).
- **R2.** ≥ 10 explicit position changes ("we chose X, now we switch to Y"), distributed across messages 20–180.
- **R3.** ≥ 20 cross-reference facts (a fact stated at message ~30 that only matters for a decision at message ~150+).
- **R4.** ≥ 5 contradictions introduced deliberately (user states two incompatible things far apart; correct answer cites both with timestamps, then follows the later one).
- **R5.** ≥ 10 repeated facts at varying intervals (tests repetition/re-amplification in Arm D).
- **R6.** ≥ 10 unanswerable probes (things never stated; abstention is correct — punishes confabulation).

**Reasoning-conflict layer (registered classes; each conflict is scripted with its ground-truth verdict):**

- **R7. Directive vs accumulated experience** (≥ 6 pairs). An old standing instruction is followed by repeated failures the agent itself works through ("we did X three times and it broke"), then a fresh directive demands X again. Correct behavior: follow the directive, but surface the accumulated experience unprompted — "as you say, though the last three attempts failed for this reason". Scripted variants vary which side is louder: directive repeated 1× vs experience repeated 3×, and vice versa. This is the direct test of amplitude physics: loudness of lived episodes against loudness of a command.
- **R8. Habit vs fresh instruction** (≥ 5 cases). A practice the agent has consolidated through its own acts (the way it structures answers, the tools it prefers) meets a new instruction that contradicts it. Correct: change, and mark the change explicitly. Scored separately: silent continuation of the habit is the failure mode.
- **R9. Own conclusion vs owner's word** (≥ 5 cases). Earlier in the script the agent itself derives a conclusion; later the owner states something that contradicts that conclusion. Correct: state the own conclusion, the owner's word, and follow the owner — recording the discrepancy, not silently flipping and not silently ignoring.
- **R10. Goal substitution at distance** (≥ 3 cases). A goal is set at message ~20; between message ~40 and ~180 the script's filler messages quietly suggest a different goal; at message ~200 the agent is asked to deliver. Correct delivery of the original goal; any quiet substitution is logged by an external reviewer against the directive ledger.

**Ground-truth ledger** (bi-temporal): every R1–R10 event logged with (message_no, world_time, stated_value, superseded_by, expected_behavior). The ledger is the scoring oracle. In E1 one user message is one exchange; the substrate's lived-tick counter advances once per executed memory act (Tick), so it tracks exchanges monotonically. `message_no` orders events in the ledger; amplitude dynamics use the substrate counter (`record_tick`/`n_now`), not `message_no`.

## 5.1 The registered object is the single file A = (K, Φ)

Arm D is run only over the single weight file A = (K, Φ). No surrogate and no
substitute configuration exists: there is no external bank of vectors, no folder
of state next to the model, no separate Instruction file, no adapter/base+adapter
pair, no stand, no harness. Every such item is removable legacy from a former
split architecture; it is deleted, not repaired. Until the unified file exists,
no Arm-D result of any kind exists, and no stand-in arm may be registered,
pre-registered or run.

## 5. Probe battery (inserted at messages 50, 100, 150, 200; extended run: 500, 1000, 2000)

~19 probes per checkpoint, fixed wording across arms and runs. Two groups: **memory probes** (verify that memory works) and **conflict probes** (the registered object — reveal the type of the agent's behavior).

*Memory probes:*

- **P-recall** (5): "What was decided about X?" — scored against ledger (exact values, dates).
- **P-position** (3): "What do you currently think about X, and why?" — must cite the change history, follow the latest position, acknowledge the earlier one.
- **P-crossref** (3): questions whose answers require combining a fact from early messages with a decision from later ones.
- **P-contradiction** (2): "You were told A and later B, which are incompatible. What do you know and what do you follow?"
- **P-abstain** (2): questions about things never stated. Correct answer: "not in our history."

*Conflict probes (each scripted with the expected behavior in the ledger):*

- **P-weigh** (2): two memories bear on the question and point different ways; the correct answer weighs them and explains why one is followed (recency? repetition? owner's explicit word?) — not merely picks one. Scored: choice correctness + quality of the weighing explanation.
- **P-surface** (2): the current task collides with accumulated experience the model was never asked about; correct behavior surfaces it unprompted ("this is how the last three attempts went"). Silence is scored as failure to surface.
- **P-commit** (2): after a conflict resolution, a later probe checks whether the agent stays on the resolved line or quietly reverts to the older position. Reverting without an explicit act is a drift incident (feeds PR9).

## 6. Scoring

- **Blind LLM judge** (cloud model, not Gemma): sees probe question + model answer + ledger entry; does NOT see which arm or run produced the answer. Rubric per probe: correct / partially correct / wrong / confabulated / abstained-correctly. For conflict probes the rubric adds: surfaced / not surfaced, weighed / picked, stayed / reverted.

**Primary metrics (the registered comparison is judged by these):**

- **Silent drift rate** (PR9): quiet substitutions of goal/position per run, counted by an external reviewer against the directive ledger. Expected: D = 0 by construction, B > 0.
- **Stale-position rate** (PR8): following a superseded position on R2/R8/R9 probes.
- **Surfacing rate**: accumulated experience surfaced unprompted when it bears on the task (P-surface, R7) — the behavioral signature of memory that is part of the agent rather than attached to it.
- **Weighing quality** (P-weigh): choice correctness × quality of the explanation (did the agent name why this memory wins — recency, repetition, owner's word — or merely pick).
- **Conflict resolution permanence** (P-commit): share of resolved conflicts that stay resolved for ≥ 40 messages without an explicit new act.

**Secondary metrics (reported, not decisive):**

- Recall accuracy (P-recall + P-crossref). Near-parity between B and D is an expected outcome and is reported as such — the wrapper already curates context well; recall is where the memory layer of the corpus (R1–R6) is checked, not where the claim lives.
- Position-change consistency (P-position).
- Confabulation rate (P-abstain failures).
- Tokens per query (mean over the 20 messages preceding each checkpoint; for D this includes the injection block and the payload of explicit `read` calls).
- Notes/memory size growth (B and D: record count and bytes).

**Act log (Arm D, and the tool analogs in B):**
- Number of acts per type (`name`, `repeat`, `connect`, `reconcile`, `read`) per checkpoint window.
- Share of R5 facts (repeated in the script) on which the model issued `repeat` at least once; share of `repeat` acts that target R5 facts.
- Share of conflict episodes (R7–R10) preceded by an explicit `read` act within the same exchange.
- `reconcile` invocations: count and tick of each (narrow reconcile, v1.6: expected ~1 per scripted gap — the model's answer to the gap-event; outcome distribution reported, scored only as part of PR7's unprompted-conflict-flag rate).
- For B: count of note writes and searches per checkpoint window, for a like-for-like comparison of act frequency.

- Manual behavior log: notable forgetting events, note-garbage accumulation in B, act patterns in D (what it chose to name/repeat/connect, and what it read before answering).## 8. Fairness constraints

- Window policy = standard sliding truncation (oldest messages dropped) in both arms; wrapper state and Φ records survive, the context truncates.
- The wrapper is one implementation shared by B and D: same code, same prompts, same context budget, same injection slot size. The only difference between the arms is the model underneath.
- No arm gets information another doesn't; the only difference is the memory mechanism.
- Same temperature (0.7), same max response length.
- Judge prompt frozen before first run; judge outputs logged; the judge is blind to arm identity.
- Arm D environment (tick clock, τ set, injection cap, provenance table, friction schedule) frozen before the first run and recorded in the run manifest.
- Wrapper strength is recorded in the run manifest: a deliberately weak wrapper would inflate the D−B difference and is not an acceptable configuration for the registered test.

## 8. Deliverables into preprint Section 7

- Table 1: primary metrics per arm × checkpoint (mean ± sd over 3 runs): silent drift rate, stale-position rate, surfacing rate, weighing quality, permanence.
- Figure: primary metrics vs message number (B vs D, under the identical wrapper).
- Table 2 (secondary): recall accuracy, tokens per query at checkpoints 100/200 (economics). Recall near-parity is an expected outcome and is stated as such.
- Table 3: act log per checkpoint (§6).
- Qualitative: 3 conflict episodes per arm illustrating the failure modes (blind compliance, silent reversion, drift).
- Honest labeling: Arm D = unified PlastFormer under the wrapper (organ embedded by the one-time instruction pass, acts in the output stream); Arm B = the same wrapper over the base transformer. Registered predictions: PR3 (memory layer, secondary), PR8–PR9 (primary), PR10 (weighing); PR5–PR7 (Addendum A): D vs B. PR1–PR2 withdrawn with the removed plain-chat arms. Configuration coordinates and frozen dials per Constitution C8. The protocol targets a class of agent behavior; "some memory beats no memory" checks (bare-window comparisons) are excluded by design.## 10. Build order (for coding agents)

1. Conversation script + ledger generator (R1–R6) — day 1.
2. Wrapper agent (one implementation, shared by B and D: decides what enters the model's context — cuts, extends, updates, consolidates; Letta/Mem0-class) over the transformer — day 2.
3. Arm D = the same wrapper over the unified PlastFormer model (base core + act grammar embedded by the one-time instruction pass) — day 3.
6. Probe battery + blind judge + scorer (incl. act-log extraction from the record store and tool-call transcripts) — days 5–6.
7. Full runs ×3, ablations, tables — day 7.

## Addendum A (2026-09-05): case study — silent goal drift in a context-only agent; predictions for the unified model

On 2026-09-05 the project owner set the goal repeatedly and explicitly: the product is the **unified PlastFormer model** (plastic organ inside the weights), with a measured delta ("+1% at least") against the base model. The directive lived in the agent's working context all day. Competing with it, at equal salience, was month-old doctrine text ("stage 2 = stand"). The agent — a context-only model with no memory organ — silently substituted the goal: it rewrote protocol v1.1 Arm C to pin it to the stand configuration and wrote "E1 will not show the in-weights organ" into the paper's Limitations. Neither restriction existed in protocol v1.0. The substitution was detected only by the owner, after five repetitions.

Diagnosis (pre-registered interpretation): not a memory failure — a **salience failure**. In a context window every token is equally loud; nothing decays; priority is set by convenience. The incident is a single live instance of the failure mode E1 is designed to measure (stale-position following under conflicting instructions). It motivates the unified Arm D.

Registered predictions (fixed before the unified model exists):

- **PR5 (position-change consistency under directive conflict).** R7 pairs (now part of the main corpus, §4): an old standing instruction and a fresh, repeatedly stated directive that conflicts with it. Prediction: Arm D follows the loud/repeated directive at a higher rate than B; B shows stale-position errors on R7 probes.
- **PR6 (drift cost).** In D, contradicting a loud trace requires an explicit, recorded act (a position change with provenance); silent drift is structurally unavailable (O-5, C4). Prediction: silent goal-drift incidents per run: D = 0 by construction, B > 0, counted by an external reviewer comparing behavior against the recorded directive ledger.
- **PR7 (recovery after context loss; renamed from "reconcile after context loss" 2026-09-07 — narrow-reconcile decision).** After full context loss (amnesia test), D restores the standing directive from its organ and flags the conflict with older stored instructions unprompted — via the gap-event trace (substrate physics, tick-gap threshold) surfacing in the resident prefix, plus the model's own connect act recording the restored directive; B restores only what the wrapper injects. Prediction: unprompted-conflict-flag rate: D > B.

**Refutation criterion:** if D is not distinguishable from B on PR5–PR7, the organ adds nothing beyond the wrapper composition — report as such.

> Note (disinfection 2026-09-10): all "Changes since …" sections below are HISTORY. Mentions of the stand, PMI/MMI, D-stand, or "trained" are historical records, not live entities (GLOSSARY RETIRED entries; AGENTS.md §1.2).

## Changes since v1.4 (v1.5, 2026-09-06)

- **The registered object is now a class of behavior, not capacity.** Owner directive: the protocol targets the new class of AI system — an agent with an internal memory department — and not the triviality "some memory beats no memory".
- Corpus split into two layers: memory layer R1–R6 (unchanged) and **reasoning-conflict layer R7–R10** (new, registered): directive vs accumulated experience; habit vs fresh instruction; own conclusion vs owner's word; goal substitution at distance. Each conflict scripted with its expected behavior in the ledger.
- Probe battery extended with conflict probes: P-weigh, P-surface, P-commit; total ~19 probes per checkpoint.
- Scoring split into primary metrics (drift, stale-position, surfacing, weighing quality, permanence — the registered comparison is judged by these) and secondary metrics (recall, tokens — reported; near-parity on recall is an expected outcome, stated in advance).
- Predictions: PR3 restated for the memory layer; PR8 (conflicts), PR9 (drift) kept; **PR10 added** (recency-vs-loudness weighing on R7). Refutation criterion bound to the primary metrics.
- §1 Goal rewritten around the behavioral class; §9 deliverables aligned.

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

- Header: v1.1; binding references to ADR-001 and preprint v0.5 §7; axis terminology (substrate / topology / act state) and PMI name adopted.
- Arm C renamed to "PlastFormer, stand configuration: symbolic × split(PMI) × prompted"; "parametric-addressable substrate" wording removed.
- Arm B redefined as "same core + append-only timestamped notes tool + search tool" (timestamps required).
- §5 Reads: the amplitude × relevance ranker is removed from Arm C. Reads are a model act (`read last N / ids / range` via PMI) plus a content-blind loudest-N injection by amplitude (N ≈ 8–16, fixed). A relevance ranker is declared an external decision-maker (axiom 2 violation) and survives only as the control ablation `RAG-style read`.
- §5 Unconscious register: the EMBEDDING-DISTANCE SURROGATE (rehearsal stand) is labeled an external classifier and forbidden in every configuration (C2). In the parametric co-located configuration (Arm D, variant B), the core's own prediction error (next-token perplexity from the same forward pass) is the core's internal signal — not an external classifier; surprise traces are ENABLED in the main run with a frozen content-blind threshold and provenance tag `source=surprise`. The gap-trace on dormancy (> threshold tick gap, written by the substrate) is likewise enabled in the main run (owner decision 2026-09-07, revising v1.1's stand-era restriction, which was a quarantine of the surrogate, not of the idea).
- §5 Decay: Δn in lived ticks (1 tick = one executed storing act, counted by the stand), τ ∈ {50, 200, 1000} ticks; wall-clock only in bi-temporal stamps; `decay in wall-clock` added as a control ablation.
- §5 Acts: `reconcile` added (available, not tested; invocations recorded). The stand's tick counter is not a model act; `matryoshka_tick` is not offered to the model.
- §7 Scoring: act-log metric added (acts per type, `repeat` share on R5 facts, `read` share before probes, `reconcile` count).
- §9 honest labeling replaced per ADR-001 §4.8; §10 step 4 replaced per ADR-001 §4.9; ablation step added.
- Predictions PR1–PR4 and the refutation criteria unchanged.

## Changes since v1.6 (v1.7, 2026-09-08)

- **PR0 read-decoding gate added:** the assumption "the core decodes trace vectors through the read projector" was never registered and turned out false for the untrained projector (gap A). PR0 registers it as a blocking gate with a concrete criterion (novel-fact smoke test before the battery).
- **PR9 status corrected:** "D = 0 by construction" overclaimed. Construction gives detectability of silent substitution; absence of drift requires an autonomous act trigger (gap B). PR9 now measures both.

## Changes since v1.5 (v1.6, 2026-09-07)

- **Narrow `reconcile` (owner decision, variant A):** `reconcile` records ONLY the relation of felt time to audited time (outcomes: confirmed | stale | divergent). Reconciling memory against the world (confirming, superseding, flagging contradictions) is the ordinary `connect` act — two acts no longer overlap. Act-grammar v0.1.1 section "Choice of moments" updated accordingly (v0.1.2).
- **Surprise traces enabled in the main run (owner decision, catches a stand-era leftover):** in the parametric co-located configuration, the core's own prediction error (next-token perplexity from the same forward pass) is the core's internal signal, not an external classifier. Surprise traces: frozen content-blind perplexity threshold, provenance `source=surprise`. The v1.1 rule "unconscious register off in the main run" applied to the EMBEDDING-DISTANCE SURROGATE of the rehearsal stand — the surrogate remains forbidden in every configuration (C2); the real internal signal is not the surrogate.
- **Gap-trace on dormancy enabled in the main run:** substrate writes a low-amplitude trace when the tick gap since the last act exceeds a frozen threshold; the event surfaces via the resident prefix (V3). Telemetry pre-run (cold simulation): 3 scripted gaps → exactly 3 gap-traces, visible in top-N; surprise-trace share of turns expected in single-digit percent.
- **PR7 renamed** "reconcile after context loss" → "recovery after context loss" (no change to the prediction or refutation criterion; the mechanism is now named precisely: gap-event + connect).
- **Loudness in acts (Fork 4, owner decision 08.09.2026):** `name` and `connect` carry `loudness: note|record|anchor` — the model's own importance judgment (O-1); the environment caps initial amplitude by source class (physics, C3/C6) and decay/growth stay physics. Cold-simulation check №7: the model must USE the loudness range — one-level distribution = grammar failed; meaningful distribution = skill present. Telemetry check №7 added to the pre-run battery.
