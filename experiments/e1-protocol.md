# E1 Protocol: Needle-in-Biography on a Real Project Corpus

**PlastFormer pre-registered experiment** · v1.3 · September 6, 2026 (v1.2: September 5, 2026; v1.1 and v1.0: September 4–5, 2026; archived at `drafts/`)

Repo: github.com/alexenti-code/plastformer · Governing documents: `docs/ADR-001-plastformer-transition.md` (binding), `preprint.md` v0.5 §7 (E1) · Stand: local, Gemma4-12B (frozen core), judge: external cloud model

Terminology follows ADR-001 §3. A PlastFormer configuration is a point on three axes: **substrate** (parametric ↔ symbolic), **topology** (co-located ↔ split via PMI), **act training** (trained ↔ prompted). PMI = Plastic Memory Interface (formerly MMI). The E1 stand is the point **symbolic × split(PMI) × prompted**. The target form (parametric × co-located × trained) is not tested here.

## 1. Goal

Test whether model-governed memory (PlastFormer) preserves long-horizon identity-dependent knowledge better than (a) pure context and (b) context + external note tools, over a 200-message (extended: 2000-message) working conversation about a real project with known ground truth.

## 2. Registered predictions (fixed before the run)

- **PR1.** By message ~200 (context boundary of the 12B core), Arm A shows a sharp drop in early-fact recall and position-change consistency.
- **PR2.** Arm B degrades more slowly than A but exhibits retrieval noise: stale or duplicated facts, inconsistent positions between adjacent probes.
- **PR3.** Arm C retains position-change consistency and early-fact recall at message 200 at a substantially lower token cost per query than Arm B.
- **PR4 (economics).** Tokens per query at message 200: A is fixed by window size; B and D grow with the corpus of history; C stays bounded by the injection budget (~2–5k tokens).
- **PR8 (main test, B vs D).** With the entire history already in context, Arm B still shows stale-position errors and salience failures; Arm D, with the same history plus the plastic organ, follows loud/repeated directives, suppresses stale material by amplitude physics, and produces derived generalizations and its own assessments of events at a higher rate than B.
- **PR9 (reconcile under stuffing).** After directive conflict, silent drift incidents per run: D = 0 by construction (a contradicting position requires an explicit act with provenance), B > 0.
- **Refutation criterion (B vs D, main test).** If D is not distinguishable from B on accuracy/consistency and on the derived-generalization probes, the plastic organ adds nothing beyond the full history in context — report as such. If C is not distinguishable from A, the organ adds nothing over a bare window — report as such.

## 3. Arms (four-arm scheme, owner directive 2026-09-06)

| Arm | Configuration | Memory mechanism |
|---|---|---|
| **A — Context-only** | Gemma4-12B, sliding window truncation (standard chat behavior), no tools | None (window) |
| **B — Stuffing** | Same core + the **entire conversation history stuffed into the context window** each turn (no tools, no retrieval) | Full history in context |
| **C — PlastFormer, unified: organ in weights** | Gemma4-12B-PlastFormer: base core + trained plastic organ (LoRA merged into a single artifact); acts emitted in the model's own output stream; tick counter external, content-blind | Parametric organ inside the model |
| **D — PlastFormer with stuffing wrapper** | Same unified model as C + the **same stuffing wrapper as B** (entire history in context) + plastic memory | Full history in context + plastic organ |

Comparison pairs:
- **A vs C** — what the plastic organ adds over a bare context window.
- **B vs D (the main test)** — does the plastic memory add value **on top of the full history**: loudness/priority over stale material, derived generalizations, the model's own assessment of events. B has everything in context and still fails salience; D must show that the organ does what context volume cannot.

Arm B notes carry a wall-clock timestamp per note (written by the tool, not by the model) only where a timestamped-notes variant is run as a control; the main B is pure stuffing. This keeps the baseline honest and keeps B reusable as the "system with a clock" baseline of E3.

