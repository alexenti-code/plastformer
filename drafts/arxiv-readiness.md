# arXiv readiness — PlastFormer preprint v0.5 (05.09.2026, worker arxiv-prep)

## Verification table (method: arXiv API over HTTPS curl; web-tools runner search; jneurosci.org links)

| # | Claim in draft | Result | Action |
|---|---|---|---|
| [1] Titans 2501.00663 | Behrouz et al., 2025 | CONFIRMED (title/authors match) | none |
| [2] MemGPT 2310.08560 | Packer et al., 2023 | CONFIRMED | none |
| [3] Zep | was bare "Zep AI, 2025" | CONFIRMED as arXiv:2501.13956 (Rasmussen et al., publ. 2026-01) | entry now carries authors + ID |
| [4] Mem0 2504.19413 | Chhikara et al., 2025 | CONFIRMED | none |
| [5] RAG NeurIPS 2020 | Lewis et al. | accepted as clean (not re-checked, canonical) | none |
| [6] Generative Agents UIST 2023 | Park et al. | accepted as clean | none |
| [7] MemOS 2507.03724 | MemTensor org label | CONFIRMED ID/title (Li et al.); org attribution kept | none |
| [8] AgentPoison NeurIPS 2024 | Chen, Z. et al. | accepted as clean (not a suspect) | none |
| [9] 2601.05504 | was "Dong et al. MINJA…" | ID REAL but authors/title were wrong: actual "Devarangadi Sunil et al., Memory Poisoning Attack and Defense on Memory Based LLM-Agents" (MINJA-robustness study in EHR agents, publ. 2026-01-09) | FIXED, flag dropped |
| [10] 2512.16962 | subtitle "…Memory Consolidation" | ID REAL, subtitle wrong: actual "…via Poisoned Experience Retrieval" (Srivastava & He, publ. 2025-12-18) | FIXED, flag dropped |
| [11] Fusi 2005, [12] Benna 2016 | canonical neuro | accepted as clean | none |
| [13] postmortem | was "internal cybersecurity evaluation" | LOCATED as the Aug-2026 Hugging Face incident: OpenAI postmortem + METR 2026-08-26 investigation + Redwood investigation | entry REWRITTEN to real documents, flag dropped; A5 anchor kept |
| [14] MRL NeurIPS 2022 | Kusupati et al. | accepted as clean | none |
| [15] Matryoshka Diffusion 2310.15111 | Gu et al., 2023 | CONFIRMED via API | none |
| [16] µKE | was bare, no ID | CONFIRMED as arXiv:2504.01196 (Su et al., publ. 2025-04-01; COLM 2025 per authors' repo) | FIXED, flag dropped |
| [17] Tsao Nature 2018 | accepted as clean | none |
| [18] Howard/Shankar | vague citation | CONFIRMED JNeurosci 34(13):4692 (Howard et al. 2014); exact full citation written (pp. 4692–4707; Shankar & Howard Neural Comp 24(1):134–193, 2012) | FIXED, flag dropped |
| [20] PoisonedRAG 2024 | Zou et al. | accepted as clean (not a suspect) | none |
| [21] 2604.00010 | was "Tan, Tan, Soatto" | ID REAL but authors/title wrong: actual "Garikaparthi, A., Can LLMs Perceive Time? An Empirical Investigation" (publ. 2026-03-09) | FIXED, flag dropped |
| [22] 2510.23853 | was "TicToc-v1…" | ID REAL, title wrong: actual "Cheng et al., Your LLM Agents are Temporally Blind…" (TicToc dataset inside; publ. 2025-10-27); venue = arXiv only | FIXED, flag dropped |
| [23] LongMemEval 2410.10813 | Wu et al., ICLR 2025 | ID CONFIRMED via API; venue taken on trust | none |
| [24] LoCoMo ACL 2024 | Maharana et al. | accepted as clean | none |
| [25] MemoryBank 2305.10250 | Zhong et al., AAAI 2024 | ID CONFIRMED via API | none |
| [26] A-MEM 2502.12110 | Xu et al., 2025 | CONFIRMED via API | none |
| [27] 2504.13171 | sleep-time compute | CONFIRMED (Lin et al., Letta, publ. 2025-04-17) | author expanded, flag dropped |
| [28] HippoRAG 2405.14831 | Gutiérrez et al., NeurIPS 2024 | ID CONFIRMED via API | none |
| [29] 2607.26760 | was "MemTensor. Metis: A…" | ID REAL: actual "Zhang et al., Metis: Memory Foundation Model" (no "A"; publ. 2026-07-29) | FIXED, flag dropped |
| [30] 2603.04740 | Memory as Ontology | CONFIRMED title match (Li, Z., publ. 2026-03-05) | author added, flag dropped |
| [31] Nested Learning | was "(HOPE), NeurIPS 2025" + flag | CONFIRMED: Behrouz et al., arXiv:2512.24695 (publ. 2025-12-31); arXiv comment states NeurIPS 2025 publication | ID added, "(HOPE)" dropped (unexplained acronym), flag dropped |

Remaining `[verify]` count in preprint.md: **0**.

## Blockers / notes for architect
- [13] now cites real Aug-2026 incident reports (OpenAI/METR/Redwood). If the architect wants URLs in arXiv comments, add them at submit time.
- [18] page ranges (4692–4707; 134–193) are standard citations, cross-checked against jneurosci.org vol/issue/article only.
- [8] AgentPoison author line ("Chen, Z. et al.") and [20] PoisonedRAG were NOT re-verified (not suspects); spot-check before submit if time permits.
- In-text §5 A2 still attributes MINJA success-rate claims to [9]; [9] is a robustness study *of* MINJA, so the sentence reads correctly but leans on a secondary source. Consider citing the original MINJA paper directly in a later pass (no hallucinated citation added).

## Build
- `pandoc 3.10.1` present. `drafts/preprint-v0.5.tex` built (exit 0, ~44 KB).
- Checks: decay formula `a_i(n)=…` survived as display math; τ-symbols intact; 2 md tables → longtables; 11 `##` → 11 subsections; references block present; stale "(with verification flags)" heading removed and tex rebuilt.
- No LaTeX engine on this machine (`pdflatex/xelatex/lualatex/tectonic/latexmk` all absent) → **no PDF built**. Build PDF on a machine with TeX Live or via arXiv's own pipeline.

## Owner-side checklist (pre-submit)
- [ ] Endorser status for cs.LG first submission (required for new arxiv authors in cs.*).
- [ ] Name-collision check date: confirm "PlastFormer" has no arXiv/citation collision on submit day.
- [ ] License: CC-BY (text) + Apache 2.0 (code) as stated in Availability.
- [ ] arXiv comment text: "Architecture and pre-registered evaluation; no results".
- [ ] Categories: cs.LG + cs.AI + cs.CR.
