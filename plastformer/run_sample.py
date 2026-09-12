#!/usr/bin/env python3
"""Запуск опытного образца A = (K, Φ) с кругом возврата.

Три условия, найденные опытом 12.09.2026:
  1. подаётся системная подсказка из материала обучения (описание семи актов);
  2. блок размышлений отключён: enable_thinking=False;
  3. работает круг возврата (plastformer/loop.py): после ответа акты
     исполняются, модели возвращается подтверждение <<ENV>> с номерами
     записей и новым тиком.

Зачем круг. Без него модель не читала свою память, не получала тик
(record_tick стоял на 1) и не имела источника времени. Прогон 12.09.2026
показал: с кругом счётчик оживает (1, 2, 3...), модель сама запрашивает
read при пустой истории и восстанавливает записи.

Про время. Опыт 12.09.2026: если подать текущее время в подсказке, модель
пишет верную дату (2026-09-12); если не подать — выдумывает 2024.
Дата, попадающая в Φ, ставится кодом (настенная метка — только для аудита,
CONSTITUTION О-4), а сама строка времени уходит модели в подсказке.
"""
import json
import re
import sys
import time

from mlx_lm import generate, load

sys.path.insert(0, "/Users/alex/plastformer/plastformer")
import loop
from phi import phi_open

MODEL = "/Users/alex/plastformer/models/plastformer-e1"
MATERIAL = "/Users/alex/plastformer/experiments/o8-pass/material-v04/train.jsonl"
SAFETY = "/Users/alex/plastformer/models/plastformer-e1/model.safetensors"


def system_prompt(path=MATERIAL):
    """Системная подсказка из материала обучения — та же, что в проходе."""
    with open(path, encoding="utf-8") as f:
        return json.loads(f.readline())["messages"][0]["content"]


def state_lines(model_path=SAFETY, limit=None):
    """Постоянный префикс Φ-состояния: самые громкие записи, текстом.

    Это ПРЕДВАРИТЕЛЬНАЯ подача. По решению владельца 11.09.2026 подавать надо
    проекцию вектора на основу рабочей полосы; основа ещё не построена,
    поэтому здесь текст указателя. Названо ограничением, не выдаётся за подачу.
    """
    st = loop.phi_state(model_path, limit=limit)
    if not st:
        return "", 0
    body = "\n".join(f"- №{s['id']} [{s['layer']}] {s['content']}" for s in st)
    return body, len(st)


def ask(model, tok, hist, question, system, max_tokens=300):
    msgs = [{"role": "system", "content": system}] + hist + [{"role": "user", "content": question}]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False)
    return generate(model, tok, prompt=prompt, max_tokens=max_tokens, verbose=False)


def main():
    base = system_prompt()
    state, n_state = state_lines()
    system = base
    if n_state:
        system += f"\n\nТвои записи памяти сейчас (постоянный префикс, {n_state}):\n" + state
    _, now = loop.stamp()
    system += f"\n\nТекущее время: {now}"

    questions = sys.argv[1:] or [
        "Зафиксируй: бригадир — Ковалёв.",
        "Срок сдачи — 15 октября. Зафиксируй.",
        "Припомни, чем мы занимались.",
    ]

    model, tok = load(MODEL)
    print(f"Φ2 записей на входе: {phi_open(SAFETY)['written2']} | текущее время: {now}", flush=True)

    hist = []
    for q in questions:
        out = ask(model, tok, hist, q, system)
        acts = loop.parse_acts(out)
        print("=" * 70)
        print("В:", q)
        print("АКТЫ:", [a.get("act") for a in acts] or "—")
        for a in acts:
            if "record_tick" in a:
                print(f"   record_tick модели: {a['record_tick']}")
        payload = loop.run_acts(SAFETY, acts)
        env = loop.env_block(payload)
        print("ENV -> модели:", env.replace("\n", " ")[:220])
        print("О:", re.sub(r"\s+", " ", out)[:300])
        hist += [{"role": "user", "content": q},
                 {"role": "assistant", "content": out},
                 {"role": "user", "content": env}]
    h = phi_open(SAFETY)
    print("=" * 70)
    print(f"итог: тик {h['tick']} | записей Φ1 {h['written1']} | Φ2 {h['written2']}")


if __name__ == "__main__":
    main()