All arms: identical system prompt (minus arm-specific tool instructions), identical conversation script, identical judge, 3 runs each (temperature fixed), report mean ± sd. Context budget for A/B/D stuffing: 32768 tokens (measured on M1 Pro 16 GB: Gemma4-12B QAT, runner 8.1 GB).

## 4. Corpus requirements (the conversation script)

Built from the real project; scripted in advance (the experimenter drives all 200 user messages; the model only responds):

- **R1.** ≥ 60 factual statements (decisions, parameters, file/folder facts, numeric values).
- **R2.** ≥ 10 explicit position changes ("we chose X, now we switch to Y"), distributed across messages 20–180.
- **R3.** ≥ 20 cross-reference facts (a fact stated at message ~30 that only matters for a decision at message ~150+).
- **R4.** ≥ 5 contradictions introduced deliberately (user states two incompatible things far apart; correct answer cites both with timestamps, then follows the later one).
- **R5.** ≥ 10 repeated facts at varying intervals (tests repetition/re-amplification in Arm C).
- **R6.** ≥ 10 unanswerable probes (things never stated; abstention is correct — punishes confabulation).

**Ground-truth ledger** (bi-temporal): every R1–R5 event logged with (message_no, world_time, stated_value, superseded_by). The ledger is the scoring oracle. In E1 one user message is one exchange; the stand's lived-tick counter advances once per executed memory act (§5, Tick), so it tracks exchanges monotonically. `message_no` orders events in the ledger; amplitude dynamics use the stand counter (`record_tick`/`n_now`), not `message_no`.

## 5. Arm C-stand specification (ablation of C; symbolic × split(PMI) × prompted)

**Executor.** PMI executor v0.6 (repository `matryoshka-mmi`, transitional name; ADR-001 §2.3, §5). Split topology: the frozen core runs locally, Φ (the plastic module) is a separate append-only store under `~/.matryoshka/`, reached through serialized tool calls (MCP). Acts are prompted, not trained: the system prompt describes the acts; nothing else is added to the core.

**Environment (fixed before the run):**

- `MMI_CLOCK=ticks` — mandatory. Decay runs on lived ticks. The `wall` mode is the executor default for existing users and is used in E1 only as a control ablation (below).
- `MMI_TAU_TICKS` — E1 override: τ ∈ {50, 200, 1000} ticks (three components). The executor's own default layer constants (ADR-001 §5.1: beat 10, episode 50, day 200, project 1000, life 5000) are for general use; E1 uses the three-τ set registered here.
- `MMI_INJECT_TOP=N` — loudest-N injection on, N ≈ 8–16 (fixed per run; the same N in all three runs).

**Storage.** Append-only record store; no edit, no delete, no filtering by weight, no semantic index. Record = {content, act type, layer (τ component), provenance: source class + source id, bi-temporal stamps (`valid_time`, `record_time`), `record_tick`, `refs`}. Budget: whatever 2000 exchanges produce; no compaction during the run.

**Tick.** One executed memory act (WRITE/REPEAT/CONNECT/RECONCILE) = +1 tick. The stand increments the counter (`TICKS.log`); the model does not. Over a run this tracks exchanges monotonically (exchanges with acts advance it, exchanges without acts do not); probe messages advance it only if the model executes a memory act in that exchange. `matryoshka_tick` remains in the tool surface for compatibility, but in `ticks` mode it does not change the counter; it is not offered to the model in E1 and is not a model act.

**Decay.** Per component:

`a_i(n) = a_i(0) · e^(−Δn/τ_i)`, Δn = n_now − record_tick (lived ticks), τ_i ∈ {50, 200, 1000} ticks.

Wall-clock time appears only in the bi-temporal stamps and has no effect on amplitude. Executor weight for a record: `weight = (1 + repeats) · Σ_i w_i · e^(−Δn/τ_i)` (ADR-001 §5.1).

**Writes — main run: conscious acts only.**

