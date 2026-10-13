import fs from 'fs'; import vm from 'vm';
for (const f of process.argv.slice(2)) { const s = fs.readFileSync(f, 'utf8'); const re = /<script(?![^>]*\b(?:src=|type="application\/json"))[^>]*>([\s\S]*?)<\/script>/g; let m, n = 0;
  while ((m = re.exec(s))) { n++; if (m[1].length < 50) continue; try { new vm.Script('(async()=>{' + m[1] + '\n})', { filename: 'x.js' }); console.log('script', n, m[1].length, 'ok'); } catch (e) { console.log('script', n, 'ERR', e.message, (e.stack || '').split('\n').slice(0, 3).join(' | ')); } } }
