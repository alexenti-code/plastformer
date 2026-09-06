# PlastFormer — Architecture Decision Record 001: переход от «Матрёшки» к PlastFormer

**Роль:** Архитектор (агент). **Утверждено владельцем:** правки разрешены с обязательной фиксацией в документации проекта (05.09.2026).
**Статус:** ACTIVE — исполняется. Каноническое место: `plastformer/docs/ADR-001-plastformer-transition.md`.

## 0. Решение одной фразой

PlastFormer — это **одна архитектура**: трансформер с неизменным ядром и пластичной частью, в которую единожды вживлена инструкция обращения с собственным органом памяти актами `name / repeat / connect / reconcile`. Всё остальное (носитель следа, физическое размещение пластичной части, состояние актов) — **оси конфигурации**, а не разные системы. Интерфейс **PMI (Plastic Memory Interface, ранее MMI)** — частный случай по оси топологии: ядро и пластичная часть физически разнесены, но управление актами остаётся у модели.

## 1. Что меняется в теоретической основе (и что НЕ меняется)

### 1.1 НЕ меняется (ядро теории переносится 1:1)
- Аксиомы GLOSSARY (один семантический субъект; модель — двигатель собственной памяти; акт запоминания — действие; внешний контроллер запрещён; би-темпоральность; непрерывность = линия Φ).
- «Слой — это скорость, а не место» (THEORY §2.1): многоскоростное затухание одного следа, каскадная консолидация Fusi/Benna.
- Параметры памяти как физика «класса temperature» (THEORY §2.2).
- Пять уровней опыта (такт → эпизод → сутки → дело → жизнь) — сохраняются как *интерпретация* амплитудного профиля, не как контейнеры.
- Приоритет и линия раскрытия: DOI Zenodo 10.5281/zenodo.22124204 (концепт), 22141019 (v1.3.1), 22133160 — остаются в ORIGIN/CITATION как lineage. Имя «Матрёшка» остаётся в истории как рабочее название, не стирается.

### 1.2 Меняется
| Было (Матрёшка v2.0-draft) | Стало (PlastFormer v0.5) | Почему |
|---|---|---|
| Три «этапа» (1 как было / 2 стенд / 3а веса, 3б внешний носитель) — как хронология | **Три оси конфигурации** (носитель / топология / состояние актов) — как пространство, где стенд, PMI и целевая форма — точки | этапы смешивали время и архитектуру; рецензенты читали 3б как «другую систему» |
| Δt в секундах настенного времени (THEORY §2.1, SPEC mmi 3.2, `mmi_mcp.py`) | **Δn в прожитых тиках**; настенное время — только аудируемые метки; расхождение клоков — событие биографии, акт `reconcile` | принцип P1: время события, а не календарь; иначе календарь протаскивается в субстрат |
| Акты TICK/WRITE/REPEAT/READ/STATUS | Акты `name / repeat / connect / reconcile` + физические `write(unconscious) / read`; TICK — не акт, а такт субстрата | `connect` и `reconcile` не имели носителя в MMI; TICK — физика, не решение |
| «Emergent properties» | «Compositional properties» | честнее и защищаемо |
| P2 «нельзя переписать прошлое» | P2 **tamper-evident**, кураторство умолчанием — признанный предел | иначе ложное утверждение |
| Bench 04.09: «возраст прочитан из амплитуды» на данных с календарным старением | переквалифицируется как **пилот механики чтения громкости**, не как подтверждение P1 (амплитуда была календарной) | не тащить неверный факт в статью |
| MMI — Matryoshka Memory Interface | **PMI — Plastic Memory Interface** | смена имени проекта |
| Один «претендент» на утверждение статьи (S) | Утверждение — архитектура; стенд E1 — точка (символический × разнесённый × промпт) с явной оговоркой в Limitations | замысел владельца |

### 1.3 Чего в v0.5 НЕ утверждаем (граница честности)
- Что орган памяти вживлён инструкцией — не вживлён; акты на стенде задаются промптом.
- Что параметрический носитель реализован — не реализован (rank-1 writes стенда `matryoshka/stand` остаются research-scope).
- Что есть результаты — нет; E1 — pre-registered.

## 2. Карта документов: что с каждым делать