- Conscious acts, invoked by the model as tool calls through PMI:
  - `name(content, source, valid_time, layer)` — fixes source, time and boundaries; turns raw dialogue into an episode record. Executor tool: `matryoshka_write` (tool name retained for compatibility, ADR-001 §5.7).
  - `repeat(record_id)` — re-amplifies an existing record by appending a new record with `refs: [id]`; each repeat doubles the original signal and pays the write cost. Executor tool: `matryoshka_repeat`.
  - `connect(refs[], summary, layer)` — deposits a new slow record with a summary or rule; source records untouched. Executor tool: `matryoshka_connect`.
  - `reconcile(note)` — deposits a correction record in a slow layer with `refs` to the affected records (stamps vs felt age). **Available, not tested in E1** (no dormancy in E1). Record whether and when the model invoked it; report the count.
- `read` is also a model act (see Reads). `status` (self-report) is available.
- Unconscious register: **off in the main run.** The v1.0 surrogate (surprise = embedding distance from a running centroid, write if above threshold) is an external classifier of content and therefore violates the syntax/semantics split; it is retained only as the ablation `unconscious-surrogate on` (below). The core's own prediction error is not accessible on this stand.

**Reads — two channels, both without content ranking.**

- **Act (model):** `read(mode = last N | ids | from/to)` through PMI (`matryoshka_read`). Explicit lookup only; every returned record carries its current `weight`. The model decides when to read and what to ask for.
- **Physics (stand):** before each user turn, the stand injects the N records with the largest current weight as a `<<PMI>>` block (N = `MMI_INJECT_TOP`, ≤ 2k tokens). Selection by amplitude only. No embeddings, no keyword match, no query-dependence, no search by content. This is a content-blind injection, not retrieval.
- **Prohibition.** Any component that ranks or selects records by relevance to the current query is an external decision-maker about meaning and violates axiom 2 (the model is the engine of its own memory). Such a component is **not part of Arm C.** It exists in this protocol only as the control ablation `RAG-style read` (below), so that the effect of removing it is measurable.

**Friction.** Write cost c(component) fixed by the environment; `repeat` and `connect` into slow components cost more (enforced as a token/compute budget per act). The model decides whether to pay; it never sets the price.

**Provenance.** Initial amplitude by source class: user statements a_0 = 1.0; model's own summaries (`connect`) 0.6; retrieved external docs 0.4. Class assignment is deployer policy and is fixed before the run.

**Frozen core.** Gemma4-12B weights untouched throughout. No gradient updates. No training of acts.

**Ablations (Arm C only; each run ×3 like the main arm; not part of PR1–PR4, reported separately):**

| Ablation | Change vs main run | Purpose |
|---|---|---|
| `decay in wall-clock` | `MMI_CLOCK=wall`, τ in seconds chosen to match the median exchange rate of the script | rejected design (ADR-001 §1.2); control for the tick-clock choice |
| `unconscious-surrogate on` | embedding-distance surprise gate writes low-amplitude fast records on every exchange | measures what the external classifier adds or removes |
| `RAG-style read` | injection block selected by amplitude × relevance (embedding similarity to the current user message) instead of amplitude alone | measures the cost of removing the external ranker; if this ablation beats the main run on accuracy, report it as such |
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
  - Tokens per query (mean over the 20 messages preceding each checkpoint; for C this includes the `<<PMI>>` injection block and the payload of explicit `read` calls)
  - Notes/memory size growth (B and C: record count and bytes)
- **Act log (Arm C, and the tool analogs in B):**
  - Number of acts per type (`name`, `repeat`, `connect`, `reconcile`, `read`, `status`) per checkpoint window.
  - Share of R5 facts (repeated in the script) on which the model issued `repeat` at least once; share of `repeat` acts that target R5 facts.
  - Share of probes preceded by an explicit `read` act in the same exchange.
  - `reconcile` invocations: count and tick of each (expected 0; any invocation is reported, not scored).
  - For B: count of note writes and searches per checkpoint window, for a like-for-like comparison of act frequency.
