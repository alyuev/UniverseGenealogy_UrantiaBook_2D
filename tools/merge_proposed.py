"""Вливает data/proposed_persons.json (новые личности) в данные.

  python tools/merge_proposed.py [data/proposed_persons.json]

Каждая запись: id, ru, en, class, origin, groups, unit, serves?, serves_ru?, serves_en?, parents, refs, desc_ru, desc_en.
Новые личности добавляются рядами (не больше 6 в ряду) в свой блок; тени (~id) — в блок служения.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from cosmo import load
from write_data import save

ROW = 6   # ширина самых глубоких блоков вмещает 6 карточек
P = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'data/proposed_persons.json', encoding='utf-8'))
d = load(); d.pop('orphans', None)
units = {}
def walk(us):
    for u in us:
        units[u['id']] = u; walk([x for x in u['content'] if isinstance(x, dict)])
walk(d['units'])

skipped, place, ghosts = [], {}, {}
for p in P:
    pid = p['id']
    if pid in d['persons'] or pid in units: skipped.append(pid + ' (уже есть)'); continue
    if p['unit'] not in units: skipped.append(f"{pid} (нет блока {p['unit']})"); continue
    e = {'class': p['class'], 'origin': p['origin'], 'groups': p.get('groups', []), 'refs': p.get('refs', []),
         'name': {'ru': p['ru'], 'en': p['en']}, 'desc': {'ru': p.get('desc_ru', ''), 'en': p.get('desc_en', '')}}
    if p.get('serves') and p['serves'] in units and p['serves'] != p['unit']:
        e['serves'] = {'ru': p.get('serves_ru', ''), 'en': p.get('serves_en', '')}
        ghosts.setdefault(p['serves'], []).append('~' + pid)
    d['persons'][pid] = e
    place.setdefault(p['unit'], []).append(pid)

def add_rows(uid, ids):
    c = units[uid]['content']
    last = max([i for i, k in enumerate(c) if isinstance(k, list)], default=-1)
    rows = [ids[i:i + ROW] for i in range(0, len(ids), ROW)]
    c[last + 1:last + 1] = rows
for uid, ids in place.items(): add_rows(uid, ids)
for uid, ids in ghosts.items(): add_rows(uid, ids)

# связи: от родителя; если у родителя есть тень в блоке потомка — от тени
ghost_unit = {}
for u in units.values():
    for k in u['content']:
        if isinstance(k, list):
            for x in k:
                if str(x).startswith('~'): ghost_unit[x[1:]] = u['id']
added = {p['id'] for p in P} & set(d['persons'])
have = {(l[0], l[1]) for l in d['links']}
for p in P:
    if p['id'] not in added: continue
    for par in p.get('parents', []):
        src = '~' + par if ghost_unit.get(par) == p['unit'] else par
        if par not in d['persons'] and not (par in units and units[par].get('linkable')): skipped.append(f"связь {par}->{p['id']} (нет {par})"); continue
        if (src, p['id']) not in have: d['links'].append([src, p['id']]); have.add((src, p['id']))

save(d)
print(f"добавлено личностей: {len(added)}, теней: {sum(map(len, ghosts.values()))}, всего связей: {len(d['links'])}")
for s in skipped: print('  пропущено:', s)
