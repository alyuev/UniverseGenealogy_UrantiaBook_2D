"""Проверка data/cosmology.yaml.

  python tools/validate.py [data/cosmology.yaml] [--all]

1) Структура: уникальные id, каждая личность размещена ровно в одном ряду,
   связи ссылаются на существующие личности/блоки, классы и группы определены.
2) Термины: русское имя ищется в тексте перевода Фонда (book.db), английское — в оригинале.
   Имя вида «Михаилы — Сыны-Создатели (…)» проверяется по частям. Окончания слов допускаются любые.
   Если термин в тексте записан иначе, можно задать поле terms: { ru: [...], en: [...] } у личности.
3) Ссылки refs: «документ» или «документ:раздел» должны существовать в book.db.
"""
import os, re, sqlite3, sys
sys.path.insert(0, os.path.dirname(__file__))
from cosmo import load

BOOK = r'D:/Develop/KU/SmartSearch-Release/Программа/BilingualTextAnalyzer/library/urantia/book.db'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
SHOW_ALL = '--all' in sys.argv
path = args[0] if args else 'data/cosmology.yaml'
d = load(path)
errors, warns = [], []
for lg, s, k in d['orphans']: warns.append(f"lang/{lg}.yaml: {s}.{k} нет в структуре")

# ---------- 1. структура ----------
persons, units, placed = d.get('persons', {}), {}, {}
def walk(lst, parent):
    for u in lst:
        if u['id'] in units or u['id'] in persons: errors.append(f"повтор id: {u['id']}")
        units[u['id']] = u
        for item in u.get('content', []):
            if isinstance(item, list):
                for pid in item:
                    if str(pid).startswith('~'):
                        if pid[1:] not in persons: errors.append(f"блок {u['id']}: тень {pid} — нет личности")
                        elif pid in placed: errors.append(f"тень {pid} размещена дважды")
                        else: placed[pid] = u['id']
                    elif pid not in persons: errors.append(f"блок {u['id']}: нет личности {pid}")
                    elif pid in placed: errors.append(f"{pid} размещён дважды ({placed[pid]}, {u['id']})")
                    else: placed[pid] = u['id']
            else: walk([item], u['id'])
walk(d.get('units', []), None)
for pid, p in persons.items():
    if pid not in placed: errors.append(f"{pid} не размещён ни в одном блоке")
    if p.get('class') not in d.get('classes', {}): errors.append(f"{pid}: неизвестный класс {p.get('class')}")
    if p.get('pair') and (persons.get(p['pair']) or {}).get('pair') != pid: errors.append(f"{pid}: пара {p.get('pair')} не взаимна")
    if p.get('serves') and '~' + pid not in placed: warns.append(f"{pid}: есть serves, но нет тени ~{pid} в блоках")
    for g in p.get('groups', []):
        if g not in d.get('groups', {}): errors.append(f"{pid}: неизвестная группа {g}")
    for g in p.get('func', []):
        if g not in d.get('functions', {}): errors.append(f"{pid}: неизвестная функция {g}")
    for lang in d['meta']['languages']:
        if not (p.get('name') or {}).get(lang): warns.append(f"{pid}: нет имени на «{lang}»")
        if not (p.get('desc') or {}).get(lang): warns.append(f"{pid}: нет описания на «{lang}»")
for l in d.get('links', []):
    for end in l[:2]:
        if str(end).startswith('~') and end in placed: continue
        if end not in persons and not (end in units and units[end].get('linkable')):
            errors.append(f"связь {l}: «{end}» не найден или не может быть концом связи")
    if len(l) > 2 and l[2] not in ('origin', 'service', 'ascent'): errors.append(f"связь {l}: неизвестный тип")

# ---------- 2-3. термины и ссылки по book.db ----------
db = sqlite3.connect(BOOK)
RU = ' '.join(r[0] for r in db.execute('select ru from paragraphs')).lower().replace('ё', 'е')
EN = ' '.join(r[0] for r in db.execute('select en from paragraphs')).lower().replace('’', "'")
SECTIONS = {(r[0], r[1]) for r in db.execute('select paper, section from sections')}
PAPERS = {r[0] for r in db.execute('select paper from papers')}

def parts(name):  # «А — Б (В)» -> [А, Б, В]
    return [x.strip() for x in re.split(r'\s+—\s+|[()]', name) if x.strip()]

def found(term, text, ru):
    words = re.findall(r"[\w'’-]+", term.lower().replace('ё', 'е').replace('’', "'"))
    if not words: return True
    if ru:  # основа слова + любое окончание
        pat = r'[\s,]+'.join(re.escape(w[:max(3, len(w) - 2)] if len(w) > 4 else w) + r'[\w-]*' for w in words)
    else:   # английский: допускаем множественное число и притяжательные формы
        pat = r'\s+'.join(re.escape(w[:-1] if w.endswith('s') and len(w) > 4 else w) + r"[\w'’]*" for w in words)
    return re.search(r'(?<![\w-])' + pat, text) is not None

rows = []
for pid, p in persons.items():
    terms = p.get('terms') or {}
    for lang, text in (('ru', RU), ('en', EN)):
        cand = terms.get(lang) or parts((p.get('name') or {}).get(lang, ''))
        miss = [t for t in cand if not found(t, text, lang == 'ru')]
        if miss: rows.append((pid, lang, '; '.join(miss)))
    for ref in p.get('refs', []):
        m = re.fullmatch(r'(\d+)(?::(\d+))?', str(ref))
        if not m: errors.append(f"{pid}: ссылка «{ref}» не в формате док[:раздел]")
        elif m.group(2) is None and int(m.group(1)) not in PAPERS: errors.append(f"{pid}: нет документа {ref}")
        elif m.group(2) is not None and (int(m.group(1)), int(m.group(2))) not in SECTIONS: errors.append(f"{pid}: нет раздела {ref}")

# ---------- отчёт ----------
print(f"Файл: {path}\nЛичностей: {len(persons)}, блоков: {len(units)}, связей: {len(d.get('links', []))}")
print(f"\nОшибки структуры: {len(errors)}"); [print('  ✗', e) for e in errors]
print(f"\nТермины, не найденные в тексте книги: {len(rows)}")
for pid, lang, miss in rows: print(f"  ? {pid:12} [{lang}] {miss}")
print(f"\nПредупреждения: {len(warns)}")
for x in (warns if SHOW_ALL else warns[:10]): print('  ·', x)
if len(warns) > 10 and not SHOW_ALL: print(f'  … ещё {len(warns) - 10} (--all)')
sys.exit(1 if errors else 0)
