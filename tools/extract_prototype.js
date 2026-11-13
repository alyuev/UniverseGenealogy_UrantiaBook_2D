// Одноразовый перенос данных из prototype/index.html в JSON (дальше -> YAML).
// node tools/extract_prototype.js prototype/index.html out.json
const fs = require('fs');
const [, , src, out] = process.argv;
const html = fs.readFileSync(src, 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
const cut = (from, to) => { const a = js.indexOf(from), b = js.indexOf(to, a); if (a < 0 || b < 0) throw new Error(from); return js.slice(a, b); };
const code = [
  cut('const CATS=', '/* Дерево'),
  cut('const C1=', 'const P=['),
  cut('const P=[', '/* Класс по происхождению'),
  cut('const OCLS=', 'const persons='),
  cut('const E=s=>', '/* ====================='),
  cut('const DESC_EN=', 'const qs='),
].join('\n') + '\n;({CATS,TREE,P,OCLS,OCLS_OF,edges,DESC_EN,UNIT_EN,CAT_EN})';
const d = eval(code);
fs.writeFileSync(out, JSON.stringify(d), 'utf8');
console.log('ok', d.P.length, d.edges.length);
