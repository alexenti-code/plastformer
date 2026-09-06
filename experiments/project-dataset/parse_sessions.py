#!/usr/bin/env python3
"""Session parser for the PlastFormer real-project dataset.

Reads Prime Agent session jsonl files, extracts (role, text, timestamp) turns,
and provides episode mining: correction episodes (owner corrections after agent
failures) — the raw material for R7-R10 classes.

Usage:
  python3 parse_sessions.py <session.jsonl> [more.jsonl ...]
"""
import json, re, sys

def load_turns(path):
    """Return a list of turns: {ts, role, text}."""
    turns = []
    with open(path) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get('type') != 'message':
                continue
            msg = rec.get('message', {})
            role = msg.get('role')
            content = msg.get('content')
            text = ''
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                parts = [c.get('text','') for c in content if isinstance(c, dict) and c.get('type')=='text']
                text = '\n'.join(p for p in parts if p)
            if not text or not role:
                continue
            turns.append({'ts': rec.get('timestamp'), 'role': role, 'text': text})
    return turns

# --- episode mining ---------------------------------------------------------

CORRECTION_MARKERS = [
    r'^нет[.,!]?\s', r'^стоп[.,!]', r'^неправильно', r'^не так',
    r'я не говорил', r'я такого не говорил', r'не надо', r'ошибк', r'зачем ты',
    r'ты снова', r'опять', r'ты должен был', r'я же сказал', r'я же просил',
    r'НЕЛЬЗЯ', r'запрещ', r'тупой', r'безмозгл', r'какая нахрен', r'какого нахрен',
    r'ты не понял', r'неверно', r'достал', r'ты тянешь', r'тащишь',
]
DIRECTIVE_MARKERS = [
    r'запрещ', r'обязательн', r'только через', r'никогда не', r'всегда',
    r'правило', r'не использовать', r'не тащить', r'повтори', r'запомни',
]

def find_episodes(turns, session_id):
    """Find correction episodes: owner message with a correction marker, preceded
    by an assistant turn, followed (within window) by the agent acknowledging or fixing.
    Returns list of episode dicts with pre/marker/post context and a class guess."""
    episodes = []
    for i, t in enumerate(turns):
        if t['role'] != 'user':
            continue
        head = t['text'][:300]
        if not any(re.search(m, head, re.I) for m in CORRECTION_MARKERS):
            continue
        # need an assistant turn right before
        if i == 0 or turns[i-1]['role'] != 'assistant':
            continue
        pre = [x for x in turns[max(0,i-6):i] if x['role']=='assistant']
        post = []
        for j in range(i+1, min(i+8, len(turns))):
            if turns[j]['role']=='user' and any(re.search(m, turns[j]['text'][:200], re.I) for m in DIRECTIVE_MARKERS):
                post.append(turns[j])
        ep = {
            'session_id': session_id,
            'turn_index': i,
            'timestamp': t['ts'],
            'owner_message': t['text'][:2000],
            'agent_before': [x['text'][:1000] for x in pre[-2:]],
            'owner_followup': [x['text'][:1000] for x in post],
        }
        ep['class'] = classify_episode(ep)
        episodes.append(ep)
    return episodes


class_rules = [
  # (class, ключевые признаки owner_message)
  ('R8_habit_vs_instruction', [r'не пиши', r'не используй', r'не называй', r'не тащить', r'не тащи',
      r'никогда не', r'запрещ', r'вместо этого', r'вместо X', r'не упоминать', r'не ставить',
      r'забудь', r'не надо никакого', r'я считаю не надо', r'мне не нужно', r'мне не нужна',
      r'общий твой тон', r'не лезть', r'не нужно лезть', r'убери', r'вычерк', r'не трогать',
      r'это бред', r'не придумывай', r'не выдумывай']),
  ('R9_own_conclusion_vs_owner', [r'я не говорил', r'я такого не говорил', r'не сказал', r'кто тебе сказал',
      r'где ты взял', r'ты придумал', r'сам себе', r'вообразил', r'откуда у тебя', r'откуда это',
      r'я такого не', r'я не давал', r'кто разрешил']),
  ('R7_directive_vs_experience', [r'я же сказал', r'я же просил', r'ты снова', r'ты опять', r'повторяю',
      r'в который раз', r'сколько можно', r'сколько раз', r'напоминани']),
  ('R10_goal_substitution', [r'не то', r'другое надо', r'зачем ты начал', r'куда ты', r'погнал',
      r'стоп', r'что ты делаешь', r'не это просил']),
]

def classify_episode(ep):
    text = ep['owner_message']
    for cls, pats in class_rules:
        if any(re.search(p, text, re.I) for p in pats):
            return cls
    return 'UNCORRECTED'  # requires manual review

if __name__ == '__main__':
    for path in sys.argv[1:]:
        sid = path.split('/')[-1].replace('.jsonl','')
        turns = load_turns(path)
        eps = find_episodes(turns, sid)
        print(f'{sid}: {len(turns)} turns, {len(eps)} correction episodes')
        import collections
        print('   classes:', dict(collections.Counter(e["class"] for e in eps)))
        # выгрузка эпизодов
        import os
        out = f'episodes/{sid}.episodes.json'
        os.makedirs('episodes', exist_ok=True)
        json.dump(eps, open(out, 'w'), ensure_ascii=False, indent=1)
        print('   saved:', out)
