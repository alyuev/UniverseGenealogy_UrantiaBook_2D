# Одноразовый перенос: JSON из прототипа -> data/cosmology.yaml (читаемый человеком формат).
import json, re, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
out = []
w = out.append

def q(s):
    s = str(s)
    if s == '' or re.search(r'[:#\[\]{},&*!|>\'"%@`]', s) or s[0] in '-?' or s.strip() != s or re.fullmatch(r'[\d.]+|true|false|null|yes|no', s, re.I):
        return json.dumps(s, ensure_ascii=False)
    return s

def tr(o):  # {ru:…, en:…} в одну строку
    return '{ ' + ', '.join(f'{k}: {q(v)}' for k, v in o.items() if v) + ' }'

UNIT_EN, CAT_EN, DESC_EN = d['UNIT_EN'], d['CAT_EN'], d['DESC_EN']
w('# Космология Книги Урантии — рабочий файл данных.')
w('# Правило: русские термины — по переводу Фонда Урантии (проверка: python tools/validate.py).')
w('# Любой текст — объект по языкам { ru: …, en: … }. Новый язык = добавить ключ (например de:) где нужно;')
w('# если перевода нет, показывается en, затем ru.')
w('')
w('meta:')
w('  version: 0.1')
w('  languages: [ru, en]')
w('')
w('# Класс по происхождению: ровно один у личности, задаёт тон заливки карточки (в тоне источника).')
w('classes:')
for k, c in d['OCLS'].items():
    w(f"  {k}: {{ color: {q(c['color'])}, name: {tr(c['name'])} }}")
w('')
w('# Группы по роли: у личности может быть несколько; показываются полосками сверху карточки.')
w('groups:')
for k, c in d['CATS'].items():
    w(f"  {k}: {{ color: {q(c['color'])}, name: {tr({'ru': c['name'], 'en': CAT_EN.get(k)})} }}")
w('')
w('# Дерево административных единиц. content идёт сверху вниз:')
w('#   [a, b, c]   — горизонтальный ряд личностей;')
w('#   - id: …     — вложенный блок (столица — первым, ниже — следующий уровень).')
w('units:')
def unit(u, ind):
    p = ' ' * ind
    w(f"{p}- id: {u['id']}")
    w(f"{p}  name: {tr({'ru': u['name'], 'en': UNIT_EN.get(u['id'])})}")
    w(f"{p}  color: {q(u['color'])}")
    if u.get('w'): w(f"{p}  width: {u['w']}")
    if u.get('endpoint'): w(f"{p}  linkable: true   # может быть началом/концом связи")
    if u.get('desc'): w(f"{p}  desc: {tr({'ru': u['desc'], 'en': 'The Paradise Trinity — union of the three Deities. Source of the Trinity Sons.'})}")
    if u.get('ref'): w(f"{p}  refs: [{q(u['ref'])}]")
    w(f"{p}  content:")
    for k in u['kids']:
        if isinstance(k, list): w(f"{p}    - [{', '.join(k)}]")
        else: unit(k, ind + 4)
for u in d['TREE']['kids']: unit(u, 2)
w('')
w('# Личности (классы личностей). origin — точки на пиктограмме: T=Троица, F/S/D=Отец/Сын/Дух, E=эволюционное.')
w('persons:')
for a in d['P']:
    pid, ru, en, _, _, _, origin, cats, ref, desc = a
    w(f'  {pid}:')
    w(f"    name: {tr({'ru': ru, 'en': en})}")
    w(f"    class: {d['OCLS_OF'].get(pid) or ('T' if origin == 'T' else 'E')}")
    w(f"    origin: {origin}")
    w(f"    groups: [{', '.join(cats.split())}]")
    w(f"    refs: [{q(ref)}]")
    w(f"    desc:")
    w(f"      ru: {q(desc)}")
    if DESC_EN.get(pid): w(f"      en: {q(DESC_EN[pid])}")
w('')
w('# Связи: [откуда, куда, тип]. Тип по умолчанию origin (происхождение); service — служение/пребывание; ascent — восхождение.')
w('links:')
for e in d['edges']:
    t = '' if e['type'] == 'origin' else ', ' + e['type']
    w(f"  - [{e['from']}, {e['to']}{t}]")
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written', sys.argv[2])