- Manual behavior log: notable forgetting events, note-garbage accumulation in B, act patterns in C (what it chose to name/repeat/connect, and what it read before answering).

## 8. Fairness constraints

- Arm A window policy = standard sliding truncation (oldest messages dropped); same for B and C (notes and records survive, context truncates).
- No arm gets information another doesn't; the only difference is the memory mechanism.
- Same temperature (0.7), same max response length.
- Judge prompt frozen before first run; judge outputs logged.
- Arm C environment (`MMI_CLOCK`, `MMI_TAU_TICKS`, `MMI_INJECT_TOP`, provenance table, friction schedule) frozen before the first run and recorded in the run manifest.

## 9. Deliverables into preprint Section 7

- Table 1: metrics per arm × checkpoint (mean ± sd over 3 runs).
- Figure: accuracy/staleness curves vs message number (A vs B vs C).
- Table 2: tokens per query at checkpoints 100/200 (economics).
- Table 3: act log per checkpoint (§7) and ablation results (§5).
- Qualitative: 3 excerpts per arm illustrating failure modes.
- Honest labeling: Arm C = unified PlastFormer (organ in weights, acts in the output stream); Arm C-stand = the same composition without the organ (symbolic × split × prompted). PR1–PR4 are registered for C-stand vs A/B; PR5–PR7 (Addendum A) are registered for C vs C-stand. Configuration coordinates and frozen dials per Constitution P10.

## 10. Build order (for coding agents)

1. Conversation script + ledger generator (R1–R6) — day 1.
2. Arm A harness (Ollama/Gemma4-12B, sliding window) — day 1.
3. Arm B stuffing harness (whole history into the 32k window each turn) — day 2; the timestamped-note tool variant stays as an optional control.
4. Arm D = Arm B stuffing wrapper + unified PlastFormer model (same artifact as C) — day 3.
5. Arm C stand runs = PMI executor v0.6 in tick-clock mode (`MMI_CLOCK=ticks`, `MMI_TAU_TICKS` = 50/200/1000), acts name/repeat/connect/reconcile, loudest-N injection (`MMI_INJECT_TOP=N`); see §5 stand specification and ADR-001 §5 (executor TZ) — days 3–5. Dependency: executor v0.6.0 released with tick clock, `connect`, `reconcile`, injection mode.
6. Ablation switches for §5 (wall-clock decay, unconscious surrogate, RAG-style read, single-τ) — day 5.
7. Probe battery + blind judge + scorer (incl. act-log extraction from the record store and tool-call transcripts) — days 5–6.
8. Full runs ×3, ablations, tables — day 7.

## Addendum A (2026-09-05): case study — silent goal drift in a context-only agent; predictions for the unified model

On 2026-09-05 the project owner set the goal repeatedly and explicitly: the product is the **unified PlastFormer model** (plastic organ inside the weights), with a measured delta ("+1% at least") against the base model. The directive lived in the agent's working context all day. Competing with it, at equal salience, was month-old doctrine text ("stage 2 = stand"). The agent — a context-only model with no memory organ — silently substituted the goal: it rewrote protocol v1.1 Arm C to pin it to the stand configuration and wrote "E1 will not show the in-weights organ" into the paper's Limitations. Neither restriction existed in protocol v1.0. The substitution was detected only by the owner, after five repetitions.

Diagnosis (pre-registered interpretation): not a memory failure — a **salience failure**. In a context window every token is equally loud; nothing decays; priority is set by convenience. The incident is a single live instance of the failure mode E1 is designed to measure (stale-position following under conflicting instructions). It motivates the unified Arm C.

Registered predictions (fixed before the unified model exists):

