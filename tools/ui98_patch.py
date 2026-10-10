#!/usr/bin/env python3
"""A frame that throws no longer stops the game: the loop carries on, the error is written on screen for a while and kept for Settings to show. The lesson's first step ends the moment you have steered and jumped, with a few seconds at full speed before the next. On top of ui97_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui97_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function frame(t) {\n  if (!booted) { booted = true;", "function frameBody(t) {\n  if (!booted) { booted = true;")
rep("  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();\n  requestAnimationFrame(frame);\n}",
    "  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();\n}\n// a frame that throws must not take the game with it: the loop goes on, and the error is put on screen and kept for Settings\nlet frameErrN = 0;\nfunction frameErr(e) {\n  frameErrN++; try { console.error(e); } catch (x) {}\n  if (frameErrN > 3) return; const m = String(e && e.message || e).slice(0, 160), at = ((e && e.stack) || '').split('\\n').slice(0, 3).join(' ').replace(/https?:\\S*?\\//g, '').slice(0, 220);\n  try { const el = $('errLine'); el.textContent = 'Error ' + frameErrN + ': ' + m + ' ' + at; el.hidden = false; clearTimeout(frameErr.t); frameErr.t = setTimeout(() => { el.hidden = true; }, 20000); } catch (x) {}\n  try { store.lastErr = m + ' | ' + at; save(); } catch (x) {}\n}\nfunction frame(t) { try { frameBody(t); } catch (e) { frameErr(e); } requestAnimationFrame(frame); }\nwindow.addEventListener('error', ev => { if (ev && (ev.error || ev.message)) frameErr(ev.error || ev.message); });")
rep('<div class="tutslow" id="tutSlow" aria-hidden="true"></div>', '<div class="tutslow" id="tutSlow" aria-hidden="true"></div><p class="errline" id="errLine" hidden></p>')
rep("      <div class=\"sgrp\">\n        <p class=\"lhead\">Tutorial</p>\n        <button class=\"btn sm\" id=\"tutReplay\" type=\"button\">Replay the tutorial</button>\n      </div>",
    "      <div class=\"sgrp\">\n        <p class=\"lhead\">Tutorial</p>\n        <button class=\"btn sm\" id=\"tutReplay\" type=\"button\">Replay the tutorial</button>\n        <p class=\"gnote\" id=\"lastErr\"></p>\n      </div>")
rep("function paintSettings() {", "function paintSettings() { try { $('lastErr').textContent = store.lastErr ? 'Last error: ' + store.lastErr : ''; } catch (e) {}")
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + ".errline{position:absolute;left:8px;right:8px;bottom:max(8px,env(safe-area-inset-bottom));z-index:99;margin:0;padding:6px 10px;background:rgba(23,19,32,.88);color:#FFD86B;font:600 11px/1.3 ui-monospace,Menlo,monospace;border-radius:6px;pointer-events:none;word-break:break-all}\n#lastErr{font:600 10px/1.3 ui-monospace,Menlo,monospace;word-break:break-all;opacity:.8}\n" + s[j:]
rep('<p class="ver">Version 167</p>', '<p class="ver">Version 168</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui98 ok', n0, '->', len(s))
