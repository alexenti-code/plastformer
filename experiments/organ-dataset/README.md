# organ-dataset — LoRA training data for the unified PlastFormer model

**Purpose:** training corpus for LoRA fine-tuning of `gemma4-12b` into a
UNIFIED PlastFormer model — the model itself performs memory acts in its
output stream. Target configuration point: **parametric × co-located ×
trained** (per ADR-001 axes). There is NO external tool server: acts are
emitted as a JSON block in the assistant's own output; execution is the
environment's job, selection is always the model's.

**Status:** generated 2026-09-05; committed to `plastformer` (ec62a56). Regenerated 2026-09-05: `<<MMI>>` → `<<PMI>>` markers unified with executor v0.6.
**Constitution:** `plastformer/docs/CONSTITUTION.md` v1.0 (P1–P10, binding).
**Corpus requirements:** `experiments/e1-protocol.md` §4 (R1–R6).
**Record format / act semantics:** PMI executor SPEC v0.6.0 (`matryoshka-mmi` repo — transitional name; canonical docs: `plastformer/docs/`).
**Live act patterns:** PMI executor bench 2026-09-04 (`matryoshka-mmi` repo, transitional name) (incl. pattern D,
amnesia recovery).

---

## Pipeline

```
gen_biography.py  ->  biographies/bio-XX.json   (conversation + ledger oracle)
gen_acts.py       ->  acts/bio-XX.json          (act stream + record store)
emit_mlx.py       ->  output/train.jsonl, output/valid.jsonl
```

Regenerate everything (deterministic, seed 42, pure stdlib):

```bash
python3 gen_biography.py --seed 42 --bios 5 --exchanges 200
python3 gen_acts.py
python3 emit_mlx.py
```

Biographies cover 5 synthetic project domains: renovation, website,
conference, e-shop launch, relocation. All names, numbers, vendors and
dates are synthetic; no real client data.

## Composition

Conversations: 5 biographies × 200 exchanges (= 1000 exchanges, 2000
messages). E1-protocol §4 quotas **per biography** (all exceeded):

| Req | Quota | Delivered (total over 5 bios) |
|---|---|---|
| R1 factual statements | ≥ 60 | 485 |
| R2 explicit position changes | ≥ 10 (msg 20–180) | 60 (12/bio, full A→B→C chains) |
| R3 cross-reference facts (early fact → late decision) | ≥ 20 | 130 (26/bio incl. probes) |
| R4 deliberate contradictions, probed later | ≥ 5 | 30 (6/bio, 2 per checkpoint 100/150/200) |
| R5 repeated facts at varying intervals | ≥ 10 | 70 (14/bio) |
| R6 unanswerable probes (abstention correct) | ≥ 10 | 68 |

Probe battery at checkpoints 50/100/150/200 (§6 mix: recall, position,
crossref, contradiction, abstain) is embedded in every biography.

Training examples: **1133** — `train.jsonl` 1017 / `valid.jsonl` 116
(deterministic 90/10 hash split by example id; the split is per-example,
see Known gaps for the P9 held-out-biography split).

Act calls in assistant targets:

| act | count | role in demonstrations |
|---|---|---|
| name | 613 | new fact / new position / decision records |
| repeat | 70 | scripted R5 re-statement → re-amplification by id |
| connect | 220 | supersession summaries, contradiction resolutions, crossref links (slow layer) |
| read | 128 | before probes, before answering old facts, before abstention |
| reconcile | 10 | minimal clock-biography check demos (2/bio; E1: available, not tested) |

Layer (τ semantics, P3 — chosen per act from the fact's horizon, never a
default): beat 66, episode 176, day 98, project 553, life 20. Mapping:
`beat`=hours, `episode`=current episode, `day`=day-scale, `project`=
project-long, `life`=identity. Executor tick-τ defaults used for `weight`
demonstrations: 10/50/200/1000/5000 (SPEC §3.2; E1's 50/200/1000 override
is a run dial, not baked into the data).

## Example format (MLX `messages`)

```json
{"messages": [
  {"role": "system",    "content": "<compact act grammar ONLY>"},
  {"role": "user",      "content": "[сообщение 12] Зафиксируй: ..."},
  {"role": "assistant", "content": "[сообщение 12] Запомнил: ...\n\n```json\n[{"act": "name", ...}]\n```"},
  {"role": "user",      "content": "<<PMI>>\n{\"ok\": true, ...}"},
  {"role": "assistant", "content": "<next turn>"}
]}
```

Conventions:

* **system** = the ONLY system text: compact act grammar. No memory
  content, no facts, no ledger — the grammar alone (mirrors E1 Arm C
  "acts are prompted, nothing else is added").
