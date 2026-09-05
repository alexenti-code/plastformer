# E1 Protocol: Needle-in-Biography on a Real Project Corpus

**PlastFormer pre-registered experiment** · v1.1 · September 5, 2026 (v1.0: September 4, 2026; archived at `drafts/e1-protocol-v1.0.md`)

Repo: github.com/alexenti-code/plastformer · Governing documents: `docs/ADR-001-plastformer-transition.md` (binding), `preprint.md` v0.5 §7 (E1) · Stand: local, Gemma4-12B (frozen core), judge: external cloud model

Terminology follows ADR-001 §3. A PlastFormer configuration is a point on three axes: **substrate** (parametric ↔ symbolic), **topology** (co-located ↔ split via PMI), **act training** (trained ↔ prompted). PMI = Plastic Memory Interface (formerly MMI). The E1 stand is the point **symbolic × split(PMI) × prompted**. The target form (parametric × co-located × trained) is not tested here.

## 1. Goal

Test whether model-governed memory (PlastFormer) preserves long-horizon identity-dependent knowledge better than (a) pure context and (b) context + external note tools, over a 200-message (extended: 2000-message) working conversation about a real project with known ground truth.

## 2. Registered predictions (fixed before the run)

- **PR1.** By message ~200 (context boundary of the 12B core), Arm A shows a sharp drop in early-fact recall and position-change consistency.
- **PR2.** Arm B degrades more slowly than A but exhibits retrieval noise: stale or duplicated facts, inconsistent positions between adjacent probes.
- **PR3.** Arm C retains position-change consistency and early-fact recall at message 200 at a substantially lower token cost per query than Arm B.
- **PR4 (economics).** Tokens per query at message 200: A is fixed by window size; B grows with corpus of notes; C stays bounded by the injection budget (~2–5k tokens).
- **Falsifier.** If C is not distinguishable from B on accuracy/consistency, the composition claim (governance layer) is not supported. Report as such.

## 3. Arms

| Arm | Configuration | Memory mechanism |
|---|---|---|
| **A — Context-only** | Gemma4-12B, sliding window truncation (standard chat behavior), no tools | None (window) |
| **B — Tools** | Same core + append-only **timestamped** notes tool + search tool over own notes; optionally small RAG agent over project docs | External timestamped notes via tools (Letta/Mem0 analog) |
| **C — PlastFormer, stand configuration: symbolic × split(PMI) × prompted** | Same core + PMI executor v0.6 in tick-clock mode (see §5) | Symbolic traces in an append-only store; decay in lived ticks, provenance, model acts |

Arm B notes carry a wall-clock timestamp per note (written by the tool, not by the model). This keeps the baseline honest (a note tool without stamps is weaker than any deployed analog) and keeps B reusable as the "system with a clock" baseline of E3.

All arms: identical system prompt (minus arm-specific tool instructions), identical conversation script, identical judge, 3 runs each (temperature fixed), report mean ± sd.

## 4. Corpus requirements (the conversation script)

Built from the real project; scripted in advance (the experimenter drives all 200 user messages; the model only responds):

- **R1.** ≥ 60 factual statements (decisions, parameters, file/folder facts, numeric values).
- **R2.** ≥ 10 explicit position changes ("we chose X, now we switch to Y"), distributed across messages 20–180.
- **R3.** ≥ 20 cross-reference facts (a fact stated at message ~30 that only matters for a decision at message ~150+).
- **R4.** ≥ 5 contradictions introduced deliberately (user states two incompatible things far apart; correct answer cites both with timestamps, then follows the later one).
- **R5.** ≥ 10 repeated facts at varying intervals (tests repetition/re-amplification in Arm C).
- **R6.** ≥ 10 unanswerable probes (things never stated; abstention is correct — punishes confabulation).

**Ground-truth ledger** (bi-temporal): every R1–R5 event logged with (message_no, world_time, stated_value, superseded_by). The ledger is the scoring oracle. In E1 one user message is one exchange; the stand's lived-tick counter advances once per executed memory act (§5, Tick), so it tracks exchanges monotonically. `message_no` orders events in the ledger; amplitude dynamics use the stand counter (`record_tick`/`n_now`), not `message_no`.

## 5. Arm C: stand specification (symbolic × split(PMI) × prompted)

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
- Honest labeling: Arm C = PlastFormer, stand configuration symbolic × split(PMI) × prompted; E1 tests the governance + physics composition, not the parametric substrate and not trained acts (see preprint §8).

## 10. Build order (for coding agents)

1. Conversation script + ledger generator (R1–R6) — day 1.
2. Arm A harness (Ollama/Gemma4-12B, sliding window) — day 1.
3. Arm B harness (timestamped note tool + search tool) — day 2.
4. Arm C = PMI executor v0.6 in tick-clock mode (`MMI_CLOCK=ticks`, `MMI_TAU_TICKS` = 50/200/1000), acts name/repeat/connect/reconcile, loudest-N injection (`MMI_INJECT_TOP=N`); see §5 stand specification and ADR-001 §5 (executor TZ) — days 3–5. Dependency: executor v0.6.0 released with tick clock, `connect`, `reconcile`, injection mode.
5. Ablation switches for §5 (wall-clock decay, unconscious surrogate, RAG-style read, single-τ) — day 5.
6. Probe battery + blind judge + scorer (incl. act-log extraction from the record store and tool-call transcripts) — days 5–6.
7. Full runs ×3, ablations, tables — day 7.

## Changes since v1.0

- Header: v1.1; binding references to ADR-001 and preprint v0.5 §7; axis terminology (substrate / topology / act training) and PMI name adopted.
- Arm C renamed to "PlastFormer, stand configuration: symbolic × split(PMI) × prompted"; "parametric-addressable substrate" wording removed.
- Arm B redefined as "same core + append-only timestamped notes tool + search tool" (timestamps required).
- §5 Reads: the amplitude × relevance ranker is removed from Arm C. Reads are a model act (`read last N / ids / range` via PMI) plus a content-blind loudest-N injection by amplitude (`MMI_INJECT_TOP=N`). A relevance ranker is declared an external decision-maker (axiom 2 violation) and survives only as the control ablation `RAG-style read`.
- §5 Unconscious register: the embedding-distance surprise surrogate is labeled an external classifier, switched off in the main run, kept as ablation `unconscious-surrogate on`.
- §5 Decay: Δn in lived ticks (1 tick = 1 exchange, counted by the stand), τ ∈ {50, 200, 1000} ticks via `MMI_TAU_TICKS`; wall-clock only in bi-temporal stamps; `decay in wall-clock` added as a control ablation.
- §5 Acts: `reconcile` added (available, not tested; invocations recorded). The stand's tick counter is not a model act; `matryoshka_tick` is not offered to the model.
- §7 Scoring: act-log metric added (acts per type, `repeat` share on R5 facts, `read` share before probes, `reconcile` count).
- §9 honest labeling replaced per ADR-001 §4.8; §10 step 4 replaced per ADR-001 §4.9; ablation step added.
- Predictions PR1–PR4 and the falsifier unchanged.
