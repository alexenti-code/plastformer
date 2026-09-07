# Design: Parametric Phi — Variant B (trace bank + MAC interface)

**Status:** ENGINEERING DESIGN (owner review pending) — 07.09.2026
**Decision context:** E1 arm D needs a parametric substrate. Two candidates analyzed:
(A) rank-1 weight updates in a Titans-style memory block; (B) trace bank + learned
write/read interfaces at the MAC position. **Variant B selected** for E1 and the paper.

## 1. What variant B is

Phi = co-located trace bank. Each trace:

```
trace = {
  content:      verbatim text (hard facts, Sec 3.7) + content_vector (d_model=3840),
  provenance:   source class (user | own_derivation | tool_result),
                bi-temporal stamps (valid_time, record_tick),
  amplitude:    vector [a_1..a_k] over k decay speeds (tau components, THEORY),
  state:        act type (name | repeat | connect | reconcile), actor=K
}
```

Substrate physics (properties of the artifact; nobody executes them):
- decay `a_i(n) = a_i(0) * exp(-dn / tau_i)` (ticks, never wall-clock)
- tick counter by the substrate; act_price 1.0 tick; audibility_floor 0.01
- surfacing_cap 12 records (<= 2k tokens) per read

Two learned interfaces, both embedded by the single instruction pass (O-8), then frozen:
- write interface: model act (JSON in its own output) -> content_vector + amplitude -> bank
- read interface: loudest-N vectors by amplitude -> hidden space, inserted BEFORE attention
  at the MAC position

Trunk (all 48 layers of Gemma4-12B) unchanged after the grammar pass.
Skill = act grammar v0.1.1 embedded in the trunk (one pass, frozen).
Memory content = the bank, written only by the model's own acts (C4).

## 2. Why not variant A (rank-1 weight writes, Titans-style)

A is the literature reference for "memory in weights" — the comparison is required
for the paper, not for us. A stores traces AS weight updates; B stores traces AS
addressable records. Against our canon A breaks two of four requirements:

| Requirement | A | B |
|---|---|---|
| multi-tau cascade (Fusi/Benna) | broken: weights decay at one rate; keeping per-trace tau = factorized bank (= B with extra math) | native: amplitude is an explicit vector |
| verbatim hard facts (Sec 3.7) | not guaranteed: vector compression distorts; fails MRCR/RULER needles | native: verbatim text stored alongside vector |
| bi-temporal stamps | nowhere to put (open question, THEORY Sec 8) | explicit field |
| audit / E4 export | opaque | row-by-row export |

Titans writes everything through a surprise gate (unconscious register, our Sec 3.3
"physics"). B implements the conscious register: only explicit acts write (C4).
Honest framing: "Titans = unconscious writes + MAC; PlastFormer = conscious acts + MAC."
THEORY Sec 9 already marks rank-1 writes as future work; A remains a post-publication
research branch.

## 3. Why this is not RAG with vectors (registered arguments)

1. **Who decides what to read.** RAG: an external system ranks chunks by query
   relevance; the model is passive. B: the model itself emits the `read` act
   (last N / ids / from-to) in its own output (C1).
2. **How surfaced material is selected.** RAG: similarity(query, chunk),
   content-dependent. B: content-blind loudest-N by amplitude — no relevance, no
   embeddings, no keyword match, no query dependence (C2; e1-protocol). The trunk
   selects relevance AFTER insertion, with its own attention.
3. **Between reads.** RAG: static store. B: live physics — decay per tick,
   dormancy = zero lived time, act_price; the substrate is never static.
4. **Writes.** RAG: an external indexer writes. B: only the model's own acts write (C4),
   with its own trust-class and layer judgments.
5. **What is stored.** RAG: document chunks, model-independent. B: instance biography —
   provenance, two clocks, amplitude profile, refs; exportable artifact (E4).
6. **RAG-style read is a registered ablation** in e1-protocol ("relevance ranker =
   external decision-maker, axiom-2 violation, survives only as control ablation").
   The comparison is pre-registered, not improvised.

## 4. MAC position (Memory as Context, Titans arXiv:2501.00663 Sec 4.1)

Retrieved memory enters as a PREFIX of the sequence, in hidden space, before attention:

```
h_t   = M*_{t-1}(q_t)               # retrieve (Titans: similarity query)
St~_t = [p_1..p_Np] || h_t || S_t   # persistent || memory || current segment
y_t   = Attn(St~_t)
```

Why before attention: biography enters the attention field together with the input;
attention decides what matters now. Post-attention insertion could not steer perception.
Write late (post-step, mature representation), read early (pre-attention).

Differences from Titans-MAC (stated honestly in the paper):
- Titans retrieval is similarity-based (content-dependent); ours is amplitude-based
  (content-blind, C2). We deliberately take the dumber selector: the trunk does the
  intelligent work with its own attention.
- Titans' M trains by gradient at test time; our bank is written only by acts,
  trunk frozen.
- Insertion position is the same; we take the MAC mechanics, not the neural-memory
  mechanics.

## 5. Speed and resources (M1 Pro 16 GB, Gemma4-12B qat-4bit)

Model: d_model 3840, 48 layers, head_dim 256, 16 heads (8 KV).

Bank size (bf16 content vectors):
  1k traces ~ 8 MB | 10k ~ 77 MB | 100k ~ 768 MB | 1M ~ 7.7 GB (fits, at the limit)

Per-turn cost:
- amplitude sort: O(N log N), microseconds at 100k
- project 12 vectors: 12 x 3840^2 ~ 0.18 GFLOP — milliseconds on Metal
- MAC prefix insertion: concatenation — free
- attention over +12 positions: ~+0.3% per turn
- decay tick over 100k traces: vectorized, milliseconds

Total memory overhead < 1% of a turn; generation (~12 tok/s) remains the bottleneck.
The 200-message scenario (~2-3 h) is unaffected.

## 6. Honest caveats

- Not "memory in weights" literally: traces in the bank, interfaces in weights.
  Paper framing: frozen core + addressable plastic substrate; interfaces embedded once.
- The difference from RAG is governance (who decides), not access mechanics; both
  stated explicitly.
- Same insertion position as Titans-MAC; different selection and write register.

## 7. Build plan (5 modules, MLX)

1. Phi bank (mx.array + metadata): append, decay(tick), loudest-N, floor filter,
   export/import (E4), zeroing.
2. Write interface (projector d x d + small MLP): act JSON -> vector + amplitude.
3. Read interface (projector d x d): trace vectors -> hidden space; MAC-prefix
   insertion before attention (custom forward).
4. Grammar pass: act-grammar v0.1.1 embedded in the trunk (one LoRA pass, frozen).
5. Harness: substrate, ticks, act acknowledgements, judge channel.
