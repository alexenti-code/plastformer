# Changelog

**Status:** CHANGELOG — история изменений; не норма.

## [split-removed] — 2026-09-10

### Removed (ТЗ «ликвидация следов разделённой архитектуры», приказ владельца)

**Старая раздельная архитектура удалена; она не является объектом дальнейшей разработки.** Итоговая форма изделия — один MLX 4-bit файл весов A = (K, Φ): секция K (неизменное ядро с вшитой Инструкцией) + секция Φ (пластичные записи того же экземпляра). Φ1/Φ2 — два происхождения записей внутри одного Φ, не отдельные хранилища. Вне файла нет состояния экземпляра.

- **Код раздельной памяти удалён целиком:** `experiments/phi-vector/` — `bank.py`, `read_iface.py`, `write_iface.py`, `train_read.py`, `run_vector.py`, `smoke_pr0.py`, `tests_test_bank.py`, `read_proj.npz`, `section-phi/`, `read-corpus/`, кэши; `experiments/calibration/` (CAL-1, стендовая физика); `experiments/e1-run/` (стендовый генератор корпуса).
- **Старый цикл o8-pass удалён:** `plastformer_run.py`, `battery.py`, `gen_anchor.py`, `mix_material.py`, `anchor.jsonl`, `phi_state.json`, `grammar*.jsonl`, `lora_v02.yaml`, `lora_v03.yaml`, `lora_alpha.yaml`, `adapters_v02/`, `adapters_v03/`, `adapters_alpha/` (включая не отслеживавшиеся git-ом каталоги и `phi_state.json`).
- **Слитая бракованная сборка удалена:** `models/plastformer-a1-ollama/`, `models/Modelfile-a1`.
- **Сохранено как сборочный материал (не часть изделия):** материал прохода Инструкции (`experiments/o8-pass/material*/`), генератор материала (`gen_material.py`), базовый чекпойнт ядра (`gemma4-12b-text-4bit/`), Инструкция v0.2.0 (`experiments/act-grammar/`), датасеты (`organ-dataset/`, `project-dataset/`).
- **e1-protocol.md → SUPERSEDED:** описывает распорядок эпохи разделения (wrapper-arms); добавлен §5.1 «регистрируемый объект — единый файл A=(K,Φ)»; никаких суррогатных конфигураций. Будет пересобран под A=(K,Φ).
- **preprint.md → SUPERSEDED:** описывает рамку эпохи разделения; будет переписан под A=(K,Φ).
- **DESIGN-PARAMETRIC-PHI.md → SUPERSEDED:** дизайн раздельного trace-банка; активная сборочная архитектура — `docs/ARCHITECTURE-FIXED-BRAIN-v1.md`.
- **run-manifest-template.md → SUPERSEDED** до пересборки под A=(K,Φ).
- **ADR-001 → LINEAGE-ONLY** (переход от «Матрёшки»; split topology PMI/MMI и стенд выведены из архитектуры), **ADR-003 → LINEAGE-ONLY** (история нумерации Конституции + соглашения эпохи разделения), **RESEARCH-LOG → LINEAGE-ONLY** (дневник эпохи разделения); все три выведены из read order в AGENTS.md.
- **AGENTS.md v3:** целевая форма — один файл A=(K,Φ); единственный источник норм — Конституция; запрет возвращать раздельную схему; правило «отдельные файлы Φ — удаляемое наследие, не чинить»; ближайшая работа — сборка единого файла; новый read order без наследия эпохи разделения.
- **README.md:** описывает только единый артефакт A=(K,Φ).
- **TECHNICAL-STATE.md** (корень + копия в `experiments/phi-vector/`): карта «удалено / сохранено как сборочный материал / единственный объект работы»; советы «чинить» старый код исключены.
- **INSTRUCTION-PACKAGE.md:** пакет переведён в статус сборочного материала; §1 (банк/интерфейсы) переписан — физика Φ это будущая секция Φ единого файла; §4 (сборка изделия) — единый файл A=(K,Φ); упоминания банка/проектора/стенда убраны.
- **GLOSSARY/MANIFEST/THEORY/THEORY.ru/act-grammar/organ-dataset:** локальные правки — «wrapper», «обвязка», «trained projector», «PMI/MMI-маркеры», «стенд» заменены нейтральными формулировками либо снабжены пометками RETIRED/LINEAGE; `<<PMI>>` → `<<ENV>>` в коде и текстах.

## [disinfection] — 2026-09-10

