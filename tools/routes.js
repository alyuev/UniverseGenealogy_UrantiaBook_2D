// Прокладка линий при сборке: тот же маршрутизатор, что в движке (src/engine.html), запускается в Node без браузера.
// Вход (stdin): данные схемы в JSON. Выход (stdout): {язык: [точки каждой линии, в порядке links]}.
// Ширина подписей блоков здесь не измеряется, а оценивается по числу букв (с запасом) — см. labelW в движке.
const fs = require('fs'), path = require('path');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(path.join(__dirname, '..', 'src', 'engine.html'), 'utf8');
const a = html.indexOf('/* ===================== ДАННЫЕ'), b = html.indexOf('/* ===================== ОТРИСОВКА');
if (a < 0 || b < a) throw new Error('routes.js: в src/engine.html не найдены разделы ДАННЫЕ … ОТРИСОВКА');
// Заглушки браузера: разделы «данные — геометрия — языки — маршрутизатор» почти не трогают страницу.
const stub = () => ({ textContent: '', classList: { toggle() {} } });
const env = {
  window: { COSMO: data }, document: { body: stub(), getElementById: stub }, location: { search: '' },
  navigator: { language: 'en' }, localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
};
const run = new Function(...Object.keys(env), html.slice(a, b) +
  ';return langs=>Object.fromEntries(langs.map(l=>{LANG=l;routeAll();return[l,edges.map(e=>e.pts)]}))');
process.stdout.write(JSON.stringify(run(...Object.values(env))(data.meta.languages)));
