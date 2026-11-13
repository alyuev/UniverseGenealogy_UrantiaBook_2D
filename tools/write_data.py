"""Запись данных обратно в файлы: структура data/cosmology.yaml + тексты data/lang/<язык>.yaml.

  from write_data import save
  save(d)   # d — как возвращает cosmo.load(): тексты в виде { ru: …, en: … }
"""
import json, os, re

def q(s):
    s = str(s)
    if s == '' or re.search(r'[:#\[\]{},&*!|>\'"%@`]', s) or s[0] in '-?~' or s.strip() != s or re.fullmatch(r'[\d.]+|true|false|null|yes|no', s, re.I):
        return json.dumps(s, ensure_ascii=False)
    return s

def lst(a): return '[' + ', '.join(q(x) for x in a) + ']'
def row(a): return '[' + ', '.join(str(x) for x in a) + ']'   # id и ~id без кавычек

def save(d, root='data'):
    langs = d['meta']['languages']
    o = []; w = o.append
    w('# Космология Книги Урантии — структура (без текстов).')
    w('# Тексты (имена, описания) — в data/lang/<язык>.yaml. Новый язык = скопировать en.yaml и перевести.')
    w('# Проверка: python tools/validate.py   Сборка: python tools/build.py')
    w('')
    w('meta:')
    w(f"  version: {q(str(d['meta'].get('version', '0.1')))}")
    w('  base_language: en   # если перевода нет, показывается en, затем ru')
    w('')
    w('# Класс по происхождению: ровно один у личности, задаёт тон заливки карточки.')
    w('classes:')
    for k, c in d['classes'].items(): w(f"  {k}: {{ color: {q(c['color'])} }}")
    w('')
    w('# Группы по роли: у личности может быть несколько; полоски сверху карточки.')
    w('groups:')
    for k, c in d['groups'].items(): w(f"  {k}: {{ color: {q(c['color'])} }}")
    w('')
    w('# Функции (служебные обязанности): у личности может быть несколько (поле func); фильтр в легенде.')
    w('functions:')
    for k, c in d.get('functions', {}).items(): w(f"  {k}: {{ color: {q(c['color'])} }}")
    w('')
    w('# Дерево административных единиц. content сверху вниз:')
    w('#   [a, b, c] — ряд личностей;  - id: … — вложенный блок (столица первой).')
    w('#   ~a — «тень» личности a: место, где она служит (сама она стоит на уровне происхождения).')
    w('units:')
    def unit(u, ind):
        p = ' ' * ind
        w(f"{p}- id: {u['id']}")
        w(f"{p}  color: {q(u['color'])}")
        if u.get('width'): w(f"{p}  width: {u['width']}")
        if u.get('linkable'): w(f"{p}  linkable: true")
        if u.get('beside'): w(f"{p}  beside: true")
        if u.get('refs'): w(f"{p}  refs: {lst(u['refs'])}")
        w(f"{p}  content:")
        for k in u['content']:
            if isinstance(k, list): w(f"{p}    - {row(k)}")
            else: unit(k, ind + 4)
    for u in d['units']: unit(u, 2)
    w('')
    w('# Личности. pair — партнёр (общий контур пары). class — класс происхождения; origin — точки пиктограммы.')
    w('persons:')
    for pid, p in d['persons'].items():
        extra = (f", func: {row(p['func'])}" if p.get('func') else '') + (f", pair: {p['pair']}" if p.get('pair') else '') + (f", fuse: {row(p['fuse'])}" if p.get('fuse') else '')
        w(f"  {pid}: {{ class: {p['class']}, origin: {q(p['origin'] or '')}, groups: {row(p.get('groups', []))}, refs: {lst(p.get('refs', []))}{extra} }}")
    w('')
    w('# Связи: [откуда, куда, тип]. Тип по умолчанию origin; service — служение; ascent — восхождение. ~a — от тени.')
    w('links:')
    for l in d['links']: w(f"  - {row(l)}")
    open(os.path.join(root, 'cosmology.yaml'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')

    NAMES = {'ru': 'Русский', 'en': 'English'}
    for lg in langs:
        o = []; w = o.append
        g = lambda obj, f: ((obj.get(f) or {}).get(lg))
        w(f'# Тексты на языке «{lg}». Ключи — id из data/cosmology.yaml.')
        if lg == 'ru': w('# Термины — по переводу Фонда Урантии.')
        w('')
        w(f'language: {{ code: {lg}, name: {NAMES.get(lg, lg)} }}')
        w('')
        w('classes:')
        for k, c in d['classes'].items(): w(f"  {k}: {q(g(c, 'name') or '')}")
        w('')
        w('groups:')
        for k, c in d['groups'].items(): w(f"  {k}: {q(g(c, 'name') or '')}")
        w('')
        w('functions:')
        for k, c in d.get('functions', {}).items(): w(f"  {k}: {q(g(c, 'name') or '')}")
        w('')
        w('units:')
        def un(u):
            w(f"  {u['id']}:")
            w(f"    name: {q(g(u, 'name') or '')}")
            if g(u, 'desc'): w(f"    desc: {q(g(u, 'desc'))}")
            for k in u['content']:
                if isinstance(k, dict): un(k)
        for u in d['units']: un(u)
        w('')
        w('# serves — подпись к месту служения; there — имя на месте служения (если иное).')
        w('persons:')
        for pid, p in d['persons'].items():
            w(f"  {pid}:")
            w(f"    name: {q(g(p, 'name') or '')}")
            for f in ('desc', 'serves', 'there'):
                if g(p, f): w(f"    {f}: {q(g(p, f))}")
            if g(p, 'terms'): w(f"    terms: {lst(g(p, 'terms'))}")
        open(os.path.join(root, 'lang', f'{lg}.yaml'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