### Changed (ТЗ «полная дезинфекция документов», приказ владельца)
- **AGENTS.md** v2: добавлены §1.1 (изделие — один файл весов K+Φ) и §1.2 (запрещённый словарь для всех агентов); §2–§4 вычищены — стенд/PMI/D-stand/trained удалены как живые сущности; ось — instructed; ссылка на e1-protocol — «версия в шапке файла».
- **experiments/phi-vector/TECHNICAL-STATE.md** v2: статус ACTIVE (карта состояния); «LoRA-адаптер» → «Инструкция» с пометкой «временная форма до слияния»; строка a0 переписана с контекстом инцидента (изъятие ≠ запрет слияния); «символический суррогат a0» изъят из карты; §5 (правила) перенесён в AGENTS.md, оставлено решение владельца о запрете разнесённой формы.
- **README.md**: таблица «Three configuration axes» удалена — одна конфигурация (parametric × co-located × instructed); PMI — строкой LINEAGE; E1-версия — «по шапке файла».
- **docs/MANIFEST.md** v4.1: PMI из шапки и research questions переведён в lineage-примечания; honest boundary переписан по факту 09.09 (банк/интерфейсы/грамматика v0.2.0 построены; разрывы A/B и единый файл — нет).
- **docs/THEORY.md** v4.1 / **docs/THEORY.ru.md**: §4 background tick помечен DEFERRED (Fork 8); §9 переписан — построено/непостроено, регистры Φ1/Φ2 по ADR-005; «LoRA» убрано.
- **docs/GLOSSARY.md** v4.1: акты — восемь (добавлены calibrate, scan, ратифицированы 09.09); sense definition переформулирован без «split»; добавлены RETIRED-записи: adapter/base+adapter, harness, PMI/MMI, stand, trained.
- **experiments/run-manifest-template.md**: grammar v0.2.0; «LoRA rank» → «pass parameters»; упоминание hash-chained journal снято (ADR-004).
- **experiments/calibration/protocol.md** v0.2: статус — частично ратифицирован (§8.2 ратифицирован 09.09); «harness-side» → «evaluator-side»; runner помечен инструментарием.
- **docs/ADR-001**: статус COMPLETED (LINEAGE-история); §3/§5 помечены как координаты/ТЗ своего времени (split(PMI)/стенд выведены).
- **docs/ACT-GRAMMAR-v02.md**: статус SUPERSEDED → experiments/act-grammar (v0.2.0, утверждена владельцем 09.09).
- **docs/DESIGN-PARAMETRIC-PHI.md** v4.1: §7 модуль 5 переименован — «run harness (development instrumentation, NOT part of the artifact)»; grammar v0.2.0.
- **drafts/**: всем шести файлам проставлены шапки SUPERSEDED/LINEAGE-ONLY.
- Не тронуты (проверено чистыми): docs/CONSTITUTION.md, docs/CONSTITUTION.ru.md, docs/ADR-004, docs/ADR-005, preprint.md (исторические секции Changes — по правилу «история не трогается»).
- Примечание к сборке (ТЗ §6): фиксированная ёмкость Φ отменена — объём Φ1/Φ2 не лимитируется, ограничитель — затухание; Φ-регион файла переменной длины (ADR-005); синхронизировано в docs/ARCHITECTURE-FIXED-BRAIN-v1.md §2.
- Шапки статуса проставлены всем .md (включая CHANGELOG, ADR-003/004, preprint, README датасетов, служебные файлы грамматики, models/*/README).
- e1-protocol.md: заголовок исправлен на фактическую v1.7 (в теле были Changes до v1.7 при шапке v1.5).
- В e1-protocol.md и preprint.md перед блоками «Changes since…» добавлено примечание: история, упоминания стенда/PMI — не живые сущности.
- docs/RESEARCH-LOG-2026-09.md, docs/ADR-002: шапки LINEAGE/ACTIVE с пометками об исторических упоминаниях.
- INSTRUCTION-PACKAGE.md, calibration/README.md: «LoRA-проход» → «инструктивный проход», harness → инструментарий; шапки уточнены.

## [0.6] — 2026-09-06

