// cq probe: serve game/ on :8765, then: node tools/cq/shot.mjs <page.html> <outdir> [w h]
import { createRequire } from 'module'; const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const [page_, out, W = '390', H = '844'] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] }).catch(() => chromium.launch());
const p = await b.newPage({ viewport: { width: +W, height: +H }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
await p.route('**/*supabase.co/**', r => r.abort()); await p.route('**/*fly.dev/**', r => r.abort());
const errs = []; p.on('pageerror', e => errs.push('PAGEERR ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
if (!process.env.FRESH) await p.addInitScript(o => { try { if (!localStorage.getItem('paint-world-red.v1')) localStorage.setItem('paint-world-red.v1', JSON.stringify({ introDone: 1, name: 'Zqtest_1', runs: 12, orient: o.o, tut: { ph: 'done', m3: 1, modes: 1, strokes: 1, comms: 1, trySd: 1 }, gfx: o.g || undefined })); } catch (e) {} }, { o: +W > +H ? 'land' : 'port', g: process.env.GFX });
await p.goto('http://localhost:8765/' + page_); const ev = s => p.evaluate(s => window.__T.ev(s), s);
const shot = async n => { await p.screenshot({ path: `${out}/${n}.jpg`, quality: 70, timeout: 180000 }); console.log('shot', n, await ev('state + " " + (typeof CQB !== "undefined" && CQB ? (CQB.boss ? CQB.boss.state || "" : "") : "")').catch(e => e.message)); };
await p.waitForFunction(() => window.__T, null, { timeout: 60000 }); await p.waitForTimeout(6000); await shot('00_boot');
for (const s of (process.env.STEPS || '').split(' ~ ').filter(Boolean)) {
  const [k, v] = [s[0], s.slice(2)];
  if (k === 'e') console.log('ev', v.slice(0, 60), '=>', await ev(v).catch(e => 'ERR ' + e.message));
  else if (k === 'f') console.log('ff', v, await ev(`(() => { const R = renderFrame; renderFrame = () => {}; let t = last; try { for (let i = 0; i < ${+v} * 20; i++) { t += 50; frameBody(t); } } finally { renderFrame = R; last = performance.now(); } return state + ' ' + (CQB && CQB.boss ? CQB.boss.state : ''); })()`).catch(e => 'ERR ' + e.message));
  else if (k === 't') { const [x, y] = v.split(',').map(Number); await p.mouse.click(x, y); }
  else if (k === 'w') await p.waitForTimeout(+v);
  else if (k === 's') await shot(v);
  else if (k === 'c') await p.click(v).catch(e => console.log('click fail', v, e.message.slice(0, 80)));
}
console.log(errs.slice(0, 20).join('\n') || 'no errors'); await b.close();
