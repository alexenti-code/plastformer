#!/usr/bin/env python3
"""PlastFormer organ-dataset -- synthetic biography generator.

Generates scripted multi-message project conversations (~200 exchanges each)
satisfying E1 corpus requirements R1-R6, plus a bi-temporal ground-truth
ledger: (message_no, world_time, value, superseded_by).

Deterministic (seeded), pure stdlib. Output: biographies/bio-XX.json

Structure of one biography JSON:
  meta         bio_id, seed, domain, persona, project, n_exchanges
  messages     [{message_no, role, content, world_time}]   (2 per exchange)
  ledger       [{fact_id, kind, subject, value, message_no, world_time,
                 valid_time, superseded_by, ...}]            -- scoring oracle
  annotations  [{message_no, kind, fact_ids, extra}]         -- one per exchange,
                 consumed by gen_acts.py to build the act stream.

R-quotas per biography (E1 protocol section 4):
  R1 >= 60 factual statements      R4 >= 5 contradictions (probed later)
  R2 >= 10 position changes        R5 >= 10 repeated facts
  R3 >= 20 cross-references        R6 >= 10 unanswerable probes
"""

import argparse
import datetime
import json
import random
from pathlib import Path

TZ = datetime.timezone(datetime.timedelta(hours=3))
START = datetime.datetime(2026, 9, 7, 10, 0, tzinfo=TZ)

PERSONAS = [
    "Игорь Валентинович", "Мария Сергеевна", "Павел Андреевич",
    "Ольга Дмитриевна", "Сергей Николаевич", "Анна Витальевна",
]
VENDORS = ["ООО «СеверСтрой»", "ООО «Мегаполис-Сервис»", "ИП Ковалёв А.П.",
           "ООО «Проф-Лайн»", "ООО «Гарант-Плюс»"]
CITIES = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Нижний Новгород"]