### Changed
- `docs/CONSTITUTION.md` / `docs/CONSTITUTION.ru.md` → **v3.0, NORMATIVE (owner edition 2026-09-06)**: postulates-first structure — ontology intro, Foundations O-1–O-11, compliance tests C1–C8, lineage appendix. Copy-as-branch wording replaced by plain duplication; the memory-keeping skill is set in one pass (no retraining framing); layers-as-speeds and the weight formula promoted to Foundations; no negative argumentation.
- `experiments/e1-protocol.md` v1.2 → **v1.4**: single registered comparison per owner directive — **B vs D**, one wrapper agent shared by both arms (B = wrapper + transformer, D = wrapper + PlastFormer); the variable is the model only. **Arms A and C (plain chat) removed**: "bare window vs PlastFormer" cannot separate this architecture from any notebook, so it is not registered. PR1–PR2 withdrawn (numbers not reused); PR3–PR4, PR8–PR9 bound to B/D; PR5–PR7 (Addendum A) rebound to D vs D-stand; former ablation arm C-stand renamed **D-stand**. Context budget 32768 tokens.
- `preprint.md` v0.5 → **v0.6**: status restated as an **architectural proposal** (abstract, §7, §9) — no empirical claim; E1 aligned to protocol v1.4; the stand is an ablation of arm D; Limitations extended (null-recall risk named in advance; no security improvement claimed). `README.md` and `CITATION.cff` synced to v0.6.
- `preprint.md` §7 Evaluation: E1 references updated to the protocol (v1.3 → v1.5) and the current scheme.
- E1 v1.5 (owner directive: target the class of behavior): corpus split into memory layer (R1–R6) and reasoning-conflict layer (**R7–R10** — directive vs accumulated experience, habit vs fresh instruction, own conclusion vs owner's word, goal substitution at distance); conflict probes (P-weigh, P-surface, P-commit) added; scoring split into primary (drift, surfacing, weighing, permanence) and secondary (recall — near-parity expected) metrics; PR10 added; §1 Goal rewritten around the behavioral class.
- Preprint §1: new subsection "What the internal memory department changes for an agent" — the cost of remembering, the window left to the task, pre-interpreted storage, instance continuity; the external-memory tax named explicitly.
- **Detached from the transitional executor** (`matryoshka-mmi`, retired): the plastic store, tick counter, and physics live inside the unified PlastFormer artifact; E1 §5 rewritten without any external executor; the repository itself carries a RETIRED banner (historical only).
- Cross-document renumbering to CONSTITUTION v3.0 (P1–P10 → O-1–O-11 / C1–C8): `docs/THEORY.md`, `docs/THEORY.ru.md`, `docs/MANIFEST.md`, `docs/GLOSSARY.md`, `AGENTS.md`, `experiments/organ-dataset/README.md`, `experiments/e1-protocol.md`. Mapping recorded in ADR-002.
- `docs/ADR-003-constitution-v2.md`: approval status updated (v3.0 supersedes the v2.x numbering).
- Wording: "falsifier"/"falsifiable" replaced by "refutation criterion"/"refutable" across active documents (owner directive 2026-09-06).
- Earlier in 0.6: erasure = deletion of the Φ section (core survives), crypto-erasure demoted to an optional protection; journal excluded from the architecture (ADR-004); tamper-evidence claims withdrawn; derived-traces topic removed (one plastic section = one subject); security scope withdrawn (threat model §5, P3, E2).

## [0.5] — 2026-09-05

### Changed
- `preprint.md` v0.3 → v0.5. One architecture, three configuration axes (substrate / topology / act training) replace the "S/P realizations" framing. PMI (Plastic Memory Interface, formerly MMI) defined as the split-topology special case (§3.9). Δn in lived ticks; two clocks and `reconcile` (§4); "compositional" replaces "emergent"; P2 restated as tamper-evident; P3 in lived ticks; Related Work extended (MemoryBank, A-MEM, HippoRAG, Metis, Memory-as-Ontology, Nested Learning, sleep-time compute); E3b and E6 added; unverified references flagged `[verify]`.
- `experiments/e1-protocol.md` v1.0 → v1.1. Arm C labelled as stand configuration (symbolic × split(PMI) × prompted); relevance-ranked read removed from the main run (kept as ablation); embedding-surprise surrogate off in the main run; decay in ticks; `reconcile` act added; Arm B gets timestamped notes; act-log metrics.
- `README.md`, `CITATION.cff` synchronized.

### Added
- `docs/ADR-001-plastformer-transition.md` — decision record for the transition from the working name "Matryoshka": what in the theory is kept, what changes, document map, work orders for the E1 protocol and the PMI executor v0.6.
- `drafts/` — preserved v0.3 preprint, v0.4 architect base, v1.0 E1 protocol.

## [0.3] — 2026-09-04
- Initial preprint v0.3 and E1 protocol v1.0.
