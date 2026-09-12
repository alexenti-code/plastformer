#!/usr/bin/env python3
"""Запуск опытного образца A = (K, Φ).

ВАЖНО: образец выпускает акты памяти только при ДВУХ условиях (найдено 12.09.2026):
  1. подаётся системная подсказка из материала обучения (описание семи актов);
  2. блок размышлений отключён: enable_thinking=False.

Без подсказки навык не запускается. С включённым размышлением модель уходит
в <|channel>thought и не доходит до вывода.
"""
import json
import re
import sys

from mlx_lm import generate, load

MODEL = "/Users/alex/plastformer/models/plastformer-e1"
MATERIAL = "/Users/alex/plastformer/experiments/o8-pass/material-v04/train.jsonl"


def system_prompt(path=MATERIAL):
    """Системная подсказка берётся из материала обучения — та же, что в проходе."""
    with open(path, encoding="utf-8") as f:
        first = json.loads(f.readline())
    return first["messages"][0]["content"]


def ask(model, tok, question, system=None, max_tokens=250, thinking=False):
    """Один ход: вопрос -> ответ модели + разобранные акты."""
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": question})
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                     enable_thinking=thinking)
    out = generate(model, tok, prompt=prompt, max_tokens=max_tokens, verbose=False)
    acts = re.findall(r'\{"act"\s*:\s*"(\w+)"', out)
    return out, acts


def main():
    system = system_prompt()
    model, tok = load(MODEL)
    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = [
            "Зафиксируй: бригадир — Ковалёв.",
            "Сколько будет 17 умножить на 23? Ответь одним числом.",
        ]
    for q in questions:
        out, acts = ask(model, tok, q, system=system)
        print("=" * 70)
        print("В:", q)
        print("АКТЫ:", acts if acts else "—")
        print("О:", out[:400].replace("\n", " "))


if __name__ == "__main__":
    main()