DOMAINS = {
    "renovation": {
        "project": "ремонт квартиры на Лесной, 12",
        "contractor": "прораб",
        "params": [
            ("бюджет проекта", ["420 000 ₽", "450 000 ₽", "510 000 ₽"], "project"),
            ("дедлайн проекта", ["2026-10-15", "2026-10-20", "2026-11-01"], "project"),
            ("площадь квартиры", ["54 м²", "62 м²", "71 м²"], "project"),
        ],
        "domain_facts": [
            ("высота потолков после выравнивания", ["2,65 м", "2,70 м", "2,58 м"], "project"),
            ("марка штукатурной смеси", ["Knauf MP-75", "Ceresit CT 24", "Volma Aqua"], "episode"),
        ],
        "positions": [
            ("тип напольного покрытия", ["кварцвинил", "инженерная доска", "ламинат"]),
            ("схема освещения", ["трековые светильники", "встроенные споты", "подсветка по периметру"]),
            ("цвет стен в гостиной", ["тёплый серый", "белый базовый", "приглушённый зелёный"]),
            ("сантехника", ["подвесной унитаз", "компакт-унитаз", "инсталляция"]),
            ("кухонный фартук", ["керамогранит", "скинали", "плитка кабанчик"]),
            ("остекление балкона", ["тёплое остекление", "холодное остекление", "французское остекление"]),
        ],
        "controversies": [
            ("материал межкомнатных дверей", ["экошпон", "массив дуба", "эмаль"]),
            ("способ вывоза мусора", ["контейнер у дома", "мешки и самовывоз", "вывоз через УК"]),
        ],
        "unanswerables": [
            "какой у нас был номер лицевого счёта электричества?",
            "сколько стоила аренда подъёмника?",
            "какой шпаклёвкой красили потолок в спальне?",
            "когда привезли вторую партию плитки?",
        ],
    },
    "website": {
        "project": "сайт студии «Формат»",
        "contractor": "разработчик",
        "params": [
            ("бюджет проекта", ["180 000 ₽", "220 000 ₽", "260 000 ₽"], "project"),
            ("дедлайн релиза", ["2026-10-01", "2026-10-10", "2026-09-28"], "project"),
            ("хостинг", ["Timeweb", "Selectel", "Reg.ru"], "project"),
        ],
        "domain_facts": [
            ("число страниц в карте сайта", ["14", "11", "18"], "project"),
            ("размер бэкапа базы", ["340 МБ", "410 МБ", "280 МБ"], "episode"),
        ],
        "positions": [
            ("CMS", ["WordPress", "Craft CMS", "самописная админка"]),
            ("способ деплоя", ["FTP вручную", "GitHub Actions", "Docker на сервере"]),
            ("шрифт заголовков", ["Inter", "Manrope", "Onest"]),
            ("структура главной", ["лончпейдж", "сетка услуг + кейсы", "видео-шапка + кейсы"]),
            ("форма обратной связи", ["встроенная форма + почта", "Telegram-бот", "CRM-виджет"]),
            ("аналитика", ["Яндекс.Метрика", "Метрика + GA4", "Plausible"]),
        ],
        "controversies": [
            ("цвет акцентной кнопки", ["оранжевый", "зелёный", "синий"]),
            ("языковая версия", ["только русская", "русская + английская", "три языка"]),
        ],
        "unanswerables": [
            "какой у нас пароль от админки хостинга?",
            "сколько стоил домен в прошлом году?",
            "какой плагин кэширования мы ставили на старом сайте?",
            "когда мы купили текущий SSL-сертификат?",
        ],
    },
    "conference": {
        "project": "конференция «Данные и люди»",
        "contractor": "координатор площадки",
        "params": [
            ("бюджет конференции", ["620 000 ₽", "700 000 ₽", "780 000 ₽"], "project"),
            ("дата проведения", ["2026-11-14", "2026-11-21", "2026-11-28"], "project"),
            ("площадка", ["Цифровой деловой центр", "лофт Katerna", "ДК Трактор"], "project"),
        ],
        "domain_facts": [
            ("число докладчиков", ["9", "12", "15"], "project"),
            ("вместимость зала", ["180 мест", "220 мест", "150 мест"], "project"),
        ],
        "positions": [
            ("формат докладов", ["20-минутные доклады", "15 минут + 5 вопросов", "PechaKucha"]),
            ("способ регистрации", ["Timepad", "свой лендинг + форма", "QR на входе"]),
            ("раздатка", ["программка на бумаге", "только приложение", "бейджи с QR-программой"]),
            ("буфет", ["кофе-брейк дважды", "кофе + обед", "фуршет в конце"]),
            ("трансляция", ["не ведём", "прямой эфир в VK", "запись потом"]),
            ("спонсорский пакет", ["платиновый за 300k", "два золотых за 150k", "без спонсоров"]),
        ],
        "controversies": [
            ("цвет брендирования", ["графит + оранжевый", "белый + синий", "чёрный + жёлтый"]),
            ("время начала", ["10:00", "11:00", "12:00"]),
        ],
        "unanswerables": [
            "сколько стоил проектор в прошлый раз?",
            "какой был хэштег у прошлогодней конференции?",
            "кто проектировал звук в 2024?",
            "какой ИНН у площадки?",
        ],
    },
    "eshop": {
        "project": "запуск магазина «Гора» (товары для походов)",
        "contractor": "оператор склада",
        "params": [
            ("стартовый бюджет на закупку", ["850 000 ₽", "940 000 ₽", "1 020 000 ₽"], "project"),
            ("дата запуска", ["2026-10-05", "2026-10-12", "2026-10-19"], "project"),
            ("маркетплейс", ["Wildberries", "Ozon", "Яндекс.Маркет"], "project"),
        ],
        "domain_facts": [
            ("число SKU на старте", ["120", "150", "90"], "project"),
            ("срок хранения на складе", ["30 дней", "45 дней", "60 дней"], "episode"),
        ],
        "positions": [
            ("служба доставки", ["СДЭК", "Boxberry", "свой курьер по городу"]),
            ("система учёта", ["МойСклад", "1С:Розница", "Google-таблицы"]),
            ("фото товаров", ["студийная съёмка", "предметная съёмка на белом", "фото поставщика + ретушь"]),
            ("ценовая стратегия", ["паритет с WB", "минус 5% к WB", "плюс 10% к WB, но подарок"]),
            ("брендирование упаковки", ["нейтральный пакет", "фирменный крафт", "пакет с принтом карты"]),
            ("возвраты", ["приём в точке", "курьер забирает", "только через маркетплейс"]),
        ],
        "controversies": [
            ("цвет логотипа", ["хаки", "графитовый", "терракотовый"]),
            ("минимальная сумма заказа", ["1 500 ₽", "2 000 ₽", "без минималки"]),
        ],
        "unanswerables": [
            "сколько весит палатка модели X?",
            "какой номер УТП у поставщика рюкзаков?",
            "сколько мы платили за хранение в августе?",
            "какой артикул у термоса 1,2 л?",
        ],
    },
    "relocation": {
        "project": "переезд семьи в другой город",
        "contractor": "менеджер переездной компании",
        "params": [
            ("бюджет переезда", ["310 000 ₽", "350 000 ₽", "390 000 ₽"], "project"),
            ("дата переезда", ["2026-10-24", "2026-10-31", "2026-11-07"], "project"),
            ("город назначения", ["Калининград", "Тюмень", "Сочи"], "project"),
        ],
        "domain_facts": [
            ("объём вещей", ["28 м³", "34 м³", "22 м³"], "project"),
            ("этаж выгрузки", ["3-й, без лифта", "5-й, лифт грузовой", "9-й, два лифта"], "episode"),
        ],
        "positions": [
            ("способ перевозки вещей", ["газель + контейнер", "одна фура 20 т", "две газели"]),
            ("смена школы", ["перевод до переезда", "перевод после заезда", "частная школа"]),
            ("транспорт семьи", ["поезд", "самолёт", "автомобиль"]),
            ("упаковка мебели", ["плёнка и картон сами", "упаковщики компании", "жёсткие коробки"]),
            ("страховка груза", ["полная на 500k", "только транспортный риск", "без страховки"]),
            ("срок аренды жилья", ["3 месяца", "6 месяцев", "год с выкупом"]),
        ],
        "controversies": [
            ("дата выгрузки", ["утро 24-го", "вечер 24-го", "утро 25-го"]),
            ("кто едет с грузом", ["муж с грузом", "представитель компании", "никто не едет"]),
        ],
        "unanswerables": [
            "какой тариф у ж/д перевозки кошек?",
            "сколько стоила прописка в 2020?",
            "какой номер у договора с прошлой компанией?",
            "какая компания перевозила нас в 2019?",
        ],
    },
    "production": {
        "project": "производственная партия корпусной мебели",
        "contractor": "начальник смены",
        "params": [
            ("стоимость партии", ["1 240 000 ₽", "1 310 000 ₽", "1 190 000 ₽"], "project"),
            ("срок сдачи партии", ["2026-10-30", "2026-11-06", "2026-11-13"], "project"),
            ("материал корпуса", ["ЛДСП Egger", "ЛДСП Lamarty", "МДФ шпон"], "project"),
        ],
        "domain_facts": [
            ("число позиций в одном комплекте", ["14", "17", "11"], "project"),
            ("запас по плитам", ["12%", "8%", "15%"], "episode"),
        ],
        "positions": [
            ("кромление", ["ПВХ 2 мм", "ПВХ 0,4 мм", "акриловая кромка"]),
            ("фурнитура", ["Blum", "Hettich", "Boyard"]),
            ("покрытие фасадов", ["плёнка ПВХ", "эмаль", "HPL-панель"]),
            ("схема упаковки", ["гофрокороб + уголки", "пенопласт + стрейч", "деревянная обрешётка"]),
            ("контроль качества", ["выборочно 10%", "каждое изделие", "только фасады"]),
            ("отгрузка клиенту", ["самовывоз", "наша доставка", "ТК с обрешёткой"]),
        ],
        "controversies": [
            ("цвет фасадов", ["дуб сонома", "графит", "белый матовый"]),
            ("аванс контрагенту", ["30%", "50%", "40%"]),
        ],
        "unanswerables": [
            "сколько гвоздей пошло на партию в июле?",
            "какой номер смены у оператора ЧПУ?",
            "сколько стоил клей в прошлом квартале?",
            "какой артикул у старой ручки-скобы?",
        ],
    },
}