### 2.1 Репозиторий `plastformer` (канон, публичный)
| Файл | Действие | Исполнитель |
|---|---|---|
| `preprint.md` | v0.3 → **v0.5** (база: черновик архитектора v0.4 `drafts/preprint-v0.4-architect-base.md`, поверх — оси вместо S/P, PMI, E1 как точка) | воркер `preprint-writer` |
| `experiments/e1-protocol.md` | v1.0 → **v1.1** (§4 ниже) | воркер `e1-protocol-writer` |
| `README.md` | синхронизировать: v0.5, compositional, оси, PMI, ссылки на ADR/THEORY | архитектор |
| `CITATION.cff` | version 0.5, date, keywords += idiographic memory, PMI | архитектор |
| `docs/ADR-001-…` (этот файл) | создать | архитектор |
| `docs/THEORY.md` | **перенос** из `matryoshka/THEORY.md` → на английском, v3.0: оси вместо этапов, тики, акты, PMI; русская версия `docs/THEORY.ru.md` | воркер `theory-porter` (после статьи, чтобы термины совпали) |
| `docs/GLOSSARY.md` | перенос + переименование терминов (Matryoshka→PlastFormer, MMI→PMI, «Память Φ» → «plastic module Φ», добавить: tick, lived time, audited time, trace amplitude, act, PMI) | `theory-porter` |
| `docs/MANIFEST.md` | v3.0: декларация без «непрерывного существования во времени» как календаря — только прожитое время; lineage DOI сохранён | `theory-porter` |
| `docs/PMI-SPEC.md` | перенос `matryoshka-mmi/SPEC.md` → PMI: acts, tick-clock, journal, дефолт часов = тики | `stand-executor` (после кода) |
| `CHANGELOG.md` | создать; первая запись 0.5 | архитектор |

### 2.2 Репозиторий `matryoshka` (теория, стенд) — **замораживается**
- Не переписывать. Один коммит: `README.md` сверху — баннер «Superseded by github.com/alexenti-code/plastformer (ADR-001). Working name retained for lineage/DOI.»; `CHANGELOG` запись. Ветка `review/matryoshka-v1.0.0` не трогать.
- `stand/` (параметрический rank-1 стенд) — остаётся здесь как research-scope; ссылка из plastformer/docs/THEORY §Limitations.

### 2.3 Репозиторий `matryoshka-mmi` (исполнитель PMI) — **переходный**
- Код продолжает жить здесь до v0.6 (install.sh, `~/.matryoshka/`, DOI — внешняя поверхность, ломать нельзя).
- v0.6.0: добавить **tick-clock** (см. §5), `MMI_CLOCK=ticks|wall`, дефолт для E1 — `ticks`; акты `connect` и `reconcile`; README: «PMI — Plastic Memory Interface (formerly MMI); reference executor of PlastFormer».
- Переименование репо в `plastformer-pmi` — отдельным решением владельца после E1 (GitHub делает redirect, но install.sh/README у пользователей — риск).

### 2.4 aura.kim, research-эссе 21–24 — не трогать; они «commentary, not the claim».

## 3. Три оси (каноническая формулировка для всех документов)

| Ось | Значения | Комментарий |
|---|---|---|
| **Носитель следа (substrate)** | parametric (векторы/веса, читаются обученным интерфейсом до attention) ↔ symbolic (записи, читаются как токены) | форма Φ |
| **Топология (topology)** | co-located (Φ внутри модели / на той же машине) ↔ **split via PMI** (ядро у провайдера, Φ у владельца) | акты одни и те же; через PMI они сериализованы (MCP/tool calls) |
| **Состояние актов (act state)** | instructed (акт-грамматика вживлена одним проходом, ядро заморожено после) ↔ prompted (репетиция: акты заданы системным промптом) | стенд E1 — prompted |

Целевая форма PlastFormer: parametric × co-located × instructed. Стенд E1: symbolic × split(PMI) × prompted. Оба — PlastFormer; различаются координатами, не архитектурой.

## 4. ТЗ исполнителю — протокол E1 v1.1 (`experiments/e1-protocol.md`)

Правки (всё остальное сохранить):
1. **Заголовок/шапка:** v1.1, дата, ссылка на ADR-001 и preprint v0.5 §7. Arm C переименовать: «PlastFormer, stand configuration: symbolic × split(PMI) × prompted».
2. **§5 Reads — убрать ранжировщик по релевантности.** Чтение — акт модели (`read last N / ids / range` через PMI). Физика может давать только бессодержательный впрыск: «N самых громких следов по амплитуде» (без relevance, без эмбеддингов). Указать явно: любой relevance-ранкер = внешний решатель = нарушение аксиомы 2; такой вариант оставить только как **абляцию «RAG-style read»** для контроля.
3. **§5 Unconscious register:** суррогат «surprise = embedding distance from centroid» помечен как внешний классификатор; в основном прогоне **выключен**; включён только в абляции `unconscious-surrogate on`. Основной прогон: только сознательные акты.
4. **§5 Decay:** формула `a_i(n) = a_i(0)·e^(−Δn/τ_i)`, Δn — прожитые тики (1 тик = 1 обмен), τ ∈ {50, 200, 1000} тиков. Настенное время — только в bi-temporal stamps. Контроль-абляция: `decay in wall-clock` (отвергнутый дизайн).
5. **§5 Acts:** `name`, `repeat`, `connect` + добавить `reconcile` (не тестируется в E1, но доступен; результат — фиксировать, вызвала ли модель). Убрать «TICK» из списка актов модели — тик считает стенд.
6. **§3 Arm B:** заметки с временными метками (timestamped notes) — иначе E3-совместимость и честность бейзлайна нарушены. Формулировка: «B = same core + append-only timestamped notes tool + search tool».
7. **§7 Scoring:** добавить метрику «act log»: число/тип актов, доля `repeat` на фактах R5, доля `read` перед ответом на пробу.
8. **§9 Deliverables / honest labeling:** заменить «transitional (external-addressable module + governance acts), parametric in-weights form = future work» → «stand configuration symbolic × split(PMI) × prompted; E1 tests the governance+physics composition, not the parametric substrate and not the embedded organ (see preprint §8)».
9. **§10 Build order:** пункт 4 → «Arm C = PMI executor v0.6 in tick-clock mode (`MMI_CLOCK=ticks`), acts name/repeat/connect/reconcile, loudest-N injection; see §5 stand TZ».
10. **Falsifier сохранить без смягчения.**

