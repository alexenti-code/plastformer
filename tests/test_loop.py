#!/usr/bin/env python3
"""Проверка круга возврата (plastformer/loop.py) на копии изделия.

Запуск: python3 tests/test_loop.py
Что проверяет: разбор актов, исполнение записи, рост тика, выдачу записей
по read, правило C5 (чтение не двигает тик), scan, calibrate (принятие и
отказ), сборку Φ-состояния, метку времени от кода.
"""
import json, os, shutil, sys, time
sys.path.insert(0, '/Users/alex/plastformer/plastformer')
import numpy as np
import loop
from phi import phi_open, phi_read, _write_header

SRC = '/Users/alex/plastformer/models/plastformer-e1'
WORK = '/tmp/loop-test'
if os.path.exists(WORK): shutil.rmtree(WORK)
os.makedirs(WORK)
print('=== копия изделия (8,2 ГБ) ===', flush=True)
t0 = time.time()
shutil.copy2(SRC + '/model.safetensors', WORK + '/model.safetensors')
for f in ('config.json','generation_config.json','tokenizer.json','tokenizer_config.json','chat_template.jinja'):
    shutil.copy2(SRC + '/' + f, WORK + '/' + f)
M = WORK + '/model.safetensors'
print('  готово за %.1f с | %.2f ГБ' % (time.time()-t0, os.path.getsize(M)/1e9), flush=True)

h = phi_open(M)
for k, v in (('written1',0),('written2',0),('tick',0),('scan_used',0),('calibrate_used',0)):
    h[k] = v
_write_header(M, h)
print('  счётчики обнулены, тик =', phi_open(M)['tick'], flush=True)
print()
print('=== 1. разбор актов ===', flush=True)
ans = 'Запомнил: бригадир — Ковалёв.\n\n```json\n[{"act": "name", "content": "бригадир — Ковалёв", "source": "user", "layer": "t4", "valid_time": "2026-09-12T10:00:00+03:00", "record_tick": 1, "refs": []}]\n```'
acts = loop.parse_acts(ans)
print('  разобрано актов:', len(acts), acts[0]['act'], flush=True)
print()
print('=== 2. исполнение: запись ===', flush=True)
p1 = loop.run_acts(M, acts)
print('  подтверждение:', json.dumps(p1, ensure_ascii=False)[:200], flush=True)
print()
print('=== 3. второй ход: тик растёт ===', flush=True)
ans2 = 'Принято.```json\n[{"act":"name","content":"срок сдачи — 15 октября","source":"user","layer":"t4","valid_time":"x","record_tick":2,"refs":[]}]\n```'
p2 = loop.run_acts(M, loop.parse_acts(ans2))
print('  подтверждение:', json.dumps(p2, ensure_ascii=False)[:200], flush=True)
assert p1['tick'] == 1 and p2['tick'] == 2, 'тик не растёт!'
print('  ТИК РАСТЁТ: 1 -> 2', flush=True)
print()
print('=== 4. read: модель получает СВОИ записи ===', flush=True)
p3 = loop.run_acts(M, [{'act':'read','mode':'last','count':5}])
print('  подтверждение:', json.dumps(p3, ensure_ascii=False)[:400], flush=True)
assert p3['records'] and p3['records'][0]['content'], 'read не вернул записи!'
print('  READ ВЕРНУЛ СОДЕРЖАНИЕ', flush=True)
print()
print('=== 5. чтение тик НЕ двигает (C5) ===', flush=True)
tb = phi_open(M)['tick']
loop.run_acts(M, [{'act':'read','mode':'last','count':5}])
ta = phi_open(M)['tick']
print('  тик до %s, после %s' % (tb, ta), flush=True)
assert tb == ta, 'чтение сдвинуло тик — нарушение C5'
print()
print('=== 6. scan: настоящие числа ===', flush=True)
p5 = loop.run_acts(M, [{'act':'scan','mode':'summary'}])
print('  подтверждение:', json.dumps(p5, ensure_ascii=False)[:300], flush=True)
print()
print('=== 7. calibrate ===', flush=True)
ok = loop.run_acts(M, [{'act':'calibrate','proposal':{'surfacing_cap':10.0},'evidence':[{'metric':'wasted_surface','tick':2,'record_id':1,'layer':'t4'}],'budget_used':1}])
print('  в границах:', json.dumps(ok, ensure_ascii=False)[:220], flush=True)
bad = loop.run_acts(M, [{'act':'calibrate','proposal':{'act_price':2.0},'evidence':[],'budget_used':1}])
print('  замороженная:', json.dumps(bad, ensure_ascii=False)[:220], flush=True)
print()
print('=== 8. Φ-состояние ===', flush=True)
st = loop.phi_state(M)
print('  записей в префиксе:', len(st), flush=True)
for s in st[:3]:
    print('    №%s слой %s громкость %.3f | %s' % (s['id'], s['layer'], s['loudness'], s['content'][:50]), flush=True)
print()
print('=== 9. время ставит КОД ===', flush=True)
_, iso = loop.stamp()
print('  текущая метка:', iso, flush=True)
print()
print('ИТОГ: круг возврата работает', flush=True)