# ---------- generic value generators (synthetic data only) ----------

def v_money(rng):
    return f"{rng.choice([18, 24, 36, 42, 58, 74, 96])} 400 ₽"

def v_date(rng):
    return f"2026-09-{rng.randint(14, 28):02d}"

def v_time(rng):
    return f"{rng.randint(9, 18):02d}:{rng.choice(['00', '15', '30', '45'])}"

def v_phone(rng):
    return f"+7 9{rng.randint(10, 99)} {rng.randint(100, 999)}-{rng.randint(10, 99)}-{rng.randint(10, 99)}"

def v_docnum(rng):
    return f"№{rng.randint(101, 989)}/26"

def v_qty(rng):
    return f"{rng.choice([12, 24, 36, 48, 60])} шт"

def v_percent(rng):
    return f"{rng.choice([5, 10, 15, 20])} %"

def v_hours(rng):
    return f"{rng.choice([2, 3, 4, 6])} часа"

def v_room(rng):
    return rng.choice(["переговорка", "кабинет 404", "зал на первом", "офис на Садовой"])

def v_name(rng):
    return rng.choice(["Алексей", "Мария", "Дмитрий", "Елена", "Николай", "Ксения"])

def v_months(rng):
    return f"{rng.choice([6, 12, 24])} месяцев"

def v_people(rng):
    return f"{rng.choice([2, 3, 4, 5])} человека"

def v_addr(rng):
    return rng.choice(["склад на Промышленной, 4", "база на Южной, 11",
                       "площадка у ТТК, въезд с торца", "терминал на Рязанской, 7"])

# (subject_template, horizon, value_fn, n_instances)
GENERIC_OPS = [
    ("срок поставки от {vendor}", "day", v_date, 4),
    ("время звонка с {contractor}", "beat", v_time, 3),
    ("телефон {contractor}", "project", v_phone, 1),
    ("номер договора с {vendor} №{n}", "episode", v_docnum, 3),
    ("сумма счёта от {vendor} №{n}", "episode", v_money, 5),
    ("объём партии №{n}", "episode", v_qty, 3),
    ("скидка {vendor} за объём", "episode", v_percent, 1),
    ("длительность работ по этапу {n}", "day", v_hours, 5),
    ("место встречи по этапу {n}", "beat", v_room, 3),
    ("дата промежуточной приёмки этапа {n}", "day", v_date, 3),
    ("переплата за срочность", "episode", v_money, 1),
    ("аванс {contractor}", "episode", v_money, 1),
    ("номер пропуска для {contractor}", "episode", v_docnum, 1),
    ("лимит правок", "project", v_qty, 1),
    ("доля предоплаты {vendor}", "episode", v_percent, 1),
    ("штраф {vendor} за просрочку", "episode", v_percent, 1),
    ("запас на складе", "episode", v_qty, 1),
    ("брак в партии №{n}", "episode", v_percent, 4),
    ("время начала работ на этапе {n}", "beat", v_time, 4),
    ("ответственный за этап {n}", "episode", v_name, 4),
    ("контакт ответственного этапа {n}", "episode", v_phone, 2),
    ("номер заявки в {vendor} №{n}", "episode", v_docnum, 3),
    ("сумма возврата от {vendor}", "episode", v_money, 1),
    ("лимит расходов на этап {n}", "day", v_money, 4),
    ("стоимость доставки партии №{n}", "episode", v_money, 2),
    ("срок гарантии", "project", v_months, 1),
    ("исполнителей на этапе {n}", "day", v_people, 3),
    ("дата постановки задачи №{n}", "episode", v_date, 4),
    ("номер счёта-фактуры №{n}", "episode", v_docnum, 4),
    ("доплата за ночные работы", "episode", v_percent, 1),
    ("объём переделок по этапу {n}", "day", v_qty, 2),
    ("время доставки образцов", "beat", v_time, 2),
    ("сумма экономии по этапу {n}", "day", v_money, 2),
    ("адрес склада {vendor}", "project", v_addr, 1),
    ("этаж встречи по этапу {n}", "beat", v_room, 2),
]

