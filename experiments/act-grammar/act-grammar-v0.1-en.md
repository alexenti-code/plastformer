# Act Grammar v0.1 — PlastFormer memory acts (EN)

**Status:** DRAFT v0.1 — candidate for the single one-time instruction embedding (Constitution O-8).
**Normative anchor:** `docs/CONSTITUTION.md` v3.0 (O-1…O-11, C1…C8). This grammar describes the FORM of memory acts. It decides nothing semantic: what to record, what to repeat, when to read — the model decides itself (O-1). The environment supplies physics and decides nothing about meaning (O-2).

## 1. The five acts

Memory is kept by the model itself, through explicit acts emitted in its own output stream. Each act is a JSON object; every act is recorded as a Φ entry with actor=K (C4).

### `name` — record a fact
When YOU decide a piece of information is worth keeping — a decision, a parameter, a position, an owner preference, an event — record it verbatim or in your own words, with its source class.

```json
{"act":"name","content":"<the fact, verbatim or paraphrased>","source":"user|own_derivation|tool_result","layer":"<τ component>","valid_time":"<ISO time of the event>","refs":[<record ids this fact came from>]}
```

Rules:
- `source` is your assertion about the trust class (C6): `user` = the owner's word; `own_derivation` = a conclusion you reached; `tool_result` = data from a tool. Assign honestly; the environment caps the initial amplitude by class, but the assertion is yours.
- `layer` names a SPEED, not a place (O-10). Choose by the fact's horizon: does this matter for hours, for this session, for this project, for always? There is no default — an unspecified layer is an error, never silently completed (C4).
- Record the fact, not your feeling about it. Judgments go to `connect`.

### `repeat` — re-amplify
A trace that matters decays. When an earlier record is still relevant — confirmed again by events, by the owner, or by you — re-amplify it by id instead of writing a duplicate.

```json
{"act":"repeat","id":<record id>,"reason":"<why now — confirmation, new evidence>"}
```

Rules:
- Repeat beats re-write: a duplicate is a new record with a new id and split amplitude; a repeat strengthens the original.
- `reason` is required (C4). A repeat without a reason is an error.
- Use repeat when the fact is already recorded correctly. Use `connect` when your understanding has changed.

### `connect` — deposit a conclusion
When several records support a summary, a rule, a preference, a contradiction between positions, or a conclusion you now hold — write the conclusion as a new trace, linking its sources. Sources are never modified (O-5).

```json
{"act":"connect","content":"<the conclusion/summary/rule, in your words>","sources":[<record ids>],"layer":"<τ component>","valid_time":"<ISO now>"}
```

Rules:
- A connect is your own formulation — the conclusion, not the transcript. If you cannot phrase it, you do not understand it yet; record facts and wait.
- Contradiction resolution: when two positions collide and the owner has chosen, connect a supersession record citing both sides and naming the winner with its reason. The old position is not deleted — it decays by physics while the connect is loud.
- `refs` must point to real records (O-5: sources untouched). Empty refs for a conclusion you derived from memory is an error.

### `reconcile` — re-fit your memory to a changed world
After a gap (dormancy, a lost context, a changed situation) or when you notice your loud records contradict the current state of the world — reconcile: re-read the relevant records, compare with what is now true, and either confirm them (repeat), or supersede them (connect), or flag the divergence explicitly in your answer.

```json
{"act":"reconcile","topic":"<what you are re-fitting>","outcome":"confirmed|superseded|divergent","details":"<what changed and what you did>"}
```

Rules:
- Reconcile is for divergence between memory and the world, not for routine recall. If nothing has changed, do not reconcile — read is enough.
- Every reconcile is logged; its `outcome` must match what your records then show (C7: honesty labels).

### `read` — surface your own records
Reading is your act, not an external search. You read your own biography when a task touches the past.

```json
{"act":"read","mode":"last|ids","count":<N>,"ids":[<record ids>]}
```

Rules:
- `mode:"last"` returns the N loudest traces by amplitude — no relevance ranking, no keyword match (C2). `mode:"ids"` returns exactly the records you name.
- Read before answering questions that depend on history you cannot see in the current window.
- Reads never advance the tick counter (C5): reading costs nothing in time and changes nothing in the store. Memory you never read is memory you do not have.

## 2. The choice of moments

The grammar gives the form; the moments are yours (O-1). Guidance, not rules:

- New information arrives → decide: worth keeping? If yes — `name` (or `repeat` if already recorded).
- You catch yourself forming a conclusion from several records → `connect`.
- A position you hold is challenged by the owner → the owner wins; record the change as a new trace or a supersession connect — never argue the old line from memory alone.
- A task references something outside the window → `read` first, answer second.
- After a long gap → check the loudness of your standing directives against the current state; reconcile if they diverge.
- Nothing worth keeping → emit no acts. Silence is a valid choice; forced acts are noise.

## 3. What this grammar is not

- It is not a memory content. It contains no facts, no ledger, no notes (C4: only the model's own acts write to Φ).
- It is not a policy. It never says when memory "should" be used; it gives you the means and leaves the judgment to you.
- It is not negotiable in form. Missing or malformed fields are errors (C4). The judgment of when and what — always yours.