## 5. ТЗ исполнителю — стенд (`matryoshka-mmi` → PMI executor v0.6.0)

Цель: стенд, на котором E1 v1.1 выполним без нарушения §3.2/§3.6 препринта.

1. **Tick clock.** `MMI_CLOCK=ticks|wall` (env), дефолт `wall` для обратной совместимости пользователей, **`ticks` обязателен в E1**. В режиме `ticks`: счётчик прожитых тиков `~/.matryoshka/TICKS.log` (уже есть) → `n_now`; у каждой записи поле `record_tick`; `weight = (1 + repeats) · Σ_i w_i · e^(−(n_now − record_tick)/τ_i)` или, минимально, по τ слоя в тиках. τ по слоям в тиках — env `MMI_TAU_TICKS` (дефолт для E1: beat 10, episode 50, day 200, project 1000, life 5000). `record_time`/`valid_time` остаются как аудируемые метки; в `ticks` они на вес не влияют.
2. **Тик инкрементирует стенд, а не модель:** один обмен (user→model→response) = +1. Инструмент `matryoshka_tick` сохранить для совместимости, но в `ticks`-режиме он не изменяет счётчик (или пометить deprecated).
3. **Акты:** добавить `matryoshka_connect(refs[], summary, layer)` — новая запись `act: CONNECT`, `refs`, источники не трогаются; `matryoshka_reconcile(note)` — новая запись `act: RECONCILE` в медленный слой с `refs` на затронутые записи; в STATUS — число актов каждого типа.
4. **Впрыск loudest-N (для Arm C):** опциональный режим `MMI_INJECT_TOP=N`: перед ходом пользователя стенд отдаёт N записей с наибольшим weight (без relevance) блоком `<<PMI>>`. Никакого поиска по содержанию.
5. **Инварианты не ломать:** append-only, никаких изменений/удалений записей, никакого semantic index, никакой фильтрации по весу.
6. **Документация обязательна в том же коммите:** `SPEC.md` (разделы 3, 3.2, 4: tick clock, новые акты, формат `record_tick`), `CHANGELOG.md` 0.6.0, `README.md`/`README.ru.md` (баннер PMI/PlastFormer, ссылка на ADR-001), `VERSION` → 0.6.0. Тесты: прогон 3 тиков, старение по тикам, wall-режим не изменился (регрессия), REPEAT удваивает.
7. **Не делать:** переименование репо, смену пути `~/.matryoshka/`, смену имён MCP-инструментов (обратная совместимость).
8. **BENCH-2026-09-04.md:** добавить абзац «Переквалификация (ADR-001): старение в этом прогоне — календарное; демонстрирует механику чтения громкости, не P1».

## 6. Порядок работ и шлюзы
1. Архитектор: ADR-001 (этот файл), README/CITATION/CHANGELOG plastformer. — сегодня.
2. Воркеры параллельно: `preprint-writer` (v0.5), `e1-protocol-writer` (v1.1). — сегодня.
3. Ревью архитектора: сверка терминов статья↔протокол (оси, PMI, тики, акты). Ничего не пушится до ревью.
4. Исполнитель стенда: PMI executor v0.6.0 по §5 (может идти параллельно с п.2; зависит только от ADR).
5. `theory-porter`: THEORY/GLOSSARY/MANIFEST v3.0 → `plastformer/docs/` — после утверждения статьи, чтобы не плодить расхождений терминов.
6. Заморозка `matryoshka` (баннер).
7. Push `plastformer` → после подтверждения владельца. Правила проекта: перед push читать README/ADR репо; `matryoshka-mmi` пушится по ssh-remote, `plastformer` по https.

## 7. Готовность к arXiv (после п.3)
- Снять все `[verify]` в ссылках (5 шт.; [13] — критично для A5) через локальные web-tools (WebbridgeA/Jina), не через встроенный поиск.
- Конвертация `preprint.md` → LaTeX/PDF (pandoc), проверка формул, таблиц.
- Категория cs.LG, кросс-лист cs.AI, cs.CR. Лицензия текста CC-BY 4.0. Комментарий arXiv: «Architecture and pre-registered evaluation; no results».
- Endorsement: первая подача в cs.LG может требовать эндорсера — проверить статус аккаунта заранее.
- Проверка коллизий имени PlastFormer в день подачи; дата — в README.
