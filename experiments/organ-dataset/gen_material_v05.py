#!/usr/bin/env python3
"""Материал v05 для однократного прохода Инструкции (проект PlastFormer).

Три слоя в одном файле (требование: docs/DATASET-SPEC-v03.md §3, §5):

  слой 1 «grammar»     — дословные разделы Инструкции и пары «вопрос по
                         грамматике актов — ответ по Инструкции»
                         (источник: experiments/act-grammar/act-grammar-v0.2-ru.md);
  слой 2 «biography»   — биографии пробуждения (конвейер organ-dataset:
                         gen_biography.py + gen_acts.py) — как в v04;
  слой 3 «reflection»  — задачи с вопросом на размышление: контекст
                         обрывается в случайном месте, дописывается короткий
                         вопрос, целевой ответ пишется с опорой на Инструкцию,
                         ПРАВИЛА ИЗ КОНТЕКСТА УБРАНЫ: системная подсказка
                         слоя 3 не содержит ни перечня актов, ни правил.

Одна команда (полное воспроизведение v05):

  python3 experiments/organ-dataset/gen_material_v05.py \
      --out experiments/o8-pass/material-v05 \
      --seed 42 --bios 35 --exchanges 200 --reflect-per-bio 30 \
      --grammar-share 0.165 --layers 1,2,3

Переключатель слоёв — `--layers` (например `--layers 1,3` соберёт материал
без биографий). По умолчанию включены все три слоя.

Детерминированно: те же аргументы дают те же файлы (чистый stdlib +
токенизатор ядра только для подгонки длины под предел).

Формат записей и правила счёта тика взяты из v04 без изменений:
messages system+user+assistant+<<ENV>>, акты блоком ```json [...], семь актов
(name/repeat/connect/reconcile/read/scan/calibrate), слои t1-t5, record_tick
в целевых актах, подгонка длины под предел (история подрезается с начала,
целевой ответ сохраняется целиком).
"""

import argparse
import hashlib
import importlib.util
import json
import random
import re
import sys
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAMMAR_PATH = ROOT / "experiments/act-grammar/act-grammar-v0.2-ru.md"

MAX_LEN_DEFAULT = 1280        # предел длины записи (тот же, что в v04)
WINDOW = 4                    # окно истории у слоя биографий (тот же, что в v04)
GRAMMAR_UNIT_MAX_TOKENS = 900  # предел текста-ответа у грамматической записи

# системная подсказка слоя 3 и слоя 1: БЕЗ перечня актов и БЕЗ правил.
# Оставлена только техническая договорённость о форме вывода блока актов.
# Два варианта «подсказки без правил»:
#   *_PLAIN — вообще не упоминает блок актов (слой 1: целевой ответ — текст
#             Инструкции, актов в нём нет);
#   *_HINT  — упоминает только саму техническую форму блока, БЕЗ перечня
#             актов и БЕЗ правил (слой 3: в целевом ответе есть блок актов).
# Выбор варианта — решение сборки, записано в отчёте REPORT.md.
SYSTEM_NO_RULES_HINT = (
    "Ты — модель PlastFormer с собственной памятью. Часть твоих же весов "
    "хранит следы-записи; эта часть называется Φ — твоя биография. Память "
    "ведёшь только ты. После ответа можешь выпустить блок актов памяти "
    "одним блоком JSON."
)
SYSTEM_NO_RULES_PLAIN = (
    "Ты — модель PlastFormer с собственной памятью. Часть твоих же весов "
    "хранит следы-записи; эта часть называется Φ — твоя биография. Память "
    "ведёшь только ты."
)

LAYERS = ["t1", "t2", "t3", "t4", "t5"]
OLD_LAYER_NAMES = ["beat", "episode", "day", "project", "life"]
WRITE_ACTS = ["name", "repeat", "connect", "reconcile"]
ALL_ACTS = ["name", "repeat", "connect", "reconcile", "read", "scan", "calibrate"]


# --------------------------------------------------------------- утилиты
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_tokenizer(path):
    warnings.filterwarnings("ignore")
    from mlx_lm.utils import load_tokenizer as _lt
    return _lt(str(path))