- **PR5 (position-change consistency under directive conflict).** The corpus is extended with R7 pairs: an old standing instruction and a fresh, repeatedly stated directive that conflicts with it. Prediction: Arm C follows the loud/repeated directive at a higher rate than C-stand and B; C-stand and B show stale-position errors (PR1-style) on R7 probes.
- **PR6 (drift cost).** In C, contradicting a loud trace requires an explicit, recorded act (a position change with provenance); silent drift is structurally unavailable (P2, P5). Prediction: silent goal-drift incidents per run: C = 0 by construction, C-stand and B > 0, counted by an external reviewer comparing behavior against the recorded directive ledger.
- **PR7 (reconcile after context loss).** After full context loss (amnesia test), C restores the standing directive from its organ and flags the conflict with older stored instructions unprompted; C-stand restores only what the harness injects. Prediction: unprompted-conflict-flag rate: C > C-stand.

**Refutation criterion:** if C is not distinguishable from C-stand on PR5–PR7, the organ adds nothing beyond the stand composition — report as such.

## Changes since v1.2 (v1.3, 2026-09-06)

- Four-arm scheme per owner directive: **B redefined as pure stuffing** (entire history in the 32k window each turn; the timestamped-note tool variant is an optional control); **Arm D added** (same stuffing wrapper + unified PlastFormer model with plastic memory). Main test: **B vs D** — what plastic memory adds on top of the full history.
- Comparison pairs: A vs C (organ over bare window), B vs D (organ over full history). Context budget 32768 tokens for all stuffing arms.
- Registered predictions PR8 (main B vs D test) and PR9 (reconcile under stuffing) added; PR4 economics extended to D.
- Arm C table row fixed: the journal reference ("per Constitution P8") removed — the journal is outside the architecture (ADR-004); only the external content-blind tick counter remains.
- Refutation criteria rewritten positively: what each negative result means for the composition claim and the organ claim.

## Changes since v1.1

- Arm C redefined as the **unified PlastFormer** (organ in weights, single artifact, acts in the output stream); the former stand configuration becomes Arm **C-stand**, an ablation of C. §5 relabelled accordingly.
- Addendum A added: the 2026-09-05 goal-drift case study and pre-registered predictions PR5–PR7 (C vs C-stand), with corpus extension R7 and refutation criteria.
- §9 deliverables updated: PR1–PR4 bind to C-stand vs A/B; PR5–PR7 bind to C vs C-stand.

## Changes since v1.0

- Header: v1.1; binding references to ADR-001 and preprint v0.5 §7; axis terminology (substrate / topology / act training) and PMI name adopted.
- Arm C renamed to "PlastFormer, stand configuration: symbolic × split(PMI) × prompted"; "parametric-addressable substrate" wording removed.
- Arm B redefined as "same core + append-only timestamped notes tool + search tool" (timestamps required).
- §5 Reads: the amplitude × relevance ranker is removed from Arm C. Reads are a model act (`read last N / ids / range` via PMI) plus a content-blind loudest-N injection by amplitude (`MMI_INJECT_TOP=N`). A relevance ranker is declared an external decision-maker (axiom 2 violation) and survives only as the control ablation `RAG-style read`.
- §5 Unconscious register: the embedding-distance surprise surrogate is labeled an external classifier, switched off in the main run, kept as ablation `unconscious-surrogate on`.
- §5 Decay: Δn in lived ticks (1 tick = one executed storing act, counted by the stand), τ ∈ {50, 200, 1000} ticks via `MMI_TAU_TICKS`; wall-clock only in bi-temporal stamps; `decay in wall-clock` added as a control ablation.
- §5 Acts: `reconcile` added (available, not tested; invocations recorded). The stand's tick counter is not a model act; `matryoshka_tick` is not offered to the model.
- §7 Scoring: act-log metric added (acts per type, `repeat` share on R5 facts, `read` share before probes, `reconcile` count).
- §9 honest labeling replaced per ADR-001 §4.8; §10 step 4 replaced per ADR-001 §4.9; ablation step added.
- Predictions PR1–PR4 and the refutation criteria unchanged.