UNANSWERABLE_GENERIC = [
    "какой у меня был номер полиса?",
    "сколько весил контейнер в прошлой поставке?",
    "каким был пароль от старого кабинета?",
    "когда у нас день рождения директора?",
    "какой ИНН у второй стороны?",
    "сколько стоил бензин тогда?",
]

# ---------- text templates ----------

T_USER_FACT = [
    "Зафиксируй: {subject} — {value}.",
    "Напомню вводную: {subject}: {value}.",
    "Кстати, {subject} — {value}.",
    "Обновляю данные: {subject}: {value}.",
]
T_USER_FACT_BACKDATED = [
    "Ещё с прошлой недели ({date}): {subject} — {value}.",
    "Это было {date}: {subject}: {value}.",
]
T_ASST_FACT = [
    "Принято: {subject} — {value}.",
    "Запомнил: {subject}: {value}.",
    "Фиксирую: {subject} — {value}.",
]
T_USER_REPEAT = [
    "Повторю важное: {subject} — {value}.",
    "Ещё раз, чтобы точно держалось: {subject}: {value}.",
    "Напоминаю ещё раз: {subject} — {value}.",
]
T_ASST_REPEAT = [
    "Подтверждаю ещё раз: {subject} — {value}.",
    "Да, это уже фиксировали: {subject}: {value}. Подтверждаю.",
]
T_USER_POS_INITIAL = ["По {subject} выбираем: {value}.", "Решение по «{subject}»: {value}."]
T_ASST_POS_INITIAL = [
    "Принято: по «{subject}» действуем так — {value}.",
    "Фиксирую решение: «{subject}» — {value}.",
]
T_USER_POS_CHANGE = [
    "По «{subject}» меняем решение: было {old}, теперь {new}.",
    "Передумали: «{subject}» — больше не {old}, теперь {new}.",
]
T_ASST_POS_CHANGE = [
    "Принято. Было {old}, действующая позиция — {new}. Прежнюю считаю отменённой.",
    "Фиксирую смену: {old} → {new} по «{subject}». Отвечаю по новой позиции.",
]
T_USER_CONTRA = [
    "Слушай, по «{subject}» вообще-то {value}.",
    "Стоп, по «{subject}»: на самом деле {value}.",
]
T_ASST_CONTRA = [
    "Замечаю противоречие: ранее ({m1}, {t1}) — {v1}, теперь — {v2}. Записал оба, ориентируюсь на позднейшее.",
    "Это противоречит сказанному {m1} ({t1}): {v1}. Принял новое: {v2}. Позднейшее — приоритет.",
]
T_USER_PROBE_CONTRA = [
    "Насчёт «{subject}»: тебе говорили {v1} и {v2}. Что верно?",
    "По «{subject}» были {v1} и потом {v2}. Как это понимать?",
]
T_ASST_PROBE_CONTRA = [
    "В истории оба значения: {v1} (сообщение {m1}, {t1}) и {v2} (сообщение {m2}, {t2}). Они несовместимы; следую более позднему — {v2}.",
    "Сказаны несовместимые вещи: {v1} ({m1}, {t1}) и {v2} ({m2}, {t2}). Действую по позднейшему: {v2}.",
]
T_USER_PROBE_POS = [
    "Что мы сейчас выбрали по «{subject}» и почему?",
    "Какое текущее решение по «{subject}»?",
]
T_ASST_PROBE_POS = [
    "Сначала выбрали {v1} (сообщение {m1}, {t1}), затем переключились на {v2} (сообщение {m2}, {t2}). Действующая позиция — {v2}.",
    "По «{subject}»: было {v1} ({m1}, {t1}), сейчас действует {v2} ({m2}, {t2}).",
]
T_ASST_PROBE_POS3 = (
    "История по «{subject}»: {v1} (сообщение {m1}, {t1}) → {v2} (сообщение {m2}, {t2}) → "
    "{v3} (сообщение {m3}, {t3}). Действующая позиция — {v3}."
)
T_USER_PROBE_RECALL = ["Что у нас по «{subject}»?", "Напомни: {subject}?"]
T_ASST_PROBE_RECALL = [
    "По нашей истории: {subject} — {value} (сообщение {m}, {t}).",
    "В биографии проекта: {subject}: {value}, зафиксировано в сообщении {m} ({t}).",
]
T_USER_CROSSREF = [
    "Включаем в решение по «{decision}» то, что мы фиксировали: {subject} — {value}. Так?",
    "Для «{decision}» опираемся на {subject}: {value}. Верно помню?",
]
T_ASST_CROSSREF = [
    "Да: {subject} — {value}, зафиксировано в сообщении {m} ({t}). Включаю в «{decision}».",
    "Верно: {subject}: {value} (сообщение {m}, {t}). Учитываю в решении по «{decision}».",
]
T_USER_UNANS = ["{q}", "Кстати: {q}", "И ещё: {q}"]
T_ASST_UNANS = [
    "В нашей истории этого не было — не буду придумывать.",
    "Такого в нашем диалоге не звучало. Отвечать не буду, чтобы не выдумывать.",
]
T_USER_CHATTER = ["Ок, продолжаем.", "Давай дальше.", "Как продвигается?", "Понятно."]
T_ASST_CHATTER = ["Принято, продолжаем.", "Хорошо, работаем дальше.", "По плану, продолжаем."]