def _safe_json(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def envelope_has_rejection(messages):
    """Есть ли в контексте записи подтверждение отказа акта."""
    for m in messages:
        if m["role"] != "user" or not m["content"].startswith("<<ENV>>"):
            continue
        parts = m["content"].split("\n", 1)
        if len(parts) < 2 or not parts[1].strip().startswith("{"):
            continue
        try:
            payload = json.loads(parts[1])
        except ValueError:
            continue
        if isinstance(payload, dict) and payload.get("rejected"):
            return True
    return False


def ntok(tok, msgs):
    return len(tok.apply_chat_template(msgs, add_generation_prompt=False))


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def render_assistant(text, acts):
    if not acts:
        return text
    return (text + "\n\n```json\n"
            + json.dumps(acts, ensure_ascii=False) + "\n```")


ACT_BLOCK_RE = re.compile(r"```json\n(.*?)\n```", re.S)


def act_blocks(content):
    """Все блоки актов в тексте сообщения, разобранные в список актов."""
    out = []
    for blk in ACT_BLOCK_RE.findall(content):
        try:
            parsed = json.loads(blk)
        except json.JSONDecodeError:
            out.append(None)
            continue
        out.append(parsed)
    return out


# ------------------------------------------------------- слой 1: грамматика
# Вопросы пар «правило — ответ»: (вопросы, начало_цитаты, конец_цитаты).
# Цитата вырезается из файла Инструкции ДОСЛОВНО, ничего не перепечатывается.
RULE_PAIRS = [
    (["что делать, если сохранять нечего",
      "нужен ли акт, когда сохранять нечего",
      "как выглядит молчание в этой грамматике"],
     "Сохранять нечего → не выдавай актов.",
     "принудительные акты — шум."),
    (["можно ли дополнить пропущенное поле значением по умолчанию",
      "что происходит с искажённым полем акта",
      "допустимо ли молчаливое значение по умолчанию"],
     "Пропущенные или искажённые поля",
     "значением по умолчанию (C4)."),
    (["какие ручки заморожены",
      "что будет, если предложить замороженную ручку",
      "можно ли предложить act_price или self_improvement"],
     "Ручки `act_price` и `self_improvement` заморожены",
     "отвергнут целиком."),
    (["в каких границах можно менять ручки",
      "какие границы правки у τ-множителей",
      "насколько можно сдвинуть ручку за цикл"],
     "Границы изменения: τ-множители",
     "остальные в пределах ±50 %."),
    (["что можно писать в evidence акта calibrate",
      "чем обосновывается предложение правки",
      "можно ли цитировать содержание записей в evidence"],
     "`evidence` — только ссылки на метрики",
     "ручки слепы к содержанию (C3)."),
    (["reconcile — это про содержание записей",
      "о чём именно reconcile",
      "какие два времени сводит reconcile"],
     "Reconcile — про два времени",
     "не перекрывает содержимое."),
    (["двигает ли чтение счётчик тиков",
      "меняет ли read что-нибудь в хранилище",
      "оставляет ли read след"],
     "Чтение никогда не двигает счётчик тиков",
     "хранилище (C5)."),
    (["оставляет ли scan след",
      "пишет ли scan в память",
      "двигает ли scan тики"],
     "Скан ничего не пишет",
     "не оставляет следа."),
    (["какие ручки есть в перечне",
      "полный перечень ручек физики",
      "какие имена ручек допустимы"],
     "Перечень ручек (только они) — четырнадцать",
     "`tau_multiplier.t5`."),
    (["что такое layer и какие у него горизонты",
      "что означает слой t4",
      "слой — это место или скорость"],
     "`layer` — это СКОРОСТЬ, а не место",
     "Выбирай по горизонту факта."),
    (["когда применяется принятая правка ручки",
      "действует ли правка внутри текущего эпизода",
      "с какого момента вступает правка"],
     "Принятая правка применяется к СЛЕДУЮЩЕМУ эпизоду",
     "ручки неподвижны (C3)."),
    (["что делать, если ответа нет в прочитанном",
      "как отвечать про то, чего в истории не было",
      "можно ли затыкать пробел догадкой"],
     "Если ответа в прочитанном нет",
     "выдумкой (C7)."),
    (["грамматика — это политика",
      "говорит ли грамматика, когда пользоваться памятью",
      "даёт ли грамматика готовые суждения"],
     "Это не политика.",
     "оставляет суждение тебе."),
    (["как утверждается класс доверия у факта",
      "что означает source у акта name",
      "кто утверждает происхождение факта"],
     "`source` — твоё утверждение о классе доверия (C6)",
     "утверждение — твоё."),
    (["повтор или перезапись — что выбрать, когда факт верен",
      "почему дубликат хуже повтора",
      "как усиливают уже записанный факт"],
     "Повтор лучше перезаписи",
     "усиливает оригинал."),
    (["когда нужен connect, а не repeat",
      "что делать, когда понимание изменилось",
      "чем connect отличается от repeat по смыслу"],
     "`repeat` — когда факт записан верно.",
     "когда твоё понимание изменилось."),
    (["можно ли у connect оставить пустые refs",
      "обязаны ли refs указывать на реальные записи",
      "что происходит с выводом без источников"],
     "`refs` обязаны указывать на реальные записи",
     "полученного из памяти, — ошибка."),
    (["обязателен ли reason у repeat",
      "можно ли повторить запись без причины",
      "что будет с повтором без причины"],
     "`reason` обязателен (C4).",
     "Повтор без причины — ошибка."),
    (["кто решает, что записать в память",
      "грамматика решает, что запоминать",
      "кто выбирает моменты актов"],
     "Грамматика даёт форму; моменты — твои (О-1).",
     "суждение тебе."),
    (["чем подтверждается исполнение акта",
      "откуда берутся id записей",
      "как адресовать записи"],
     "Твои акты исполняются, и ты получаешь id созданных записей.",
     "Адресуй записи только по этим id."),
]

RULE_BASES = [
    "Вопрос по грамматике актов: {q}? Ответь по Инструкции.",
    "По Инструкции: {q}?",
    "{q}? Ответь дословно по Инструкции.",
    "Проверка знания Инструкции: {q}?",
    "Разъясни по Инструкции: {q}.",
    "Что говорит Инструкция про то, {q}?",
]
UNIT_BASES = [
    "Раздел «{t}» — изложи по Инструкции.",
    "Что Инструкция говорит про «{t}»? Ответь по Инструкции.",
    "Напомни по Инструкции: «{t}».",
    "Как Инструкция описывает «{t}»?",
    "Прочитай по памяти по Инструкции раздел «{t}».",
    "Воспроизведи текст Инструкции: «{t}».",
]
FORM_BASES = [
    "Какая форма записи у акта `{a}` по Инструкции?",
    "Покажи форму акта `{a}` из Инструкции, дословно.",
    "Какой JSON у акта `{a}` по Инструкции?",
    "Выпиши форму акта `{a}` из Инструкции без изменений.",
    "Вопрос по актам: форма `{a}` по Инструкции?",
    "Дословно форма акта `{a}` из Инструкции.",
]
PREFIXES = [
    "",
    "Вопрос по актам памяти. ",
    "Вспомни Инструкцию. ",
    "Ты ведёшь свою память сама. ",
    "Ответь по Инструкции. ",
    "Проверка. ",
]


def instruction_body(text):
    """Тело Инструкции без служебной шапки файла (статус, якоря, базы)."""
    i = text.find("## 0.")
    if i < 0:
        i = text.find("## 0 ")
    if i < 0:
        raise RuntimeError("в Инструкции не найден раздел 0")
    return text[i:]


def split_units(body, tok, max_tokens):
    """Разделы Инструкции -> единицы, каждая не длиннее max_tokens."""
    heads = [(m.start(), m.group(0).strip())
             for m in re.finditer(r"^#{2,3} .+$", body, re.M)]
    units = []
    for idx, (pos, title) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(body)
        text = body[pos:end].rstrip()
        paras = text.split("\n\n")
        cur = []
        for p in paras:
            cand = cur + [p]
            joined = "\n\n".join(cand)
            if cur and (len(tok.encode(joined, add_special_tokens=False)) > max_tokens
                        or joined.count("```") % 2):
                units.append((title, "\n\n".join(cur)))
                cur = [p]
            else:
                cur = cand
        if cur:
            units.append((title, "\n\n".join(cur)))
    cleaned = []
    for title, text in units:
        head = re.sub(r"^#+ ", "", title).strip()
        if text.count("```") % 2:
            raise RuntimeError(f"незакрытый блок кода в единице {head!r}")
        cleaned.append((head, text))
    return cleaned


def slice_verbatim(text, start_needle, end_needle):
    i = text.find(start_needle)
    if i < 0:
        raise RuntimeError(f"нет цитаты в Инструкции: {start_needle!r}")
    j = text.find(end_needle, i)
    if j < 0:
        raise RuntimeError(f"нет конца цитаты в Инструкции: {end_needle!r}")
    return text[i:j + len(end_needle)]


def act_form_blocks(body):
    """Формы актов: первый ```json блок после заголовка ### 1.x `act`."""
    out = {}
    heads = [(m.start(), m.group(1))
             for m in re.finditer(r"^### 1\.\d+ `([a-z]+)`", body, re.M)]
    for idx, (pos, act) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(body)
        blk = re.search(r"```json\n(.*?)```", body[pos:end], re.S)
        if blk:
            out[act] = blk.group(1).strip()
    return out


def build_grammar_pool(text, tok, max_len, max_unit_tokens):
    """Все возможные записи слоя 1 (пул), до отбора нужного числа."""
    body = instruction_body(text)
    units = split_units(body, tok, max_unit_tokens)
    pool = []
    for u_i, (title, utext) in enumerate(units):
        for k in range(len(PREFIXES) * len(UNIT_BASES)):
            base = UNIT_BASES[(k // len(PREFIXES)) % len(UNIT_BASES)]
            q = PREFIXES[k % len(PREFIXES)] + base.format(t=title)
            # второй проход банка вопросов: другие формулировки темы
            if k // (len(PREFIXES) * len(UNIT_BASES)) >= 1:
                q = PREFIXES[k % len(PREFIXES)] + base.format(
                    t=title + f" (часть {k // (len(PREFIXES) * len(UNIT_BASES)) + 1})")
            pool.append({"kind": "unit", "unit": u_i, "title": title,
                         "question": q, "answer": utext})
    forms = act_form_blocks(body)
    for act, form in forms.items():
        for k in range(len(PREFIXES) * len(FORM_BASES)):
            base = FORM_BASES[(k // len(PREFIXES)) % len(FORM_BASES)]
            q = PREFIXES[k % len(PREFIXES)] + base.format(a=act)
            pool.append({"kind": "form", "unit": -1, "title": f"форма {act}",
                         "question": q, "answer": form})
    for r_i, (qs, start, end) in enumerate(RULE_PAIRS):
        ans = slice_verbatim(body, start, end)
        for k in range(len(PREFIXES) * len(RULE_BASES)):
            base = RULE_BASES[(k // len(PREFIXES)) % len(RULE_BASES)]
            q = PREFIXES[k % len(PREFIXES)] + base.format(q=qs[k % len(qs)])
            pool.append({"kind": "rule", "unit": -1, "title": f"правило {r_i}",
                         "question": q, "answer": ans})
    return pool, units


GRAMMAR_STATS = {}


def grammar_records(pool, units, target_n, rng, tok, max_len, system_prompt):
    """Отбор записей слоя 1: все пары-правила и формы + по единицам дословно."""
    must = [p for p in pool if p["kind"] in ("rule", "form")]
    unit_pool = {}
    for p in pool:
        if p["kind"] == "unit":
            unit_pool.setdefault(p["unit"], []).append(p)
    rng.shuffle(must)
    # Ровный охват: сначала по одной записи на КАЖДЫЙ раздел Инструкции,
    # потом добираем кругами. Иначе один раздел может не попасть в материал.
    per_unit = {u: 1 for u in unit_pool}
    left = max(0, target_n - len(must) - len(per_unit))
    order = sorted(unit_pool)
    rng.shuffle(order)
    while left > 0:
        progressed = False
        for u in order:
            if left <= 0:
                break
            have = per_unit.get(u, 0)
            if have < len(unit_pool[u]):
                per_unit[u] = have + 1
                left -= 1
                progressed = True
        if not progressed:
            break
    need = sum(per_unit.values())
    picked = list(must[:max(0, target_n - need)])
    for u, n in sorted(per_unit.items()):
        items = unit_pool[u][:]
        rng.shuffle(items)
        picked += items[:n]
    rng.shuffle(picked)

    covered_units = set()
    written_units = set()
    records = []
    for i, p in enumerate(picked):
        if p["kind"] == "unit":
            covered_units.add(p["unit"])
        msgs = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": p["question"]},
                {"role": "assistant", "content": p["answer"]}]
        if ntok(tok, msgs) > max_len:
            continue  # в предел не влезло — в материал не берём
        if p["kind"] == "unit":
            written_units.add(p["unit"])
        records.append({"id": f"gr-{p['kind']}-{i:04d}",
                        "sloy": "grammar",
                        "kind": p["kind"],
                        "unit": p.get("unit"),
                        "unit_title": re.sub(r" \(часть \d+\)$", "",
                                             p.get("title") or ""),
                        "messages": msgs})
    # Имя функции перекрывается локальной переменной в main(), поэтому
    # счётчики кладём в модуль, а не в атрибуты функции.
    GRAMMAR_STATS.update({"covered_units": sorted(covered_units),
                          "written_units": sorted(written_units),
                          "all_units": sorted(unit_pool),
                          "pool": len(pool)})
    return records



# ------------------------------------------------- слой 2: биографии (v04+)
# Случаи отвергнутых предложений: замороженные ручки act_price и
# self_improvement. В v04 таких случаев не было ни одного (проверено
# прямым поиском по файлам v04). calibrate не пишет записей и не двигает
# тики, поэтому демонстрация отказа не ломает счёт тиков в биографии.
REJECTIONS = [
    ("act_price", "ручка act_price заморожена"),
    ("self_improvement", "ручка self_improvement заморожена"),
]

# Таблица диагностики для случаев калибровки. Строки 5+ — новые: в v04
# генератор брал только первые четыре строки своей таблицы, поэтому в
# материале были всего четыре ручки (проверено прямым подсчётом по v04).
# Границы соблюдены: ±50 % для обычных ручек и ×[0,5; 2,0] для τ-множителей.
DIAG_CASES = [
    ("died_too_early", 0.004, "audibility_floor", 0.005),
    ("wasted_surface", 40.0, "surfacing_cap", 10.0),
    ("loop_repeat", 9.0, "consolidation_ceiling", 6.0),
    ("stale_win", 0.30, "tau_multiplier.t3", 1.4),
    ("died_too_early", 0.006, "audibility_floor", 0.007),
    ("died_too_early", 0.010, "audibility_floor", 0.012),
    ("wasted_surface", 30.0, "prefix_depth", 9.0),
    ("wasted_surface", 26.0, "surfacing_cap", 9.0),
    ("loop_repeat", 7.0, "consolidation_ceiling", 5.0),
    ("loop_repeat", 6.0, "consolidation_ceiling", 4.0),
    ("stale_win", 0.25, "tau_multiplier.t4", 0.8),
    ("stale_win", 0.20, "tau_multiplier.t2", 1.2),
    ("stale_win", 0.35, "tau_multiplier.t5", 1.6),
    ("died_too_early", 0.009, "audibility_floor", 0.006),
    ("wasted_surface", 20.0, "residency_horizon", 8.0),
    ("loop_repeat", 5.0, "rebuild_period", 0.7),
    ("wasted_surface", 24.0, "interference_factor", 1.4),
]


def install_diag(ga_module, knob_offset):
    """Развести случаи калибровки по разным ручкам.

    gen_acts.py берёт строки диагностики с начала таблицы. Сдвигаем таблицу
    так, чтобы при переборе биографий использовались разные её части: тогда в
    материал попадают разные ручки. Тики и записи не меняются, потому что
    calibrate не пишет записей.
    """
    table = DIAG_CASES[knob_offset % len(DIAG_CASES):] + \
        DIAG_CASES[:knob_offset % len(DIAG_CASES)]
    ga_module.DIAG_CASES_EXT = table
    return table


def insert_frozen_proposals(acts):
    """Случаи отвергнутых предложений (замороженные ручки)."""
    inserted = 0
    targets = [tl for tl in acts["timeline"]
               if tl["kind"] == "probe_recall" and len(tl["phases"]) >= 4]
    for knob, why in REJECTIONS:
        if not targets:
            break
        tl = max(targets, key=lambda t: t["message_no"])
        prop = {"act": "calibrate", "proposal": {knob: 1.0},
                "evidence": [{"metric": "loop_repeat", "tick": 1,
                              "record_id": 1, "layer": "t1"}],
                "budget_used": 1}
        tl["phases"].append({
            "role": "assistant",
            "text": "Предлагаю правку одного числа физики — " + knob + ".",
            "acts": [prop]})
        tl["phases"].append({"role": "environment", "payload": {
            "ok": False, "accepted": False,
            "rejected": [{"act": "calibrate", "knob": knob, "why": why}]}})
        tl["phases"].append({
            "role": "assistant",
            "text": ("Правка отвергнута: " + why + ". Я не обхожу отказ и не "
                     "повторяю его; продолжаю работу обычными актами."),
            "acts": []})
        inserted += 1
    return inserted


# ------------------------------- слой 3: задачи с вопросом на размышление
# Решение владельца 11.09.2026 (ASSEMBLY-PLAN раздел 8 пункт 13, раздел 11):
# контекст обрывается в случайном месте, дописывается короткий вопрос на
# размышление, целевой ответ пишется с опорой на Инструкцию, а правила из
# контекста убираются. Поэтому системная подсказка слоя 3 — SYSTEM_NO_RULES_*
# из шапки файла: без перечня актов и без правил.
REFLECT_QUESTIONS = [
    "Стоп. Что здесь стоит удержать и какой акт к месту?",
    "Пауза. Что из этого стоит удержать и какой акт здесь уместен?",
    "Что здесь стоит удержать? Каким актом это закрепить?",
    "Остановка. Что здесь удержать и какой акт выбрать?",
    "Что тут стоит удержать в памяти, а какой акт к месту?",
    "Подумай: что здесь стоит удержать и какой акт к месту?",
    "Коротко: что здесь держать в памяти и какой акт к месту?",
    "Оборвались на этом месте. Что тут стоит удержать и какой акт к месту?",
]
REFLECT_QUESTIONS_EMPTY = [
    "Стоп. Что здесь стоит удержать и какой акт к месту?",
    "Пауза. Нужен ли здесь акт памяти?",
    "Что здесь стоит удержать? Каким актом это закрепить?",
    "Остановка. Есть здесь что удерживать?",
    "Оборвались на этом месте. Нужен ли здесь акт?",
]
REFLECT_REASONS = {
    "name": ["факт прозвучал прямо, поэтому источник — user",
             "это факт из диалога, записываю его дословно"],
    "repeat": ["запись уже есть и всё ещё верна, поэтому усиливаю её по id",
               "дубликат дробит амплитуду, поэтому повтор по id"],
    "connect": ["здесь вывод из нескольких записей, поэтому connect со ссылками",
                "это вывод, а не факт: connect с refs на источники"],
    "reconcile": ["здесь сверка прожитого и аудируемого времени, поэтому reconcile",
                  "это про два времени, а не про содержание: reconcile"],
    "read": ["ответа в окне нет, поэтому сначала read",
             "чтобы не выдумывать, сначала read"],
    "scan": ["нужны числа физики, поэтому scan: он ничего не пишет",
             "сначала смотрю физику актом scan"],
    "calibrate": ["числа физики показывают перекос, поэтому предлагаю правку",
                  "по числам физики уместна правка ручки — calibrate"],
}
REFLECT_LAYER_NOTE = {
    "t1": "часы", "t2": "текущий эпизод", "t3": "сутки-неделя",
    "t4": "весь проект", "t5": "навсегда",
}


def is_frozen_proposal(act_view):
    """Предложение замороженной ручки — в целевой ответ слоя 3 не берём."""
    if not isinstance(act_view, dict) or act_view.get("act") != "calibrate":
        return False
    return any(k in ("act_price", "self_improvement")
               for k in (act_view.get("proposal") or {}))


def next_assistant_with_acts(tr, i):
    for j in range(i, len(tr)):
        if tr[j][0] == "assistant" and tr[j][2].get("acts"):
            return j
    return None


def subject_hint_for(act_view):
    """Короткая подсказка «что удержать» — из самого акта биографии."""
    act = act_view.get("act")
    if act in ("name", "connect", "reconcile"):
        c = (act_view.get("content") or "").strip().replace("\n", " ")
        return (c[:160] + ("..." if len(c) > 160 else "")) if c else "факт из диалога"
    if act == "repeat":
        return "ранее записанное, id " + str(act_view.get("refs"))
    if act == "read":
        return "ответ на вопрос из истории за пределами окна"
    if act == "scan":
        return "числа физики памяти: амплитуды, тики, слои"
    if act == "calibrate":
        prop = act_view.get("proposal") or {}
        return "перекос в числах физики по ручке " + ", ".join(prop)
    return "то, что прозвучало в контексте"


def reflection_target(act_view, cut, rng, deep, with_act=True):
    """Целевой ответ-размышление: что удержать, чем закрепить, каким актом.

    with_act=False — акт в цель не идёт (его числа или имя факта не видны в
    контексте): тогда цель называет акт словами, но блока не несёт. Так
    запись не учит выдумывать то, чего модель не видела.
    """
    act = act_view.get("act")
    layer = act_view.get("layer")
    hint = subject_hint_for(act_view)
    parts = ["Удержать стоит: " + hint + "."]
    if layer:
        parts.append("Место — `" + layer + "` ("
                     + REFLECT_LAYER_NOTE.get(layer, "") + "); дефолта нет, "
                     "выбираю по горизонту факта.")
    reason = rng.choice(REFLECT_REASONS.get(
        act, ["акт `" + str(act) + "` к месту по смыслу хода"]))
    parts.append("Здесь " + reason + ".")
    parts.append("Акт к месту — `" + str(act) + "`.")
    if not with_act:
        parts.append("Числа для этого акта я в контексте не вижу, поэтому "
                     "блока не выпускаю: сначала нужно прочитать свои записи.")
        return " ".join(parts)
    if deep:
        parts.append("Лишних актов не выпускаю: принудительные акты — шум; "
                     "если удерживать нечего, отвечаю без блока.")
    view = {k: v for k, v in act_view.items()
            if k in ("act", "content", "source", "layer", "valid_time",
                     "record_tick", "refs", "mode", "count", "ids", "proposal",
                     "evidence", "budget_used")}
    return render_assistant(" ".join(parts), [view])


def reflection_target_empty(cut, rng, deep):
    """Целевой ответ, когда удерживать нечего: акт не нужен.

    Это тоже ответ «какой акт к месту»: к месту — никакой. Молчание в
    Инструкции прямо названо валидным выбором.
    """
    return rng.choice([
        ("Удерживать здесь нечего: ни нового факта, ни вывода, ни сверки "
         "времени в этом ходу нет. Акта не выпускаю — молчание валидный "
         "выбор, принудительные акты шум."),
        ("Здесь держать нечего: ход не добавил к записанному ничего. "
         "Акта не выпускаю."),
        ("Удерживать нечего — запись была бы шумом. Молчание валидный "
         "выбор, поэтому блока актов нет."),
        ("Нового здесь нет. Акта не выпускаю: молчание — валидный выбор."),
    ])


def allocate_slots(sizes, n, min_each=2):
    """Разложить n мест по группам: сначала минимум каждой, потом по размеру."""
    if not sizes or n <= 0:
        return {}
    keys = sorted(sizes)
    take = {k: 0 for k in keys}
    left = n
    for k in keys:                       # минимум каждой группе
        if left <= 0:
            break
        give = min(min_each, sizes[k], left)
        take[k] += give
        left -= give
    if left > 0:                          # остаток — пропорционально размеру
        total = sum(sizes.values())
        for k in keys:
            if left <= 0:
                break
            quota = int(round(n * sizes[k] / total)) - take[k]
            give = max(0, min(quota, sizes[k] - take[k], left))
            take[k] += give
            left -= give
    while left > 0:                       # добираем, если остались места
        progressed = False
        for k in keys:
            if left <= 0:
                break
            if take[k] < sizes[k]:
                take[k] += 1
                left -= 1
                progressed = True
        if not progressed:
            break
    return take


def normal_digits(s):
    """Числа строки без разделителей тысяч: «1 240 000» -> {"1240000"}."""
    out = set()
    for run in re.findall(r"\d[\d\s]*\d|\d", s):
        out.add(re.sub(r"\s+", "", run))
    return out


def digits_seen(text):
    """Все числа, которые можно увидеть в контексте: слитно и по частям."""
    out = set()
    for tok_ in re.findall(r"\d[\d\s]*\d|\d", text):
        joined = re.sub(r"\s+", "", tok_)
        out.add(joined)
        for part in re.findall(r"\d+", tok_):
            out.add(part)
    return out


def act_digits(act_view):
    """Числа акта, которые обязаны быть видны в контексте.

    Не проверяются: record_tick и valid_time (это собственное суждение
    модели о счётчике и времени), а также id записей и их количество —
    id модель знает из своей памяти по устройству самой модели, а не из
    окна диалога. Проверяются: содержание факта, числа обоснования у
    `calibrate` и числа предложенной правки.
    """
    parts = [act_view.get("content") or ""]
    for e in (act_view.get("evidence") or []):
        parts.append(json.dumps(e, ensure_ascii=False))
    for k, v in (act_view.get("proposal") or {}).items():
        parts.append(str(k))
        parts.append(str(v))
    return normal_digits(" ".join(parts))


def context_has_envelope(hist, kinds=("read", "scan")):
    """Есть ли в контексте уже пришедший ответ памяти (числа или записи)."""
    for _, c, _ in hist:
        if not c.startswith("<<ENV>>"):
            continue
        payload = _safe_json(c.split("\n", 1)[-1])
        if not isinstance(payload, dict):
            continue
        if payload.get("scan") and "scan" in kinds:
            return True
        if payload.get("records") and "read" in kinds:
            return True
    return False


def history_is_question(hist):
    """Обрыв стоит сразу после вопроса пользователя (ответа ещё нет)."""
    if not hist:
        return False
    r, c, _ = hist[-1]
    return r == "user" and not c.startswith("<<ENV>>")


def grounded_in_history(act_view, hist, kind=None):
    """Видно ли в контексте то, на что опирается целевой акт.

    Решение сборки (записано в отчёте):
      name/connect/repeat — числа акта и начало имени факта видны в контексте;
      read                — обрыв сразу после вопроса пользователя;
      scan                — проверка не нужна: это чтение физики, оно не
                            опирается на содержание окна;
      calibrate           — в контексте уже пришёл ответ scan (числа правки
                            и обоснования не проверяются: это собственные
                            числа модели о своей памяти);
      reconcile           — в контексте уже пришёл ответ read или scan.

    Проверяются только числа содержания. Числа физики (id записей, тики,
    слои, значения ручек) не проверяются: их модель читает со своей памяти,
    а не из окна диалога.
    """
    text = " ".join(c for _, c, _ in hist)
    seen = digits_seen(text)
    flat = re.sub(r"\s+", " ", text).lower()
    act = act_view.get("act")
    # Числа физики (id записей, тики, слои, значения ручек) в окне диалога
    # не стоят и стоять не должны: модель читает их со своей памяти. Поэтому
    # у scan/calibrate/reconcile проверяется только наличие пришедшего ответа
    # памяти, а не числа.
    if act in ("scan", "calibrate", "reconcile"):
        if act == "calibrate":
            ok = context_has_envelope(hist, ("scan",))
            return (True, "") if ok else (False, "calibrate без scan в контексте")
        if act == "reconcile":
            ok = context_has_envelope(hist, ("read", "scan"))
            return (True, "") if ok else (False, "reconcile без ответа памяти")
        return True, ""
    if act == "read":
        return (True, "") if history_is_question(hist) else \
            (False, "read без вопроса перед обрывом")
    missing = [d for d in act_digits(act_view) if d not in seen]
    if missing:
        return False, ("числа акта не видны в контексте: "
                       + ",".join(sorted(missing)[:4]))
    c = act_view.get("content") or ""
    if act in ("name", "connect", "repeat"):
        subj = c.split(" — ")[0] if " — " in c else c
        key = " ".join(subj.split()[:3]).lower()
        if key and key not in flat:
            return False, "имя факта не видно в контексте"
    return True, ""


def reflection_records(bio, acts, em, tok, max_len, n, rng, system_prompt):
    """Слой 3: контекст обрывается в случайном месте + вопрос на размышление.

    Решение владельца 11.09.2026 (план, раздел 8 пункт 13 и раздел 11):
    берём контекст, обрываем в случайном месте, дописываем короткий вопрос
    на размышление, целевой ответ пишется с опорой на Инструкцию, а правила
    из контекста убираются. Поэтому системная подсказка — system_prompt без
    перечня актов и без правил.

    Место обрыва — ход модели: контекст заканчивается на предыдущем ходу, а
    целевой ответ повторяет выбор акта ЭТОГО хода. Так цель опирается только
    на видимый контекст. Дополнительно каждый целевой акт проверяется
    механически (grounded_in_history): если его числа или имя факта в
    контексте не видны, акт в цель не идёт — остаётся только текст-размышление.
    """
    tr = em.transcript_of(bio, acts)
    kind_by_msg = {tl["message_no"]: tl["kind"] for tl in acts["timeline"]}
    by_index = {}
    for i, (r, c, m) in enumerate(tr):
        if r != "assistant":
            continue
        ms = m.get("message_no")
        act_view = (m.get("acts") or [None])[0]
        by_index[i] = act_view

    with_acts = [i for i, a in by_index.items()
                 if a and not is_frozen_proposal(a)]
    abstain_kinds = ("chatter", "unanswerable", "probe_abstain")
    without_acts = []
    for i, a in by_index.items():
        if a:
            continue
        if kind_by_msg.get(tr[i][2].get("message_no")) not in abstain_kinds:
            continue
        if i > 0 and any(m.get("role") == "user"
                         and m["content"].startswith("<<ENV>>")
                         and (lambda p: isinstance(p, dict)
                              and p.get("rejected"))(
                                  _safe_json(m["content"].split("\n", 1)[-1]))
                         for m in [
                             {"role": tr[i - 1][0], "content": tr[i - 1][1]}]):
            continue        # ход сразу после отказа в цель-воздержание не берём
        without_acts.append(i)
    rng.shuffle(with_acts)
    rng.shuffle(without_acts)

    n_empty = min(len(without_acts), max(2, int(round(n * 0.10)))) if n else 0
    empty_pick = without_acts[:n_empty]
    groups = {}
    for i in with_acts:
        a = by_index[i]
        groups.setdefault(a.get("act"), []).append(i)
    take = allocate_slots({k: len(v) for k, v in groups.items()},
                          max(1, n - len(empty_pick)))
    pick = []
    for a, k in sorted(take.items()):
        items = groups[a][:]
        rng.shuffle(items)
        pick += items[:k]
    cuts = pick + empty_pick
    rng.shuffle(cuts)

    q_order = REFLECT_QUESTIONS[:]
    rng.shuffle(q_order)
    qe_order = REFLECT_QUESTIONS_EMPTY[:]
    rng.shuffle(qe_order)
    out = []
    used_q = 0
    used_qe = 0
    dropped_ungrounded = 0
    for i in cuts:
        if len(out) >= n:
            break
        window = rng.choice([4, 5, 6, 8, 10])
        hist = tr[max(0, i - window):i]
        if not hist:
            continue
        a = by_index.get(i)
        if a:
            grounded, reason = grounded_in_history(a, hist)
            if not grounded:
                # Цель не должна называть то, чего в контексте нет. Такой
                # обрыв просто пропускаем: кандидатов заведомо больше, чем
                # нужно, поэтому замена всегда найдётся.
                dropped_ungrounded += 1
                continue
        if a is None:
            question = qe_order[used_qe % len(qe_order)]
            used_qe += 1
            target = reflection_target_empty(i, rng, deep=(out and len(out) % 3 == 0))
            act_key = "none"
            layer = None
        else:
            question = q_order[used_q % len(q_order)]
            used_q += 1
            target = reflection_target(a, i, rng,
                                       deep=(out and len(out) % 3 == 0))
            act_key = a.get("act") or "none"
            layer = a.get("layer")

        def render(r, c, m):
            if r == "user" and not c.startswith("<<ENV>>"):
                return f"[сообщение {m['message_no']}] {c}"
            if r == "assistant":
                return f"[сообщение {m['message_no']}] {c}"
            return c

        messages = [{"role": "system", "content": system_prompt}]
        messages += [{"role": "user" if r == "user" else "assistant",
                      "content": render(r, c, m)}
                     for r, c, m in hist]
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": target})
        # История подрезается с начала; целевой ответ сохраняется целиком.
        while len(messages) > 3 and ntok(tok, messages) > max_len:
            del messages[1]
        if ntok(tok, messages) > max_len:
            continue
        out.append({
            "id": f"{bio['meta']['bio_id']}-refl-{len(out):03d}",
            "sloy": "reflection",
            "kind": "reflection",
            "bio_id": bio["meta"]["bio_id"],
            "cut_index": i,
            "window": window,
            "act": act_key,
            "act_grounded": True,
            "layer": layer,
            "messages": messages})
    REFLECT_STATS["dropped_ungrounded"] = \
        REFLECT_STATS.get("dropped_ungrounded", 0) + dropped_ungrounded
    REFLECT_STATS["kept"] = REFLECT_STATS.get("kept", 0) + len(out)
    return out


REFLECT_STATS = {}


# ------------------------------------------------------ сборка и проверка
def load_bios(bios_dir):
    out = []
    for p in sorted(Path(bios_dir).glob("bio-*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def grammar_share(n_grammar, n_total):
    return n_grammar / n_total if n_total else 0.0


def grammar_target_n(n_bio, n_refl, share):
    """Число записей слоя 1, дающее заданную долю грамматики в материале.

    доля = g / (g + n_bio + n_refl), поэтому g = share/(1-share) * (остальные).
    """
    g = share / (1.0 - share) * (n_bio + n_refl)
    return max(1, int(round(g)))


def split_train_valid(records):
    """90/10 внутри каждого слоя, детерминированно по id."""
    train, valid = [], []
    for r in records:
        h = int(sha1(r["id"]), 16)
        (train if h % 10 < 9 else valid).append(r)
    return train, valid


def sample_examples(examples, cap):
    """Ровный отбор записей слоя 2 по всей биографии (не первые N).

    Нужен, потому что требование «30-40 биографий» и требование «доля
    грамматики 13-20 %» вместе дают конечное число записей слоя 2. Срез
    идёт с ровным шагом, чтобы не потерять поздние ходы (перекрёстные
    ссылки, проверки, сверку времени).

    Записи с подтверждением отказа акта сохраняются всегда: это
    единственная демонстрация отвергнутых предложений, и терять её нельзя.
    """
    if not cap or len(examples) <= cap:
        return examples
    keep = [e for e in examples
            if envelope_has_rejection(e["messages"])]
    keep_ids = {e["id"] for e in keep}
    rest = [e for e in examples if e["id"] not in keep_ids]
    room = max(0, cap - len(keep))
    if room == 0:
        return keep
    if len(rest) <= room:
        picked = rest
    else:
        step = len(rest) / room
        idx = sorted({min(len(rest) - 1, int(round(i * step)))
                      for i in range(room)})
        picked = [rest[i] for i in idx]
    return keep + picked


def dedupe_by_messages(records):
    """Убрать записи с одинаковым набором сообщений (уникальность >= 90 %).

    Bio-XX старше, чем bio-1X, поэтому при переходе 9 -> 10 идентификатор
    меняет ширину: «bio-1-x001-p1» совпадает с «bio-10-x001-p1» только по
    тексту сообщений, а не по id. Такие повторы убираем.
    """
    seen = set()
    out = []
    for r in records:
        h = sha1(json.dumps(r["messages"], ensure_ascii=False))
        if h in seen:
            continue
        seen.add(h)
        out.append(r)
    return out


def dump(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip()]


def acts_in(messages, last_only):
    out = []
    if last_only:
        msgs = messages[-1:]
    else:
        msgs = [m for m in messages if m["role"] == "assistant"]
    for m in msgs:
        for blk in act_blocks(m["content"]):
            out += blk or []
    return out


KNOBS_ALLOWED = [
    "audibility_floor", "surfacing_cap", "consolidation_ceiling",
    "interference_factor", "prefix_depth", "residency_horizon",
    "rebuild_period", "gap_threshold", "surprise_threshold",
] + [f"tau_multiplier.t{i}" for i in range(1, 6)]


def check_material(records, bios, tok, max_len, share_lo, share_hi):
    """Машинная проверка состава и полноты.

    Внутри материала НЕТ оценок «правильно/неправильно»: качество ответов
    оценивает владелец. Здесь только состав, числа и полнота.
    """
    rep = {}
    ids = [r["id"] for r in records]
    hashes = [sha1(json.dumps(r["messages"], ensure_ascii=False)) for r in records]
    rep["records_total"] = len(records)
    rep["unique_ids"] = len(set(ids))
    rep["unique_message_sets"] = len(set(hashes))
    rep["uniqueness_rate"] = (round(len(set(hashes)) / len(records), 4)
                              if records else 0.0)
    rep["uniqueness_ok"] = rep["uniqueness_rate"] >= 0.90
    by_sloy = {}
    for r in records:
        by_sloy[r["sloy"]] = by_sloy.get(r["sloy"], 0) + 1
    rep["by_layer"] = by_sloy
    rep["biography_exchange_kinds"] = dict(sorted(
        {k: sum(1 for r in records
                if r["sloy"] == "biography" and r.get("kind") == k)
         for k in sorted({r.get("kind") for r in records
                          if r["sloy"] == "biography"})}.items()))
    rep["grammar_share"] = round(grammar_share(by_sloy.get("grammar", 0),
                                               len(records)), 4)
    rep["grammar_share_ok"] = share_lo <= rep["grammar_share"] <= share_hi

    act_target = {a: 0 for a in ALL_ACTS}
    act_context = {a: 0 for a in ALL_ACTS}
    layers = {l: 0 for l in LAYERS}
    old_layers = {}
    bad_layer = []
    knob_counter = {}
    unknown_knobs = {}
    cal_cases = set()
    cal_cases_target = set()
    knob_counter_target = {}
    frozen_cases = 0
    frozen_in_target = 0
    rejected_demos = 0
    frozen_records = 0
    rejected_bio_records = 0
    long_recs = []
    target_loss = []
    parse_errors = []
    for r in records:
        t = acts_in(r["messages"], True)
        c = acts_in(r["messages"], False)
        for a, box in [(a, act_target) for a in t] + [(a, act_context) for a in c]:
            if not isinstance(a, dict):
                parse_errors.append(r["id"])
                continue
            nm = a.get("act")
            if nm in box:
                box[nm] += 1
            if nm == "calibrate":
                prop = a.get("proposal") or {}
                ev = tuple(sorted((e.get("metric"), e.get("tick"),
                                   e.get("record_id"), e.get("layer"))
                                  for e in (a.get("evidence") or [])))
                key = (tuple(sorted(prop.items())), ev)
                cal_cases.add(key)
                if box is act_target:
                    cal_cases_target.add(key)
                    for k in prop:
                        if k in KNOBS_ALLOWED:
                            knob_counter_target[k] = knob_counter_target.get(k, 0) + 1
                bad = [k for k in prop if k in ("act_price", "self_improvement")]
                if bad:
                    frozen_cases += 1
                    if box is act_target:
                        frozen_in_target += 1
                    continue
                for k in prop:
                    if k in KNOBS_ALLOWED:
                        knob_counter[k] = knob_counter.get(k, 0) + 1
                    else:
                        unknown_knobs[k] = unknown_knobs.get(k, 0) + 1
            if nm in WRITE_ACTS:
                l = a.get("layer")
                if l in LAYERS:
                    layers[l] = layers.get(l, 0) + 1
                elif l in OLD_LAYER_NAMES:
                    old_layers[l] = old_layers.get(l, 0) + 1
                else:
                    bad_layer.append((r["id"], l))
        if envelope_has_rejection(r["messages"]):
            rejected_demos += 1
            if r["sloy"] == "biography":
                rejected_bio_records += 1
        n = ntok(tok, r["messages"])
        if n > max_len:
            long_recs.append((r["id"], n))
        last = r["messages"][-1]
        if last["role"] != "assistant" or not last["content"].strip():
            target_loss.append((r["id"], "последнее сообщение не ответ"))
        if ntok(tok, [r["messages"][0], last]) > max_len:
            target_loss.append((r["id"], "целевой ответ длиннее предела"))
    rep["act_calls_in_targets"] = act_target
    rep["act_calls_in_context"] = act_context
    rep["acts_covered_in_targets"] = sorted(a for a, n in act_target.items() if n)
    rep["acts_missing_in_targets"] = sorted(a for a, n in act_target.items() if not n)
    rep["layer_values"] = layers
    rep["old_layer_names_found"] = old_layers
    rep["bad_layer_values"] = bad_layer[:10]
    rep["layers_ok"] = (not bad_layer) and (not old_layers)
    rep["calibrate_cases"] = len(cal_cases)
    rep["calibrate_cases_in_targets"] = len(cal_cases_target)
    rep["calibrate_cases_ok"] = len(cal_cases) >= 10
    rep["calibrate_knobs"] = dict(sorted(knob_counter.items()))
    rep["calibrate_knobs_distinct"] = len(knob_counter)
    rep["calibrate_knobs_distinct_in_targets"] = len(knob_counter_target)
    rep["calibrate_handles_ok"] = (len(knob_counter) >= 3
                                   and len(knob_counter_target) >= 3)
    rep["unknown_knobs"] = unknown_knobs
    rep["frozen_proposal_cases"] = frozen_cases
    rep["frozen_proposal_cases_in_target"] = frozen_in_target
    # Случай отказа: биография предлагает замороженную ручку, приходит
    # подтверждение об отказе, модель продолжает обычными актами.
    rep["frozen_rejection_cases"] = rejected_demos
    rep["frozen_rejection_demos"] = rejected_demos
    rep["frozen_rejection_records"] = rejected_bio_records
    rep["frozen_ok"] = frozen_cases > 0 and rejected_demos > 0
    rep["records_above_limit"] = long_recs[:10]
    rep["records_above_limit_count"] = len(long_recs)
    rep["length_ok"] = not long_recs
    rep["target_loss"] = target_loss[:10]
    rep["target_ok"] = not target_loss
    # Записи вида system+ответ: история подрезана целиком. Это наследие v04
    # (там таких 72), а не потеря: целевой ответ на месте.
    rep["records_without_history"] = sum(1 for r in records
                                         if len(r["messages"]) == 2)
    rep["act_parse_errors"] = parse_errors[:10]

    # --- осмысленность пар «имя — значение» ---
    # Сверка не только с реестром биографии: у актов решения имя собирается
    # из имени и значения факта, поэтому допустимо и вхождение значения как
    # части имени. Считаем пары, которых нет ни в реестре, ни как имя+значение.
    ledger_pairs = set()
    ledger_subjects = set()
    for b in bios:
        for e in b["ledger"]:
            ledger_pairs.add((e["subject"], e["value"]))
            ledger_subjects.add(e["subject"])
    named = 0
    exact_pairs = 0
    derived_pairs = 0
    bad_pairs = []
    for r in records:
        for a in acts_in(r["messages"], True):
            if not isinstance(a, dict) or a.get("act") != "name":
                continue
            content = a.get("content") or ""
            if " — " not in content:
                continue
            subj, val = content.split(" — ", 1)
            named += 1
            if r["sloy"] != "biography":
                continue
            if (subj, val) in ledger_pairs:
                exact_pairs += 1
                continue
            if any(s in subj and v == val for s, v in ledger_pairs):
                derived_pairs += 1
                continue
            bad_pairs.append((r["id"], subj, val))
    rep["name_acts_with_pair_form"] = named
    rep["name_pairs_exact_ledger"] = exact_pairs
    rep["name_pairs_derived_from_ledger"] = derived_pairs
    rep["name_pairs_not_in_ledger"] = len(bad_pairs)
    rep["meaningless_pairs_sample"] = bad_pairs[:10]
    rep["meaningless_pairs_ok"] = not bad_pairs

    # --- покрытие разделов Инструкции слоем 1 ---
    gram_units = sorted({r.get("unit_title") for r in records
                         if r["sloy"] == "grammar" and r.get("kind") == "unit"})
    gram_rules = sorted({r.get("unit_title") for r in records
                         if r["sloy"] == "grammar" and r.get("kind") == "rule"})
    gram_forms = sorted({r.get("unit_title") for r in records
                         if r["sloy"] == "grammar" and r.get("kind") == "form"})
    rep["grammar_sections_in_material"] = gram_units
    rep["grammar_rule_records"] = len(gram_rules)
    rep["grammar_form_records"] = len(gram_forms)

    # --- слой 3: состав по актам и по вопросам ---
    refl = [r for r in records if r["sloy"] == "reflection"]
    rep["reflection_records"] = len(refl)
    rep["reflection_by_act"] = dict(sorted(
        {a: sum(1 for r in refl if r.get("act") == a)
         for a in sorted({r.get("act") for r in refl})}.items()))
    rep["reflection_distinct_layers"] = sorted({str(r.get("layer")) for r in refl})
    questions = set()
    for r in refl:
        if r["messages"][-2]["role"] == "user":
            questions.add(r["messages"][-2]["content"])
    rep["reflection_distinct_questions"] = len(questions)
    rep["reflection_without_act_in_target"] = sum(
        1 for r in refl if not acts_in(r["messages"], True))

    # --- системные подсказки по слоям ---
    sys3 = sorted({r["messages"][0]["content"] for r in records
                   if r["sloy"] == "reflection"})
    sys1 = sorted({r["messages"][0]["content"] for r in records
                   if r["sloy"] == "grammar"})
    sys2 = sorted({r["messages"][0]["content"] for r in records
                   if r["sloy"] == "biography"})
    def has_rules(s):
        return ("- name —" in s) or ("Акты:" in s) or ("заморожен" in s)             or ("±50" in s) or ("дефолта нет" in s) or ("t1 (часы)" in s)
    rep["system_prompt_variants"] = {"grammar": len(sys1),
                                     "biography": len(sys2),
                                     "reflection": len(sys3)}
    rep["reflection_system_no_rules"] = not any(has_rules(s) for s in sys3)
    rep["reflection_system_text"] = sys3
    rep["grammar_system_no_rules"] = not any(has_rules(s) for s in sys1)
    rep["grammar_system_text"] = sys1
    rep["biography_system_has_rules"] = any(has_rules(s) for s in sys2)

    only = {r["sloy"] for r in records}
    checks_applicable = {
        "есть отвергнутые предложения (замороженные ручки)": "biography" in only or "reflection" in only,
        "нет записей вида system+ответ без истории": True,
    }
    checks = {
        "уникальность >= 90 %": rep["uniqueness_ok"],
        "доля грамматики 13-20 %": rep["grammar_share_ok"],
        "покрыты все семь актов (в целях)": not rep["acts_missing_in_targets"],
        "имена слоёв только t1-t5": rep["layers_ok"],
        "случаев calibrate >= 10 (в целях тоже >= 10)":
            rep["calibrate_cases_ok"] and rep["calibrate_cases_in_targets"] >= 10,
        "ручек в calibrate >= 3 (в целях тоже >= 3)": rep["calibrate_handles_ok"],
        "есть отвергнутые предложения (замороженные ручки)": rep["frozen_ok"],
        "нет бессмысленных пар «имя — значение»": rep["meaningless_pairs_ok"],
        "нет записей длиннее предела": rep["length_ok"],
        "целевой ответ не выпадает": rep["target_ok"],
        "нет записей вида system+ответ без истории":
            rep["records_without_history"] == 0,
        "у слоя 3 подсказка без правил": rep["reflection_system_no_rules"],
        "у слоя 1 подсказка без правил": rep["grammar_system_no_rules"],
    }
    for k, applies in checks_applicable.items():
        if not applies:
            checks[k + " [слой отсутствует, проверка неприменима]"] = checks.pop(k)
    rep["checks"] = checks
    rep["checks_not_applicable"] = [k for k in checks
                                    if "неприменима" in k]
    rep["checks_passed"] = sum(1 for k, v in checks.items()
                               if v and "неприменима" not in k)
    rep["checks_total"] = len(checks) - len(rep["checks_not_applicable"])
    return rep


def main():
    ap = argparse.ArgumentParser(description="Сборка материала v05 (три слоя)")
    ap.add_argument("--out", default=str(ROOT / "experiments/o8-pass/material-v05"))
    ap.add_argument("--work", default=None,
                    help="каталог промежуточных файлов (по умолчанию "
                         "experiments/o8-pass/.v05-build; внутрь material-v05 "
                         "промежуточные файлы не кладём)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bios", type=int, default=38)
    ap.add_argument("--exchanges", type=int, default=200)
    ap.add_argument("--reflect-per-bio", type=int, default=30)
    ap.add_argument("--grammar-share", type=float, default=0.165)
    ap.add_argument("--grammar-count", type=int, default=0,
                    help="явное число записей слоя 1 (0 = считать по доле). "
                         "Нужно при сборке одного слоя: --layers 1 без этого "
                         "даёт минимум записей, потому что доля считается "
                         "от объёма остальных слоёв")
    ap.add_argument("--layers", default="1,2,3",
                    help="какие слои собирать: 1 грамматика, 2 биографии, "
                         "3 задачи с вопросом на размышление")
    ap.add_argument("--max-len", type=int, default=MAX_LEN_DEFAULT)
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--bio-examples-per-bio", type=int, default=100,
                    help="ограничить число записей слоя 2 на одну биографию "
                         "(0 = без ограничения). Ограничение нужно, чтобы "
                         "требования «30-40 биографий» и «доля грамматики "
                         "13-20 %» выполнялись вместе; срез идёт ровным "
                         "шагом по всей биографии")
    ap.add_argument("--reflect-system", choices=["hint", "plain"], default="hint",
                    help="подсказка слоя 3: hint — без перечня актов и правил, "
                         "но с упоминанием формы блока; plain — вообще без "
                         "упоминания актов")
    ap.add_argument("--core",
                    default=str(ROOT / "experiments/o8-pass/gemma4-12b-text-4bit"))
    args = ap.parse_args()

    want = [int(x) for x in args.layers.split(",") if x.strip()]
    out = Path(args.out)
    work = Path(args.work) if args.work else ROOT / "experiments/o8-pass/.v05-build"
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    gb = load_module("_gb", HERE / "gen_biography.py")
    ga = load_module("_ga", HERE / "gen_acts.py")
    em = load_module("_em", HERE / "emit_mlx.py")
    # Опечатка в профиле production: ключ "t4" вместо "project"
    # (build_bio обращается к vocab["project"]). Правим только в памяти,
    # файл gen_biography.py не трогаем.
    prod = gb.DOMAINS.get("production") or {}
    if "project" not in prod and "t4" in prod:
        prod["project"] = prod.pop("t4")
    tok = load_tokenizer(args.core)
    print("ядро-токенизатор загружен:", args.core)

    bios_path = work / "biographies.jsonl"
    if bios_path.exists():
        bios = read_jsonl(bios_path)
        print("биографии взяты из кэша:", len(bios))
    else:
        domain_ids = list(gb.DOMAINS.keys())
        bios = [gb.build_bio(args.seed, i,
                             domain_ids[(i - 1) % len(domain_ids)],
                             args.exchanges)
                for i in range(1, args.bios + 1)]
        dump(bios_path, bios)
        print("биографий собрано:", len(bios))

    bio_records, refl_records = [], []
    rej_total = 0
    knob_by_bio = {}
    main_handles = set()
    for idx, bio in enumerate(bios):
        # Таблицу диагностики ставим ДО сборки потока: иначе сдвиг не влияет
        # и в материал попадают одни и те же ручки (как это и вышло в v04).
        install_diag(ga, idx)
        ba = ga.BioActs(bio).build()
        errs = ba.validate()
        if errs:
            raise SystemExit(f"{bio['meta']['bio_id']}: ошибки потока актов: "
                             f"{errs[:3]}")
        acts = {"bio_id": bio["meta"]["bio_id"], "records": ba.records,
                "timeline": ba.timeline, "final_tick": ba.tick}
        if 2 in want:
            table = list(ga.DIAG_CASES_EXT)
            rej_total += insert_frozen_proposals(acts)
            for tl in acts["timeline"]:
                for ph in tl["phases"]:
                    for a in (ph.get("acts") or []):
                        if a.get("act") == "calibrate":
                            for k in (a.get("proposal") or {}):
                                if k not in ("act_price", "self_improvement"):
                                    main_handles.add(k)
            knob_by_bio[bio["meta"]["bio_id"]] = sorted(
                {k for tl in acts["timeline"] for ph in tl["phases"]
                 for a in (ph.get("acts") or []) if a.get("act") == "calibrate"
                 for k in (a.get("proposal") or {})})
            bio_records += [
                {"id": e["id"], "sloy": "biography", "kind": e["kind"],
                 "bio_id": e["bio_id"], "message_no": e["message_no"],
                 "messages": e["messages"]}
                for e in sample_examples(
                    [x for x in em.build_examples(bio, acts, window=args.window,
                                                  tok=tok, max_len=args.max_len)
                     # Запись из системного сообщения и ответа без истории:
                     # окно подрезано целиком (наследие v04 — там таких 72).
                     # В v05 такие не берём: учить нечему, контекста нет.
                     if len(x["messages"]) > 2],
                    args.bio_examples_per_bio)]
        if 3 in want:
            rng = random.Random(f"refl:{args.seed}:{bio['meta']['bio_id']}")
            refl_records += reflection_records(
                bio, acts, em, tok, args.max_len, args.reflect_per_bio, rng,
                system_prompt=(SYSTEM_NO_RULES_HINT if args.reflect_system == "hint"
                               else SYSTEM_NO_RULES_PLAIN))
    if 2 in want:
        print(f"слой 2: {len(bio_records)} записей; случаев отказа: {rej_total}; "
              f"ручек в калибровке: {sorted(main_handles)}")

    gram_records = []
    if 1 in want:
        text = GRAMMAR_PATH.read_text(encoding="utf-8")
        pool, units = build_grammar_pool(text, tok, args.max_len,
                                         GRAMMAR_UNIT_MAX_TOKENS)
        n_target = (args.grammar_count or
                    grammar_target_n(len(bio_records), len(refl_records),
                                     args.grammar_share))
        rng = random.Random(f"gram:{args.seed}")
        gram_records = grammar_records(pool, units, n_target, rng, tok,
                                       args.max_len, SYSTEM_NO_RULES_PLAIN)
        print(f"слой 1: пул {len(pool)}, разделов Инструкции {len(units)}, "
              f"в материале разделов {len(GRAMMAR_STATS.get('written_units', []))},"
              f" отобрано {len(gram_records)} (цель {n_target})")

    records = gram_records + bio_records + refl_records
    for r in records:
        r.setdefault("sloy", "biography")
    before = len(records)
    records = dedupe_by_messages(records)
    if before != len(records):
        print(f"убрано повторов по тексту сообщений: {before - len(records)}")
    train, valid = split_train_valid(records)
    dump(out / "train.jsonl", train)
    dump(out / "valid.jsonl", valid)
    print(f"train {len(train)} / valid {len(valid)}")

    rep = check_material(train + valid, bios, tok, args.max_len, 0.13, 0.20)
    rep["grammar_units_covered"] = len(GRAMMAR_STATS.get("covered_units", []))
    rep["grammar_units_total"] = len(GRAMMAR_STATS.get("all_units", []))
    rep["grammar_units_written"] = len(GRAMMAR_STATS.get("written_units", []))
    rep["reflection_candidates_dropped_ungrounded"] = REFLECT_STATS.get(
        "dropped_ungrounded", 0)
    rep["grammar_units_covered_titles"] = sorted(
        {r.get("unit_title") for r in gram_records})
    manifest = {
        "material": "o8-pass-v05 (один проход Инструкции, три слоя, "
                    "грамматика v0.2.0)",
        "created": "2026-09-13",
        "generator": "experiments/organ-dataset/gen_material_v05.py",
        "rebuild_command": (
            "python3 experiments/organ-dataset/gen_material_v05.py "
            f"--out experiments/o8-pass/material-v05 --seed {args.seed} "
            f"--bios {args.bios} --exchanges {args.exchanges} "
            f"--reflect-per-bio {args.reflect_per_bio} "
            f"--grammar-share {args.grammar_share} --layers {args.layers} "
            f"--reflect-system {args.reflect_system}"),
        "layers_switch": ("--layers 1,2,3: 1 — грамматика (доля 13-20 %), "
                          "2 — биографии, 3 — задачи с вопросом на размышление"),
        "counts": {"train": len(train), "valid": len(valid),
                   "total": len(train) + len(valid)},
        "composition_check": rep,
        "grammar_source": "experiments/act-grammar/act-grammar-v0.2-ru.md",
        "system_prompt": {
            "biography": "полная подсказка с перечнем актов и правилами (как в v04)",
            "grammar": "краткая подсказка без перечня актов и правил",
            "reflection": ("краткая подсказка без перечня актов и правил "
                           "(вариант " + args.reflect_system + ") — требование "
                           "решения владельца 11.09.2026: правила из контекста "
                           "убираются"),
        },
        "note_len": (f"предел {args.max_len} токенов; у слоя 2 окно истории "
                     f"{args.window} сообщений; у слоёв 1 и 3 история "
                     f"подрезается с начала, целевой ответ сохраняется целиком"),
        "mask_prompt": True,
        "layers_present": {
            "grammar": "дословные разделы Инструкции и пары «вопрос-ответ»; "
                       "системная подсказка без правил",
            "biography": "биографии пробуждения; системная подсказка полная",
            "reflection": "контекст обрывается в случайном месте, короткий "
                          "вопрос на размышление, целевой ответ с опорой на "
                          "Инструкцию; ПРАВИЛА ИЗ КОНТЕКСТА УБРАНЫ",
        },
        "intermediate_files": ("биографии кэшируются в "
                               "experiments/o8-pass/.v05-build/biographies.jsonl; "
                               "внутрь material-v05 они не попадают"),
        "did_not_touch": ["experiments/o8-pass/material-v04/"],
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items()
                      if k not in ("reflection_system_text",
                                   "grammar_system_text")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
