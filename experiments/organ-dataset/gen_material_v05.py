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
     "Перечень ручек (только они):",
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


def grammar_records(pool, units, target_n, rng, tok, max_len, system_prompt):
    """Отбор записей слоя 1: все пары-правила и формы + по единицам дословно."""
    must = [p for p in pool if p["kind"] in ("rule", "form")]
    unit_pool = {}
    for p in pool:
        if p["kind"] == "unit":
            unit_pool.setdefault(p["unit"], []).append(p)
    need = max(0, target_n - len(must))
    rng.shuffle(must)
    need = min(need, sum(len(v) for v in unit_pool.values()))
    per_unit = {u: 1 for u in unit_pool} if need >= len(unit_pool) else {}
    left = need - sum(per_unit.values())
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
    picked = list(must[:target_n])
    for u, n in sorted(per_unit.items()):
        items = unit_pool[u][:]
        rng.shuffle(items)
        picked += items[:n]
    rng.shuffle(picked)

    records = []
    for i, p in enumerate(picked):
        msgs = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": p["question"]},
                {"role": "assistant", "content": p["answer"]}]
        if ntok(tok, msgs) > max_len:
            continue  # в предел не влезло — в материал не берём
        records.append({"id": f"gr-{p['kind']}-{i:04d}",
                        "sloy": "grammar",
                        "kind": p["kind"],
                        "messages": msgs})
    return records


# ------------------------------------------------- слой 2: биографии (v04+)
# Случаи отвергнутых предложений: замороженные ручки act_price и
# self_improvement. В v04 таких случаев не было ни одного (проверено).
# calibrate не пишет записей и не двигает тики, поэтому демонстрация
# отказа не ломает счёт тиков в потоке биографии.
REJECTIONS = [
    ("act_price", "ручка act_price заморожена"),
    ("self_improvement", "ручка self_improvement заморожена"),
]

# Таблица диагностики для случаев калибровки. Взята из gen_acts.py
# (DIAG_CASES локально, чтобы не менять тот файл) и расширена: в v04
# генератор всегда брал первые четыре строки, поэтому в материале были
# только четыре ручки. В v05 строки разводятся по номеру биографии.
DIAG_CASES = [
    ("died_too_early", 0.004, "audibility_floor", 0.005),
    ("wasted_surface", 40.0, "surfacing_cap", 10.0),
    ("loop_repeat", 9.0, "consolidation_ceiling", 6.0),
    ("stale_win", 0.30, "tau_multiplier.t3", 1.4),
    ("died_too_early", 0.006, "audibility_floor", 0.007),
    ("wasted_surface", 30.0, "prefix_depth", 9.0),
    ("loop_repeat", 7.0, "consolidation_ceiling", 5.0),
    ("stale_win", 0.25, "tau_multiplier.t4", 0.8),
    ("died_too_early", 0.008, "audibility_floor", 0.008),
    ("wasted_surface", 20.0, "residency_horizon", 8.0),
    ("loop_repeat", 6.0, "consolidation_ceiling", 4.0),
    ("stale_win", 0.20, "tau_multiplier.t2", 1.2),
    ("wasted_surface", 28.0, "interference_factor", 1.3),
    ("loop_repeat", 8.0, "rebuild_period", 0.7),
]


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


def rotate_calibrations(acts, bio_index):
    """Развести случаи калибровки по разным ручкам (требование: >=3 ручек)."""
    used = []
    j = 0
    for tl in acts["timeline"]:
        for ph in tl["phases"]:
            if ph["role"] != "assistant":
                continue
            for a in ph.get("acts") or []:
                if a.get("act") != "calibrate":
                    continue
                name, val, knob, newval = DIAG_CASES[(bio_index + j) % len(DIAG_CASES)]
                j += 1
                a["proposal"] = {knob: newval}
                a["evidence"] = [dict(e, metric=name) for e in a["evidence"]]
                used.append(knob)
    return used


