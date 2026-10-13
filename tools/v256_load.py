"""v256: a quicker start. The character pack (the last thing the loading screen waited for, at 'Hanging the show') is asked for at the
top of the page alongside the menu song and the sound effects, instead of once the game's code has run; and the shaders are compiled
ahead of the warm-up render without blocking where the browser can, so the bar keeps moving through a new last step."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    s = rep(s, "// and the two sheets of sound effects\n",
               "// (v256) and the character pack, the last thing the loading screen waits for: asked for now too, not once the game's code has run\n"
               "window.__axoPre = (() => { try { if (location.protocol === 'file:' || typeof fetch !== 'function' || window.AXO_PACK_BUF) return null; const u = window.AXO_PACK || 'axo-pack-250.txt'; return { u, p: fetch(u).then(r => r.ok ? r.text() : null).catch(() => null) }; } catch (e) { return null; } })();\n"
               "// and the two sheets of sound effects\n")
    s = rep(s, "else { const r = await fetch(url); if (!r.ok) throw new Error('axolotl pack ' + r.status); buf = fromB64(await r.text()); }",
               "else { const pre = window.__axoPre; window.__axoPre = null; const t = pre && pre.u === url ? await pre.p : null; if (t) buf = fromB64(t); else { const r = await fetch(url); if (!r.ok) throw new Error('axolotl pack ' + r.status); buf = fromB64(await r.text()); } } // (v256: the copy asked for at the top of the page)")
    s = rep(s, "let warmQ = 0; const queueWarm = () => { clearTimeout(warmQ); warmQ = setTimeout(warmRender, 30); };",
               "let warmQ = 0, bootWarm = false; const queueWarm = () => { clearTimeout(warmQ); if (bootWarm) warmQ = setTimeout(warmRender, 30); }; // (v256: not while loading: loading warms up once, at its end)")
    s = rep(s, "function warmRender() {",
               "// (v256) the shaders compiled ahead of the warm-up render, without blocking the page where the browser can (the loading bar keeps\n"
               "// moving meanwhile); the warm-up render after finds them ready\n"
               "async function warmCompile() {\n"
               "  if (typeof renderer.compileAsync !== 'function') return;\n"
               "  const hid = []; scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } });\n"
               "  let p = null; try { p = renderer.compileAsync(scene, camera); } catch (e) {} // (every program asked for now; the browser builds them in the background)\n"
               "  for (const o of hid) o.visible = false;\n"
               "  const t0 = performance.now(), par = renderer.extensions.has('KHR_parallel_shader_compile');\n"
               "  try { if (p) await Promise.race([p, new Promise(r => setTimeout(r, 8000))]); } catch (e) {}\n"
               "  if (!par) while (performance.now() - t0 < 700) await new Promise(r => requestAnimationFrame(() => r())); // (no way to ask if they're done: a moment's head start)\n"
               "}\n"
               "function warmRender() {")
    s = rep(s, "await bootStep(0.82, 0.97, 'Hanging the show');\nawait Promise.race([slimeLoad, new Promise(r => setTimeout(r, 12000))]); attachSlimes();\nwarmRender();\nbootTo(1, 1, 0, 'Ready');",
               "await bootStep(0.82, 0.93, 'Hanging the show');\nawait Promise.race([slimeLoad, new Promise(r => setTimeout(r, 12000))]); attachSlimes();\n"
               "bootTo(0.93, 0.99, 3500, 'Lighting the gallery'); await warmCompile(); // (v256)\nwarmRender(); bootWarm = true;\nbootTo(1, 1, 0, 'Ready');")
    return s
