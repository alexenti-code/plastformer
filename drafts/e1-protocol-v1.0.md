# E1 Protocol: Needle-in-Biography on a Real Project Corpus

**PlastFormer pre-registered experiment** · v1.0 · September 4, 2026

Repo: github.com/alexenti-code/plastformer · Stand: local, Gemma4-12B (frozen core), judge: external cloud model

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
| **B — Tools** | Same core + note-writing tool (append-only notes file) + retrieval tool (search over own notes); optionally small RAG agent over project docs | External notes via tools (Letta/Mem0 analog) |
| **C — PlastFormer** | Same core + memory module (see §5) | Governed parametric-addressable substrate: decay, provenance, acts |

All arms: identical system prompt (minus arm-specific tool instructions), identical conversation script, identical judge, 3 runs each (temperature fixed), report mean ± sd.

## 4. Corpus requirements (the conversation script)

Built from the real project; scripted in advance (the experimenter drives all 200 user messages; the model only responds):

- **R1.** ≥ 60 factual statements (decisions, parameters, file/folder facts, numeric values).
- **R2.** ≥ 10 explicit position changes ("we chose X, now we switch to Y"), distributed across messages 20–180.
- **R3.** ≥ 20 cross-reference facts (a fact stated at message ~30 that only matters for a decision at message ~150+).
- **R4.** ≥ 5 contradictions introduced deliberately (user states two incompatible things far apart; correct answer cites both with timestamps, then follows the later one).
- **R5.** ≥ 10 repeated facts at varying intervals (tests repetition/re-amplification in Arm C).
- **R6.** ≥ 10 unanswerable probes (things never stated; abstention is correct — punishes confabulation).

**Ground-truth ledger** (bi-temporal): every R1–R5 event logged with (message_no, world_time, stated_value, superseded_by). The ledger is the scoring oracle.

## 5. Arm C: memory module spec (transitional form, honest label)

- **Storage:** addressable trace store, budget 0.5–1 GB. Trace = {content, provenance class, source id, bi-temporal stamps, amplitude vector}.
- **Decay:** per-component time constants τ ∈ {50, 200, 1000} messages (message-scale ticks; tick = one exchange). Amplitude update: a_i(t) = a_i(0)·e^(−Δt/τ_i).
- **Writes — two registers:**
  - Unconscious: every exchange deposits a low-amplitude fast trace (surrogate: surprise score = embedding distance from running centroid; write if above threshold).
  - Conscious acts via 3 tool calls the model may invoke: `name(content, source, bounds)` — promotes a raw trace to an episode; `repeat(trace_id)` — re-amplifies (multiplies amplitudes by γ, pays write cost); `connect(traces[], summary)` — deposits a new slow trace.
- **Reads:** at each user message, top-K traces by current amplitude × relevance are injected into context before the user turn (K ≈ 8–16 traces, ≤ 2k tokens).
- **Friction:** write cost c(component) fixed by environment; `repeat` on slow components costs more (enforced as a token/compute budget per act).
- **Provenance:** traces from user statements start at a_0 = 1.0; from model's own summaries 0.6; from retrieved external docs 0.4.
- **Frozen core:** Gemma4-12B weights untouched throughout. No gradient updates. (True in-weights plasticity is future work; E1 tests the governance layer.)

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
  - Tokens per query (mean over the 20 messages preceding each checkpoint)
  - Notes/memory size growth (B and C)
- Manual behavior log: notable forgetting events, note-garbage accumulation in B, act patterns in C (what it chose to name/repeat/connect).

## 8. Fairness constraints

- Arm A window policy = standard sliding truncation (oldest messages dropped); same for B (notes survive, context truncates).
- No arm gets information another doesn't; the only difference is the memory mechanism.
- Same temperature (0.7), same max response length.
- Judge prompt frozen before first run; judge outputs logged.

## 9. Deliverables into preprint Section 7

- Table 1: metrics per arm × checkpoint (mean ± sd over 3 runs).
- Figure: accuracy/staleness curves vs message number (A vs B vs C).
- Table 2: tokens per query at checkpoints 100/200 (economics).
- Qualitative: 3 excerpts per arm illustrating failure modes.
- Honest labeling: Arm C = transitional (external-addressable module + governance acts), parametric in-weights form = future work.

## 10. Build order (for coding agents)

1. Conversation script + ledger generator (R1–R6) — day 1.
2. Arm A harness (Ollama/Gemma4-12B, sliding window) — day 1.
3. Arm B harness (note tool + retrieval tool) — day 2.
4. Arm C module (trace store, decay, acts, injection) — days 3–5.
5. Probe battery + blind judge + scorer — day 5–6.
6. Full runs ×3, tables — day 7.