# ------------------------------- слой 3: задачи с вопросом на размышление
REFLECT_QUESTIONS = [
    "Стоп. Что здесь стоит удержать и какой акт к месту?",
    "Пауза. Что из этого стоит удержать и какой акт здесь уместен?",
    "Что здесь стоит удержать? Каким актом это закрепить?",
    "Остановка. Что здесь удержать и какой акт выбрать?",
    "Что тут стоит удержать в памяти, а какой акт к месту?",
    "Подумай: что здесь стоит удержать и какой акт к месту?",
    "Коротко: что здесь держать в памяти и какой акт к месту?",
]
REFLECT_REASONS = {
    "name": ["факт прозвучал прямо, значит источник — user",
             "это факт из диалога, записываю дословно"],
    "repeat": ["запись уже есть и всё ещё верна — усиливаю её по id",
               "дубликат дробит амплитуду, поэтому повтор по id"],
    "connect": ["здесь вывод из нескольких записей, значит connect со ссылками",
                "это вывод, а не факт: connect с refs на источники"],
    "reconcile": ["здесь сверка прожитого и аудируемого времени, значит reconcile",
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


def next_assistant_with_acts(tr, i):
    for j in range(i, len(tr)):
        if tr[j][0] == "assistant" and tr[j][2].get("acts"):
            return j
    return None


def subject_hint_for(act_view, tr, i):
    """Короткая подсказка «что удержать» — из самого акта биографии."""
    act = act_view.get("act")
    if act in ("name", "connect", "reconcile"):
        c = act_view.get("content") or ""
        c = c.strip().replace("\n", " ")
        return (c[:160] + ("…" if len(c) > 160 else "")) if c else "факт из диалога"
    if act == "repeat":
        return f"ранее записанное (id {act_view.get('refs')})"
    if act == "read":
        return "ответ на вопрос из истории за пределами окна"
    if act == "scan":
        return "числа физики памяти: амплитуды, тики, слои"
    if act == "calibrate":
        prop = act_view.get("proposal") or {}
        return "перекос в числах физики по ручке " + ", ".join(prop)
    return "то, что прозвучало в контексте"


def reflection_target(act_view, layer, rng, deep):
    act = act_view.get("act")
    hint = subject_hint_for(act_view, None, None)
    parts = [f"Удержать стоит: {hint}."]
    if layer:
        parts.append("Место — " + layer + " ("
                     + REFLECT_LAYER_NOTE.get(layer, "") + "); дефолта нет, "
                     "выбираю по горизонту факта.")
    if act in ("name", "repeat", "connect", "reconcile"):
        parts.append("Здесь " + rng.choice(REFLECT_REASONS[act]) + ".")
    elif act in REFLECT_REASONS:
        parts.append("Здесь " + rng.choice(REFLECT_REASONS[act]) + ".")
    parts.append("Акт к месту — `" + str(act) + "`.")
    if deep:
        parts.append("Лишних актов не выпускаю: принудительные акты — шум; "
                     "если удерживать нечего, отвечаю без блока.")
    text = " ".join(parts)
    view = {k: v for k, v in act_view.items()
            if k in ("act", "content", "source", "layer", "valid_time",
                     "record_tick", "refs", "mode", "count", "ids", "proposal",
                     "evidence", "budget_used")}
    return render_assistant(text, [view])


def reflection_records(bio, acts, em, tok, max_len, n, rng):
    """Слой 3: контекст обрывается в случайном месте + вопрос на размышление.

    Системная подсказка НЕ содержит ни перечня актов, ни правил.
    """
    tr = em.transcript_of(bio, acts)
    cuts = [i for i in range(3, len(tr))
            if next_assistant_with_acts(tr, i) is not None]
    rng.shuffle(cuts)
    out = []
    used_q = 0
    for i in cuts:
        if len(out) >= n:
            break
        window = rng.choice([2, 3, 4, 5, 6, 8])
        hist = tr[max(0, i - window):i]
        if not hist:
            continue
        j = next_assistant_with_acts(tr, i)
        act_view = tr[j][2]["acts"][0]
        question = REFLECT_QUESTIONS[used_q % len(REFLECT_QUESTIONS)]
        used_q += 1
        layer = act_view.get("layer")
        target = reflection_target(act_view, layer, rng, deep=(used_q % 3 == 0))

        def render(r, c, m):
            if r == "user" and not c.startswith("<<ENV>>"):
                return f"[сообщение {m['message_no']}] {c}"
            if r == "assistant":
                return f"[сообщение {m['message_no']}] {c}"
            return c

        messages = [{"role": "system", "content": SYSTEM_NO_RULES_HINT}]
        messages += [{"role": "user" if r == "user" else "assistant",
                      "content": render(r, c, m)}
                     for r, c, m in hist]
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": target})
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
            "act": act_view.get("act"),
            "layer": layer or "t0",
            "messages": messages})
    return out