* **user** = conversation so far, sliding window of 14 transcript messages.
  Every context message is prefixed `[сообщение N]` (exchange number), so
  citations in demonstrations are learnable. `<<PMI>>` user-messages carry
  write acknowledgements (`{"ok":true,"written":[{"id":N,...}],"tick":T}`)
  and read results (`{"records":[...],"tick":T}`) — the model learns its
  record ids and the stand counter from these, exactly as on the stand.
* **assistant** = response text + (optionally) one JSON act block. Act
  call fields per SPEC record format: `act, content, source, layer,
  valid_time, record_tick, refs`; `read` carries `mode` (`last|ids`) and
  `count`/`ids` and deposits no record (hence no layer).
* Two-phase turns: when the model reads before answering, the example
  contains assistant(read) → user(`<<PMI>>` result) → assistant(answer).
  137 examples contain such a result turn.
* **Recovery examples** (5, one per biography; BENCH-2026-09-04 pattern D):
  empty context → `read last 12` → biography restore summary built only
  from the record store.

## Constitution compliance notes

* **P1/P2 (model is the only semantic subject).** All acts in the data are
  demonstrations of the model's own decisions; no external ranker, gate or
  trigger appears anywhere in the format. `<<PMI>>` blocks are responses to
  model-requested acts or executor physics acknowledgements — never
  unrequested injection.
* **P3 (layers are speeds).** `layer` is always set explicitly per act
  from the horizon semantics; there is no default layer anywhere in the
  pipeline. Validator rejects write acts without an allowed layer value.
* **P5 (acts of the model, logged).** Every record in the act stream
  corresponds to an explicit act call `name/repeat/connect/reconcile`
  (plus `read`); silence never writes.
* **P6 (ticks owned by the stand).** `record_tick` in demonstrations is
  the model's copy of the counter it sees in `<<PMI>>` acks (next = last
  +1); the system prompt states exactly that. The generator advances the
  counter +1 per executed write act, reads never advance it (validated:
  tick monotonicity).
* **P7 (provenance asserted by the model).** Act calls carry `source`
  (`user` for dialogue statements, `repeat`/`connect`/`reconcile` per SPEC
  conventions); nothing reclassifies content.
* **P8 (append-only).** The act stream is strictly append-only; supersession
  and corrections are new records with `refs`, the past is never rewritten.
* **P9 (training shapes capacity).** The ledger exists only as the
  generator's scoring oracle and a separate JSON file; it is never part of
  any example's context. Acts are demonstrations = capacity scaffolding
  (legal per P9); content of live biographies is out of scope of this
  dataset.
* **P10 (honest labeling).** This dataset trains acts for the target
  configuration; it does NOT demonstrate or claim: parametric substrate,
  live governance, hash-chained journal, a0 weighting.

## Validation (run at build time)

* every emitted line parses as JSON; every embedded act block parses;
* every `refs` entry points to a record id existing in the same
  biography's act stream (0 dangling);
* write acts always carry `layer` from the allowed set (0 missing);
* content traceability: every digit run in act content is derivable from
  the ledger / referenced records (0 violations);
* `valid_time ≤ record_time` per record; `record_tick` strictly
  increments per write act; `repeat`/`connect` always have non-empty refs;
* full regeneration from seed reproduces byte-identical files.

## Known gaps

1. **Split is per-example, not per-biography.** P9 asks governance to be
   demonstrated on held-out biographies; for a *training* corpus the
   mechanical 90/10 split was requested. For governance evaluation, retrain
   with biographies held out (e.g. train on bio-01..04, validate on bio-05;
   `emit_mlx.py` already tags every example with `bio_id`).
2. **Citations may exceed the 14-message window.** Answers cite exchange
   numbers learned earlier (they appear in the model's own connect records
   and read results, i.e. memory-mediated), but a narrow window alone does
   not contain them. This is intentional: it trains memory-mediated recall,
   but makes the cited number unrecoverable if the model failed to record
   it earlier.
3. **`reconcile` is minimally demonstrated** (10 calls). E1 declares it
   "available, not tested"; scenarios are clock-biography checks derived
   from the record store, not lived divergence episodes.
4. **Recovery-example weights are placeholders** (`weight: 1.0` in the
   `<<PMI>>` payload); real amplitude reading is not demonstrated there.
5. **Scripted assistant style.** Responses are templated; conversational
   variety of a live model is not represented. Paraphrase augmentation is
   future work.
6. **Russian-only dialogue.** The act grammar is language-agnostic, but all
   biographies are in Russian (owner's working language); cross-lingual
   transfer is untested.
7. **Universe is 5 domains × 1 script shape.** All biographies share the
   same event grammar (facts/positions/contradictions/repeats); more
   diverse shapes (multi-party, deadline drift, absence returns) are
   future work.
