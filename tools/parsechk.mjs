import fs from 'fs'; import vm from 'vm';
for (const f of process.argv.slice(2)) { const s = fs.readFileSync(f, 'utf8'); const re = /<script type="module">([\s\S]*?)<\/script>/g; let m, n = 0;
  while ((m = re.exec(s))) { n++; try { new vm.Script('(async()=>{' + m[1] + '\n})', { filename: 'x.js' }); console.log(f, 'module', n, 'ok'); } catch (e) { console.log(f, 'module', n, 'ERR', e.message); } } }
