"""Загрузка данных: структура data/cosmology.yaml + тексты data/lang/*.yaml.

  from cosmo import load
  d = load()   # тексты собраны в объекты { ru: …, en: … } на месте name/desc/terms

Новый язык = положить data/lang/<код>.yaml (копия en.yaml с переводом).
"""
import glob, os, yaml

def _y(p): return yaml.safe_load(open(p, encoding='utf-8')) or {}

def load(path='data/cosmology.yaml'):
    d = _y(path)
    langs = {}
    for f in sorted(glob.glob(os.path.join(os.path.dirname(path), 'lang', '*.yaml'))):
        t = _y(f); langs[t['language']['code']] = t
    d.setdefault('meta', {})['languages'] = list(langs)

    def put(obj, sect, key, fields):
        for lg, t in langs.items():
            v = (t.get(sect) or {}).get(key)
            if isinstance(v, str): v = {'name': v}
            for f in fields:
                if v and v.get(f): obj.setdefault(f, {})[lg] = v[f]

    for k, c in d.get('classes', {}).items(): put(c, 'classes', k, ['name'])
    for k, c in d.get('groups', {}).items(): put(c, 'groups', k, ['name'])
    for k, c in d.get('functions', {}).items(): put(c, 'functions', k, ['name'])
    def walk(us):
        for u in us:
            put(u, 'units', u['id'], ['name', 'desc'])
            walk([x for x in u.get('content', []) if isinstance(x, dict)])
    walk(d.get('units', []))
    for pid, p in d.get('persons', {}).items(): put(p, 'persons', pid, ['name', 'aka', 'desc', 'terms', 'serves', 'there', 'stages'])
    e = d.get('energy')
    if e:  # энергетический цикл: тексты стадий и подписи вида
        for st in e['stages']:
            for lg, t in langs.items():
                v = ((t.get('energy') or {}).get('stages') or {}).get(st['id']) or {}
                for f in ('name', 'book', 'desc'):
                    if v.get(f): st.setdefault(f, {})[lg] = v[f]
        e['ui'] = {lg: (t.get('energy') or {}).get('ui') or {} for lg, t in langs.items()}
        m = e.get('matter')
        if m:  # ветвь вещества (42:3)
            tx = {lg: (t.get('energy') or {}).get('matter') or {} for lg, t in langs.items()}
            m['title'] = {lg: v.get('title') for lg, v in tx.items() if v.get('title')}
            m['note'] = {lg: v.get('note') for lg, v in tx.items() if v.get('note')}
            m['items'] = [{'id': i, **{f: {lg: v['items'][i][f] for lg, v in tx.items() if (v.get('items') or {}).get(i, {}).get(f)}
                                       for f in ('name', 'desc')}} for i in m['items']]
    # тексты для id, которых нет в структуре
    d['orphans'] = [(lg, s, k) for lg, t in langs.items() for s in ('classes', 'groups', 'functions', 'persons')
                    for k in (t.get(s) or {}) if k not in d.get(s, {})]
    return d
