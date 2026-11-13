"""Сборка схемы: данные (data/cosmology.yaml + data/lang/*.yaml) + движок (src/engine.html) -> dist/cosmology.html.

  python tools/build.py

Запускать после каждой правки данных. Готовый файл самодостаточен: открывается без сервера,
его можно скачать или встроить на сайт.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from cosmo import load

r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'validate.py')],
                   capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
if r.returncode:
    print(r.stdout); sys.exit('Сборка остановлена: в данных ошибки (см. выше).')

d = load()
d.pop('orphans', None)
data = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = open('src/engine.html', encoding='utf-8').read().replace('/*@COSMO@*/', 'window.COSMO=' + data + ';')
os.makedirs('dist', exist_ok=True)
open('dist/cosmology.html', 'w', encoding='utf-8').write(html)
print(f"Готово: dist/cosmology.html ({len(html) // 1024} КБ) — личностей {len(d['persons'])}, "
      f"связей {len(d['links'])}, языки: {', '.join(d['meta']['languages'])}")