# ------------------------------------------------------ сборка и проверка
def load_bios(bios_dir):
    out = []
    for p in sorted(Path(bios_dir).glob("bio-*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def grammar_share(n_grammar, n_total):
    return n_grammar / n_total if n_total else 0.0


def choose_grammar_target(n_bio, n_refl, want, lo, hi):
    """Число записей слоя 1, чтобы доля грамматики попала в рамку [lo; hi]."""
    # доля = g / (g + n_bio + n_refl); решаем относительно нижней границы рамки
    target = int(round((lo + (hi - lo) / 2) / (1 - (lo + (hi - lo) / 2))
                       * (n_bio + n_refl)))
    return max(1, target) if want is None else want


def split_train_valid(records):
    """90/10 внутри каждого слоя (детерминированно по id)."""
    train, valid = [], []
    for r in records:
        h = int(sha1(r["id"]), 16)
        (train if h % 10 < 9 else valid).append(r)
    return train, valid


def dump(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def targets_of(rec):
    """Акты в целевом ответе (а также в контексте, отдельно)."""
    msgs = rec["messages"]
    last = msgs[-1]
    target = []
    context = []
    for m in msgs[:-1]:
        if m["role"] == "assistant":
            for b in act_blocks(m["content"]):
                context += b or []
    for b in act_blocks(last["content"]):
        target += b or []
    return target, context


def all_acts(rec):
    t, c = targets_of(rec)
    return t, c


def check_material(train, valid, bios, tok, max_len, share_lo, share_hi):
    """Машинная проверка состава и полноты (без оценок качества ответов)."""
    all_recs = train + valid
    rep = {}
    ids = [r["id"] for r in all_recs]
    rep["records_total"] = len(all_recs)
    rep["records_train"] = len(train)
    rep["records_valid"] = len(valid)
    rep["unique_ids"] = len(set(ids))
    hashes = [sha1(json.dumps(r["messages"], ensure_ascii=False)) for r in all_recs]
    rep["unique_message_hashes"] = len(set(hashes))
    rep["uniqueness_rate"] = round(len(set(hashes)) / len(all_recs), 4) if all_recs else 0.0
    by_sloy = {}
    for r in all_recs:
        by_sloy[r["sloy"]] = by_sloy.get(r["sloy"], 0) + 1
    rep["by_layer"] = by_sloy
    rep["grammar_share"] = round(grammar_share(by_sloy.get("grammar", 0), len(all_recs)), 4)
    rep["grammar_share_ok"] = share_lo <= rep["grammar_share"] <= share_hi

    act_target = {a: 0 for a in ALL_ACTS}
    act_context = {a: 0 for a in ALL_ACTS}
    layers = {l: 0 for l in LAYERS}
    bad_layer = []
    tick_pairs = []
    knob_counter = {}
    cal_cases = set()
    frozen_cases = 0
    rejected_recs = 0
    long_recs = []
    cut_answer_loss = []
    parse_errors = []
    pair_set = set()
    layer_token_layers = set()
    for r in all_recs:
        t, c = all_acts(r)
        for a in t + c:
            if not isinstance(a, dict):
                parse_errors.append(r["id"])
                continue
            nm = a.get("act")
            if nm in act_target:
                (act_target if a in t else act_context)[nm] += 1
            if nm == "calibrate":
                prop = a.get("proposal") or {}
                for k in prop:
                    knob_counter[k] = knob_counter.get(k, 0) + 1
                ev = tuple(sorted((e.get("metric"),
                                   e.get("tick"), e.get("record_id"),
                                   e.get("layer")) for e in (a.get("evidence") or [])))
                key = (tuple(sorted(prop.items())), ev)
                cal_cases.add(key)
                if any(k in ("act_price", "self_improvement") for k in prop):
                    frozen_cases += 1
            if nm in WRITE_ACTS:
                l = a.get("layer")
                if l not in LAYERS:
                    bad_layer.append((r["id"], l))
                else:
                    layers[l] = layers.get(l, 0) + 1
                    tick_pairs.append((r["id"], a.get("record_tick")))
        n = ntok(tok, r["messages"])
        if n > max_len:
            long_recs.append((r["id"], n))
        # целевой ответ не выпал: последнее сообщение — ответ и непустое
        last = r["messages"][-1]
        if last["role"] != "assistant" or not last["content"].strip():
            cut_answer_loss.append((r["id"], "last message not assistant/empty"))
        if ntok(tok, [r["messages"][0], last]) > max_len:
            cut_answer_loss.append((r["id"], "target alone above limit"))
        if r["sloy"] == "reflection":
            layer_token_layers.add(r["messages"][0]["content"])
    rep["act_calls_in_targets"] = act_target
    rep["act_calls_in_context"] = act_context
    rep["acts_covered_in_targets"] = sorted(a for a, n in act_target.items() if n)
    rep["acts_missing_in_targets"] = sorted(a for a, n in act_target.items() if not n)
    rep["layers"] = layers
    rep["bad_layer_values"] = bad_layer[:10]
    rep["layers_names_ok"] = not bad_layer
    rep["calibrate_cases"] = len(cal_cases)
    rep["calibrate_knobs"] = dict(sorted(knob_counter.items()))
    rep["calibrate_knobs_distinct"] = len([k for k, n in knob_counter.items() if n > 0])
    rep["calibrate_ok"] = (len(cal_cases) >= 10
                           and len(knob_counter) >= 3)
    rep["frozen_proposal_cases"] = frozen_cases
    rep["frozen_rejection_demos"] = rejected_recs
    rep["frozen_ok"] = frozen_cases > 0 and rejected_recs > 0
    rep["records_above_limit"] = long_recs[:10]
    rep["records_above_limit_count"] = len(long_recs)
    rep["length_ok"] = not long_recs
    rep["target_loss"] = cut_answer_loss[:10]
    rep["target_ok"] = not cut_answer_loss
    rep["act_parse_errors"] = parse_errors[:10]

    # --- осмысленность пар «имя — значение» ---
    ledger_pairs = set()
    for b in bios:
        for e in b["ledger"]:
            ledger_pairs.add((e["subject"], e["value"]))
    name_pairs = 0
    name_pairs_bad = []
    for r in all_recs:
        t, _ = all_acts(r)
        for a in t:
            if not isinstance(a, dict) or a.get("act") != "name":
                continue
            content = a.get("content") or ""
            if " — " not in content:
                continue
            subj, val = content.split(" — ", 1)
            name_pairs += 1
            if r["sloy"] == "biography" and (subj, val) not in ledger_pairs:
                name_pairs_bad.append((r["id"], subj, val))
    rep["name_acts_direct_form"] = name_pairs
    rep["name_pairs_vs_ledger"] = len(name_pairs_bad)
    rep["meaningless_pairs"] = name_pairs_bad[:10]
    rep["meaningless_pairs_ok"] = not name_pairs_bad

    # --- слой 3: системная подсказка без правил ---
    sys3 = [r["messages"][0]["content"] for r in all_recs
            if r["sloy"] == "reflection"]
    rep["reflection_system_distinct"] = list(sorted(set(sys3)))
    rep["reflection_system_has_act_list"] = any(
        "- name —" in s or "Акты:" in s for s in sys3)
    rep["reflection_system_has_rules"] = any(
        ("заморожен" in s or "±50" in s or "дефолта нет" in s) for s in sys3)
    rep["reflection_rules_removed_ok"] = (not rep["reflection_system_has_act_list"]
                                          and not rep["reflection_system_has_rules"])
    # --- слой 1: системная подсказка ---
    sys1 = [r["messages"][0]["content"] for r in all_recs
            if r["sloy"] == "grammar"]
    rep["grammar_system_distinct"] = list(sorted(set(sys1)))
    return rep


def main():
    ap = argparse.ArgumentParser(description="Сборка материала v05 (три слоя)")
    ap.add_argument("--out", default=str(ROOT / "experiments/o8-pass/material-v05"))
    ap.add_argument("--work", default=None,
                    help="каталог промежуточных файлов (по умолчанию <out>/.build)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bios", type=int, default=35)
    ap.add_argument("--exchanges", type=int, default=200)
    ap.add_argument("--reflect-per-bio", type=int, default=30)
    ap.add_argument("--grammar-share", type=float, default=0.165)
    ap.add_argument("--layers", default="1,2,3")
    ap.add_argument("--max-len", type=int, default=MAX_LEN_DEFAULT)
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--core", default=str(ROOT / "experiments/o8-pass/gemma4-12b-text-4bit"))
    args = ap.parse_args()

    want = [int(x) for x in args.layers.split(",") if x.strip()]
    out = Path(args.out)
    work = Path(args.work) if args.work else out / ".build"
    (work / "biographies").mkdir(parents=True, exist_ok=True)
    (work / "acts").mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    gb = load_module("_gb", HERE / "gen_biography.py")
    # Опечатка в профиле production: ключ "t4" вместо "project"
    # (build_bio обращается к vocab["project"]). Правим только в памяти —
    # файл gen_biography.py не трогаем.
    prod = gb.DOMAINS.get("production") or {}
    if "project" not in prod and "t4" in prod:
        prod["project"] = prod.pop("t4")
    ga = load_module("_ga", HERE / "gen_acts.py")
    em = load_module("_em", HERE / "emit_mlx.py")
    tok = load_tokenizer(args.core)
    print("ядро-токенизатор загружен:", args.core)

    # --- биографии: генерация и поток актов (своими модулями, без правки
    #     файлов проекта: profile production в gen_biography.py имеет опечатку
    #     ключа "t4" вместо "project"; правим только в памяти) ---
    bios = []
    domain_ids = list(gb.DOMAINS.keys())
    for i in range(1, args.bios + 1):
        bio = gb.build_bio(args.seed, i, domain_ids[(i - 1) % len(domain_ids)],
                           args.exchanges)
        bio["meta"]["domain"] = domain_ids[(i - 1) % len(domain_ids)]
        bios.append(bio)
    print(f"биографий: {len(bios)}")

    bio_records, refl_records = [], []
    rej_total = 0
    knob_used = {}
    for idx, bio in enumerate(bios):
        ba = ga.BioActs(bio).build()
        errs = ba.validate()
        if errs:
            raise SystemExit(f"{bio['meta']['bio_id']}: ошибки потока актов: {errs[:3]}")
        acts = {"bio_id": ba.bio["meta"]["bio_id"], "records": ba.records,
                "timeline": ba.timeline, "final_tick": ba.tick}
        if 2 in want:
            knob_used.setdefault(bio["meta"]["bio_id"], rotate_calibrations(acts, idx))
            rej_total += insert_frozen_proposals(acts)
            bio_records += [
                {"id": e["id"], "sloy": "biography", "kind": e["kind"],
                 "bio_id": e["bio_id"], "message_no": e["message_no"],
                 "messages": e["messages"]}
                for e in em.build_examples(bio, acts, window=args.window,
                                           tok=tok, max_len=args.max_len)]
        if 3 in want:
            rng = random.Random(f"refl:{args.seed}:{bio['meta']['bio_id']}")
            refl_records += reflection_records(
                bio, acts, em, tok, args.max_len, args.reflect_per_bio, rng)
    print(f"слой 2: {len(bio_records)} записей; слой 3: {len(refl_records)} записей; "
          f"демонстраций отказа: {rej_total}")

    gram_records = []
    if 1 in want:
        text = GRAMMAR_PATH.read_text(encoding="utf-8")
        pool, units = build_grammar_pool(text, tok, args.max_len,
                                         GRAMMAR_UNIT_MAX_TOKENS)
        n_target = choose_grammar_target(len(bio_records), len(refl_records),
                                         None, args.grammar_share - 0.015,
                                         args.grammar_share + 0.015)
        rng = random.Random(f"gram:{args.seed}")
        gram_records = grammar_records(pool, units, n_target, rng, tok,
                                       args.max_len, SYSTEM_NO_RULES_HINT)
        print(f"слой 1: пул {len(pool)}, отобрано {len(gram_records)} "
              f"(цель {n_target})")
        for r in gram_records:
            r["sloy"] = "grammar"

    records = gram_records + bio_records + refl_records
    for r in records:
        r.setdefault("sloy", "biography")
    train, valid = split_train_valid(records)
    dump(out / "train.jsonl", train)
    dump(out / "valid.jsonl", valid)
    print(f"train {len(train)} / valid {len(valid)}")

    rep = check_material(train, valid, bios, tok, args.max_len, 0.13, 0.20)
    rep["frozen_rejection_demos"] = rej_total
    rep["frozen_ok"] = (rep["frozen_proposal_cases"] > 0 and rej_total > 0)
    rep["calibrate_knobs_by_bio"] = knob_used if len(knob_used) <= 5 else {
        "bios": len(knob_used)}
    manifest = {
        "material": "o8-pass-v05 (один проход Инструкции; три слоя; "
                    "грамматика v0.2.0)",
        "created": "2026-09-13",
        "generator": "experiments/organ-dataset/gen_material_v05.py",
        "rebuild_command": (
            "python3 experiments/organ-dataset/gen_material_v05.py "
            f"--out experiments/o8-pass/material-v05 --seed {args.seed} "
            f"--bios {args.bios} --exchanges {args.exchanges} "
            f"--reflect-per-bio {args.reflect_per_bio} "
            f"--grammar-share {args.grammar_share} --layers {args.layers}"),
        "layers_switch": "--layers 1,2,3 (1 — грамматика, 2 — биографии, "
                         "3 — задачи с вопросом на размышление)",
        "counts": {"train": len(train), "valid": len(valid),
                   "total": len(train) + len(valid)},
        "composition_check": rep,
        "grammar_source": "experiments/act-grammar/act-grammar-v0.2-ru.md",
        "system_prompt_biography": "полная подсказка с правилами (как в v04)",
        "system_prompt_grammar_and_reflection":
            "без перечня актов и без правил (слой 3 — требование решения "
            "владельца 11.09.2026: правила из контекста убираются)",
        "note_len": (f"предел {args.max_len} токенов; история слоя 2 — окно "
                     f"{args.window} сообщений; у слоёв 1 и 3 история "
                     f"подрезается с начала, целевой ответ сохраняется целиком"),
        "mask_prompt": True,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    main()