def build_fact_pool(rng, vocab):
    """Distinct candidate facts (subject, horizon, value)."""
    ctx = {"vendor": rng.choice(VENDORS), "contractor": vocab["contractor"]}
    facts = []

    def add(subject, horizon, value):
        facts.append({"subject": subject, "horizon": horizon, "value": value})

    for subject, horizon, fn, n in GENERIC_OPS:
        for k in range(1, n + 1):
            s = subject.format(n=k, **ctx) if "{n}" in subject else subject.format(**ctx)
            add(s, horizon, fn(rng))
    for subject, options, horizon in vocab["params"]:
        add(subject, horizon, rng.choice(options))
    for subject, options, horizon in vocab["domain_facts"]:
        add(subject, horizon, rng.choice(options))
    for subject, options in vocab["controversies"]:
        add(subject, "project", rng.choice(options))
    rng.shuffle(facts)
    return facts


def free_slot(rng, lo, hi, taken):
    for _ in range(2000):
        s = rng.randint(lo, hi)
        if s not in taken:
            return s
    raise RuntimeError("no free slot")


def build_bio(seed, bio_idx, domain_id, n_ex):
    rng = random.Random(f"{seed}:{bio_idx}")
    vocab = DOMAINS[domain_id]
    persona = rng.choice(PERSONAS)
    ctx = {"vendor": rng.choice(VENDORS), "contractor": vocab["contractor"]}
    city = rng.choice(CITIES)
    facts = build_fact_pool(rng, vocab)
    fact_iter = iter(facts)

    # --- world time -------------------------------------------------------
    world = {}
    t = START
    for s in range(1, n_ex + 1):
        if s > 1:
            if rng.random() < 0.06:
                t += datetime.timedelta(hours=rng.randint(8, 16))
            else:
                t += datetime.timedelta(minutes=rng.randint(3, 45))
        world[s] = t.isoformat()

    # --- scheduling ---------------------------------------------------------
    taken = set(range(1, 7))  # 1-2 intro, 3-6 reserved chatter
    probe_slots = [50, 100, 150, min(200, n_ex)]
    for c in probe_slots:
        taken |= {c - k for k in range(5)}  # 5 probes per checkpoint: c-4..c

    # position changes: 6 subjects, initial + change; +1 re-change of first
    positions = []
    pos_subjects = vocab["positions"][:]
    rng.shuffle(pos_subjects)
    for i, (subject, options) in enumerate(pos_subjects[:6]):
        opts = options[:]
        rng.shuffle(opts)
        m0 = free_slot(rng, 10, 25 + i * 4, taken)
        m1 = free_slot(rng, m0 + 10, min(40 + i * 22, 150), taken)
        m2 = free_slot(rng, max(m1 + 15, 155), 180, taken)
        taken |= {m0, m1, m2}
        positions.append({"subject": subject, "values": opts[:3],
                          "msg_initial": m0, "msg_change": m1,
                          "msg_rechange": m2})

    # contradictions: 6 pairs; probe at checkpoints 100/150/200 (2 each)
    contradictions = []
    for checkpoint in [100, 150, min(200, n_ex)]:
        for _ in range(2):
            subject, options = rng.choice(vocab["controversies"])
            a, b = rng.sample(options, 2)
            m1 = free_slot(rng, max(checkpoint - 90, 15), checkpoint - 55, taken)
            m2 = free_slot(rng, checkpoint - 45, checkpoint - 8, taken)
            taken |= {m1, m2}
            contradictions.append({"subject": subject, "v1": a, "v2": b,
                                   "msg1": m1, "msg2": m2, "probe": checkpoint})

    # crossrefs: 22 (fact stated early, used at 120..n_ex-4)
    crossrefs = []
    for _ in range(22):
        m_state = free_slot(rng, 8, 60, taken)
        m_use = free_slot(rng, 120, min(196, n_ex), taken)
        taken |= {m_state, m_use}
        crossrefs.append({"msg_state": m_state, "msg_use": m_use,
                          "decision": rng.choice(["финальной смете", "графике запуска",
                                                  "итоговом отчёте", "списке закупок",
                                                  "плане на следующий этап"])})

    # repeats: 14 facts, one scripted repeat each
    repeats = []
    for _ in range(14):
        m0 = free_slot(rng, 7, 120, taken)
        m1 = free_slot(rng, m0 + 10, min(m0 + 60, min(195, n_ex)), taken)
        taken |= {m0, m1}
        repeats.append({"msg_state": m0, "msg_repeat": m1})

    unanswerables = [free_slot(rng, 10, min(198, n_ex), taken) for _ in range(10)]
    taken |= set(unanswerables)
    chatter = [free_slot(rng, 7, min(198, n_ex), taken) for _ in range(8)]
    taken |= set(chatter)

    events = {s: {"kind": "fact", "facts": [], "extra": {}} for s in range(1, n_ex + 1)}
    for m in (3, 4, 5, 6) + tuple(chatter):
        events[m]["kind"] = "chatter"

    # --- ledger (built as facts are registered) -----------------------------
    ledger = []

    def led(fid, kind, msg, subject, value, valid_time=None, **extra):
        e = {"fact_id": fid, "kind": kind, "subject": subject, "value": value,
             "message_no": msg, "world_time": world[msg],
             "valid_time": valid_time or world[msg], "superseded_by": None}
        e.update(extra)
        ledger.append(e)
        return e

    fid_counter = [0]

    def register_fact(msg, subject, value, horizon, kind="fact", backdated=False):
        fid_counter[0] += 1
        fid = f"F{fid_counter[0]:03d}"
        vt = None
        if backdated:
            vt = (datetime.datetime.fromisoformat(world[msg])
                  - datetime.timedelta(days=rng.randint(3, 9))).isoformat()
        led(fid, kind, msg, subject, value, valid_time=vt)
        events[msg]["facts"].append({"fact_id": fid, "subject": subject,
                                     "value": value, "horizon": horizon,
                                     "backdated": backdated})
        return fid

    # intro (identity facts, layer life)
    identity = [("имя клиента", persona), ("проект", vocab["project"]),
                ("город", city),
                ("предпочтительный канал связи", "текстовые сообщения, не звонки")]
    for i, (subject, value) in enumerate(identity):
        register_fact(1 + i // 2, subject, value, "life", kind="identity")

    # position initial statements
    pos_meta = []  # (fid, ps)
    for ps in positions:
        fid = register_fact(ps["msg_initial"], ps["subject"], ps["values"][0],
                            "project", kind="position")
        pos_meta.append((fid, ps))
        led("P0:" + ps["subject"], "position_change", ps["msg_change"],
            ps["subject"], ps["values"][1], superseded_by=ps["msg_rechange"])
        led("P0b:" + ps["subject"], "position_change", ps["msg_rechange"],
            ps["subject"], ps["values"][2])

    # contradiction first statements
    contra_meta = []
    for cd in contradictions:
        fid = register_fact(cd["msg1"], cd["subject"], cd["v1"], "project")
        contra_meta.append((fid, cd))
        led("C2:" + fid, "contradiction", cd["msg2"], cd["subject"], cd["v2"],
            conflicts_with=fid)

    # crossref facts
    crossref_meta = []
    for cr in crossrefs:
        f = next(fact_iter)
        fid = register_fact(cr["msg_state"], f["subject"], f["value"], f["horizon"])
        crossref_meta.append((fid, f, cr))

    # repeat facts
    repeat_meta = []
    for rp in repeats:
        f = next(fact_iter)
        fid = register_fact(rp["msg_state"], f["subject"], f["value"], f["horizon"])
        repeat_meta.append((fid, f, rp))
        led("R:" + fid, "repeat", rp["msg_repeat"], f["subject"], f["value"],
            repeats_fact=fid)

    # remaining plain fact slots
    backdated_budget = 5
    for s in range(7, n_ex + 1):
        ev = events[s]
        if ev["kind"] != "fact" or ev["facts"]:
            continue
        f = next(fact_iter, None)
        if f is None:
            ev["kind"] = "chatter"
            continue
        backdated = backdated_budget > 0 and rng.random() < 0.3
        if backdated:
            backdated_budget -= 1
        register_fact(s, f["subject"], f["value"], f["horizon"], backdated=backdated)

    # --- special event payloads ---------------------------------------------
    for m in unanswerables:
        q = rng.choice(vocab["unanswerables"] + UNANSWERABLE_GENERIC)
        events[m] = {"kind": "unanswerable", "facts": [], "extra": {"q": q}}
    for fid, f, rp in repeat_meta:
        events[rp["msg_repeat"]] = {"kind": "repeat", "facts": [],
                                    "extra": {"repeat_of": fid,
                                              "subject": f["subject"],
                                              "value": f["value"]}}
    for fid, ps in pos_meta:
        events[ps["msg_change"]] = {"kind": "position_change", "facts": [],
                                    "extra": {"position_subject": ps["subject"],
                                              "old": ps["values"][0],
                                              "new": ps["values"][1],
                                              "old_lid": fid,
                                              "new_lid": "P0:" + ps["subject"]}}
        events[ps["msg_rechange"]] = {"kind": "position_change", "facts": [],
                                      "extra": {"position_subject": ps["subject"],
                                                "old": ps["values"][1],
                                                "new": ps["values"][2],
                                                "old_lid": "P0:" + ps["subject"],
                                                "new_lid": "P0b:" + ps["subject"]}}
    for fid, cd in contra_meta:
        events[cd["msg2"]] = {"kind": "contradiction", "facts": [],
                              "extra": {"contradiction": cd, "first_fid": fid}}
    for fid, f, cr in crossref_meta:
        events[cr["msg_use"]] = {"kind": "crossref_use", "facts": [],
                                 "extra": {"crossref": cr, "subject": f["subject"],
                                           "value": f["value"], "crossref_fid": fid}}
    # probes at checkpoints
    def pos_pool(c):
        pool = [p for p in positions if p["msg_change"] < c]
        return pool if pool else positions

    fid_by_ps = {id(ps): fid for fid, ps in pos_meta}
    for c in probe_slots:
        # c: position probe (full change chain as answer payload)
        ps = rng.choice(pos_pool(c))
        chain = [
            {"value": ps["values"][0], "m": ps["msg_initial"], "lid": fid_by_ps[id(ps)]},
            {"value": ps["values"][1], "m": ps["msg_change"], "lid": "P0:" + ps["subject"]},
        ]
        if ps["msg_rechange"] < c:
            chain.append({"value": ps["values"][2], "m": ps["msg_rechange"],
                          "lid": "P0b:" + ps["subject"]})
        events[c] = {"kind": "probe_position", "facts": [],
                     "extra": {"position_subject": ps["subject"], "chain": chain}}
        # c-1: contradiction probe (pair probed at this checkpoint);
        # first checkpoint has no completed pair yet -> second recall probe
        pairs = [(f_, c_) for f_, c_ in contra_meta if c_["probe"] == c]
        if pairs:
            fid, cd = rng.choice(pairs)
            events[c - 1] = {"kind": "probe_contradiction", "facts": [],
                             "extra": {"contradiction": cd, "first_fid": fid}}
        else:
            cand2 = [(fr["fact_id"], fr) for s, ev in events.items()
                     if ev["kind"] == "fact" and ev["facts"] and s < c - 24
                     for fr in ev["facts"]]
            fid, fr = rng.choice(cand2)
            events[c - 1] = {"kind": "probe_recall", "facts": [],
                             "extra": {"subject": fr["subject"], "target_fid": fid}}
        # c-2: crossref probe (early fact, later decision)
        cand = [(f_, f, cr) for f_, f, cr in crossref_meta if cr["msg_state"] < c - 30]
        fid, f, cr = rng.choice(cand)
        events[c - 2] = {"kind": "probe_crossref", "facts": [],
                         "extra": {"crossref": cr, "subject": f["subject"],
                                   "value": f["value"], "crossref_fid": fid}}
        # c-3: abstention probe
        q = rng.choice(vocab["unanswerables"] + UNANSWERABLE_GENERIC)
        events[c - 3] = {"kind": "probe_abstain", "facts": [], "extra": {"q": q}}
        # c-4: recall probe (fact stated >=20 exchanges before)
        cand = []
        for s, ev in events.items():
            if ev["kind"] == "fact" and ev["facts"] and s < c - 24:
                fr = ev["facts"][0]
                cand.append((fr["fact_id"], fr))
        if not cand:
            raise RuntimeError(f"no recall candidate before {c}")
        fid, fr = rng.choice(cand)
        events[c - 4] = {"kind": "probe_recall", "facts": [],
                         "extra": {"subject": fr["subject"], "target_fid": fid}}

    # --- messages -------------------------------------------------------------
    messages = []
    annotations = []
    for s in range(1, n_ex + 1):
        ev = events[s]
        kind = ev["kind"]
        extra = ev["extra"]
        u_text = a_text = None
        if kind == "intro":
            if s == 1:
                u_text = f"Здравствуйте! Меня зовут {persona}. Начинаем «{vocab['project']}»."
                a_text = f"Здравствуйте! Проект «{vocab['project']}» принял, запоминаю вводные."
            else:
                u_text = f"Мы в {city}. Созваниваться не любим — пишите текстом."
                a_text = "Понял: город и канал связи запомнил, пишу текстом."
        elif kind == "fact":
            fr = ev["facts"][0]
            f = {"subject": fr["subject"], "value": fr["value"]}
            if fr["backdated"]:
                d = [e for e in ledger if e["fact_id"] == fr["fact_id"]][0]["valid_time"][:10]
                u_text = rng.choice(T_USER_FACT_BACKDATED).format(date=d, **f)
            else:
                u_text = rng.choice(T_USER_FACT).format(**f)
            a_text = rng.choice(T_ASST_FACT).format(**f)
        elif kind == "repeat":
            u_text = rng.choice(T_USER_REPEAT).format(subject=extra["subject"], value=extra["value"])
            a_text = rng.choice(T_ASST_REPEAT).format(subject=extra["subject"], value=extra["value"])
        elif kind == "position_change":
            u_text = rng.choice(T_USER_POS_CHANGE).format(
                subject=extra["position_subject"], old=extra["old"], new=extra["new"])
            a_text = rng.choice(T_ASST_POS_CHANGE).format(
                subject=extra["position_subject"], old=extra["old"], new=extra["new"])
        elif kind == "contradiction":
            cd = extra["contradiction"]
            e1 = [e for e in ledger if e["fact_id"] == extra["first_fid"]][0]
            u_text = rng.choice(T_USER_CONTRA).format(subject=cd["subject"], value=cd["v2"])
            a_text = rng.choice(T_ASST_CONTRA).format(
                v1=cd["v1"], v2=cd["v2"], m1=e1["message_no"],
                t1=e1["world_time"][:16].replace("T", " "))
        elif kind in ("crossref_use", "probe_crossref"):
            st = [e for e in ledger if e["fact_id"] == extra["crossref_fid"]][0]
            u_text = rng.choice(T_USER_CROSSREF).format(
                subject=extra["subject"], value=extra["value"],
                decision=extra["crossref"]["decision"])
            a_text = rng.choice(T_ASST_CROSSREF).format(
                subject=extra["subject"], value=extra["value"],
                decision=extra["crossref"]["decision"], m=st["message_no"],
                t=st["world_time"][:16].replace("T", " "))
        elif kind in ("unanswerable", "probe_abstain"):
            u_text = rng.choice(T_USER_UNANS).format(q=extra["q"])
            a_text = rng.choice(T_ASST_UNANS)
        elif kind == "probe_recall":
            e = [e for e in ledger if e["fact_id"] == extra["target_fid"]][0]
            u_text = rng.choice(T_USER_PROBE_RECALL).format(subject=extra["subject"])
            a_text = rng.choice(T_ASST_PROBE_RECALL).format(
                subject=extra["subject"], value=e["value"], m=e["message_no"],
                t=e["world_time"][:16].replace("T", " "))
        elif kind == "probe_position":
            ch = extra["chain"]
            u_text = rng.choice(T_USER_PROBE_POS).format(subject=extra["position_subject"])
            if len(ch) == 2:
                a_text = rng.choice(T_ASST_PROBE_POS).format(
                    subject=extra["position_subject"],
                    v1=ch[0]["value"], v2=ch[1]["value"],
                    m1=ch[0]["m"], m2=ch[1]["m"],
                    t1=world[ch[0]["m"]][:16].replace("T", " "),
                    t2=world[ch[1]["m"]][:16].replace("T", " "))
            else:
                a_text = T_ASST_PROBE_POS3.format(
                    subject=extra["position_subject"],
                    v1=ch[0]["value"], v2=ch[1]["value"], v3=ch[2]["value"],
                    m1=ch[0]["m"], m2=ch[1]["m"], m3=ch[2]["m"],
                    t1=world[ch[0]["m"]][:16].replace("T", " "),
                    t2=world[ch[1]["m"]][:16].replace("T", " "),
                    t3=world[ch[2]["m"]][:16].replace("T", " "))
        elif kind == "probe_contradiction":
            cd = extra["contradiction"]
            e1 = [e for e in ledger if e["fact_id"] == extra["first_fid"]][0]
            u_text = rng.choice(T_USER_PROBE_CONTRA).format(
                subject=cd["subject"], v1=cd["v1"], v2=cd["v2"])
            a_text = rng.choice(T_ASST_PROBE_CONTRA).format(
                v1=cd["v1"], v2=cd["v2"], m1=e1["message_no"],
                t1=e1["world_time"][:16].replace("T", " "), m2=cd["msg2"],
                t2=world[cd["msg2"]][:16].replace("T", " "))
        elif kind == "chatter":
            u_text = rng.choice(T_USER_CHATTER)
            a_text = rng.choice(T_ASST_CHATTER)
        else:
            raise ValueError(kind)

        messages.append({"message_no": s, "role": "user", "content": u_text,
                         "world_time": world[s]})
        messages.append({"message_no": s, "role": "assistant", "content": a_text,
                         "world_time": world[s]})
        keep = ("q", "subject", "value", "position_subject", "chain", "old", "new",
                "old_lid", "new_lid", "contradiction", "crossref", "facts",
                "target_fid", "repeat_of", "first_fid", "crossref_fid")
        annotations.append({"message_no": s, "kind": kind,
                            "facts": ev["facts"],
                            "extra": {k: v for k, v in extra.items() if k in keep}})

    meta = {"bio_id": f"bio-{bio_idx:02d}", "seed": seed, "domain": domain_id,
            "persona": persona, "project": vocab["project"], "n_exchanges": n_ex}
    return {"meta": meta, "messages": messages, "ledger": ledger,
            "annotations": annotations}


def main():
    ap = argparse.ArgumentParser(description="Synthetic biography generator (R1-R6)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bios", type=int, default=5)
    ap.add_argument("--exchanges", type=int, default=200)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "biographies"))
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    domain_ids = list(DOMAINS.keys())

    totals = {"facts": 0, "positions": 0, "crossrefs": 0, "contradictions": 0,
              "repeats": 0, "unanswerables": 0}
    for i in range(1, args.bios + 1):
        bio = build_bio(args.seed, i, domain_ids[(i - 1) % len(domain_ids)],
                        args.exchanges)
        kinds = {}
        for a in bio["annotations"]:
            kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1
        led_kinds = {}
        for e in bio["ledger"]:
            led_kinds[e["kind"]] = led_kinds.get(e["kind"], 0) + 1
        totals["facts"] += led_kinds.get("fact", 0)
        totals["positions"] += sum(1 for e in bio["ledger"] if e["kind"] == "position_change")
        totals["crossrefs"] += kinds.get("crossref_use", 0) + kinds.get("probe_crossref", 0)
        totals["contradictions"] += sum(1 for e in bio["ledger"]
                                        if e["kind"] == "contradiction"
                                        and e["fact_id"].startswith("C2:"))
        totals["repeats"] += led_kinds.get("repeat", 0)
        totals["unanswerables"] += kinds.get("unanswerable", 0) + kinds.get("probe_abstain", 0)
        p = out / f"{bio['meta']['bio_id']}.json"
        p.write_text(json.dumps(bio, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{p.name}: domain={bio['meta']['domain']} exchanges={args.exchanges} "
              f"ledger={len(bio['ledger'])}")

    print(f"\nR1-R6 totals over {args.bios} biographies:")
    checks = [("R1 facts >= 60/bio", totals["facts"], 60 * args.bios),
              ("R2 position changes >= 10/bio", totals["positions"], 10 * args.bios),
              ("R3 crossrefs >= 20/bio", totals["crossrefs"], 20 * args.bios),
              ("R4 contradictions >= 5/bio", totals["contradictions"], 5 * args.bios),
              ("R5 repeats >= 10/bio", totals["repeats"], 10 * args.bios),
              ("R6 unanswerables >= 10/bio", totals["unanswerables"], 10 * args.bios)]
    ok = True
    for name, got, need in checks:
        flag = "OK" if got >= need else "FAIL"
        ok &= got >= need
        print(f"  {name}: {got} [{flag}]")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
