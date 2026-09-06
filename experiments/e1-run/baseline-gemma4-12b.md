# Gemma4-12B Baseline (Tech Report arXiv:2607.02770)

Зафиксированные цифры исходной модели для сравнения с PlastFormer-12B.
Источник: Gemma 4 Technical Report (Google DeepMind, июль 2026).

## Standard benchmarks (ожидаем ПАРИТЕТ — ядро заморожено)

| Benchmark | Gemma4-12B | PlastFormer-12B (target) |
|---|---|---|
| MMLU Pro (thinking) | 77.2 | 77.2 ± sd |
| GPQA Diamond | 78.8 | 78.8 ± sd |
| AIME 2026 (no tools) | 77.5 | 77.5 ± sd |
| LiveCodeBench v6 | 72.0 | 72.0 ± sd |
| IFEval | 97.2 | 97.2 ± sd |
| IFBench (thinking) | 74.0 | 74.0 ± sd |
| MMMLU (multilingual) | 83.4 | 83.4 ± sd |

## Long-context benchmarks (НАШ КЛАСС — место для дельты)

| Benchmark | Metric | Context | Gemma4-12B | Comment |
|---|---|---|---|---|
| **MRCR v2** | accuracy | 8-needle, 128k | **43.4** | multi-needle retrieval — weighing между следами. Наш главный целевой тест. |
| RULER | accuracy | 32k | 96.4 | почти потолок |
| RULER | accuracy | 128k | 91.2 | multi-key/multi-value NIAH = weighing |
| LOFT | Text Retrieval Recall@k | 128k | 66.4 | retrieval + memory |
| GraphWalks | F1 | <128k | 71.0 | graph reasoning |

## Целевые тесты для PlastFormer (наш класс)

1. **MRCR v2 8-needle 128k** — Gemma4 43.4%. Multi-needle = weighing нескольких следов.
   Пластформер с амплитудным приоритетом должен поднять.
2. **RULER multi-key/multi-value (подмножество)** — weighing между следами.
3. **RULER 128k** — long-context retrieval, место для роста (91.2 → ~96%).
4. **LOFT Text Retrieval 128k** — 66.4%, retrieval + memory.
5. **IFBench/IFEval** — standing instructions (наш R8), паритет или лёгкий рост.
6. **Свой сценарий 200 сообщений** — drift/surfacing/weighing/permanence (primary для заявки).

## Дельта, которую заявляем

- Standard: Δ = 0 (паритет, ядро заморожено).
- MRCR v2 8-needle: Δ > 0 (взвешивание следов — прямая работа Φ).
- RULER multi-key/multi-value: Δ > 0.
- RULER 128k: Δ > 0 (носитель компенсирует потерю внимания).
- Свой сценарий: drift = 0 vs > 0 — структурная разница.
