#!/usr/bin/env python3
"""The locker scene: the wall takes a fresh coat of your ink on a torn diagonal, repainting when you change color; slot cards show what is worn. On top of ui9_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui9_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== the locker: slot cards, one per category, showing what is worn ===== */
.seg.lcats{gap:8px}
.seg.lcats button,.seg.lcats button[aria-selected="true"]{display:grid;justify-items:center;align-content:center;gap:3px;min-height:76px;padding:7px 4px 8px;background:#fff url(art/m_paperbg.webp) center/300px;color:var(--black);border-radius:4px;box-shadow:3px 4px 0 rgba(23,19,32,.18);transform:none;text-shadow:none;font-size:11px}
.seg.lcats button small{font:800 9px/1 var(--font-ui);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.seg.lcats button .lci{width:34px;height:34px;display:grid;place-items:center}
.seg.lcats button .lci svg{width:32px;height:32px}
.seg.lcats button .lci .none{width:20px;height:20px;border-radius:50%;border:2px dashed rgba(23,19,32,.3)}
.seg.lcats button b{display:block;max-width:100%;font:900 11px/1.1 var(--font-head);text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg.lcats button[aria-selected="true"]{background:var(--ink);color:#fff;box-shadow:3px 4px 0 rgba(23,19,32,.3),0 0 0 2px var(--black)}
.seg.lcats button[aria-selected="true"] small{color:rgba(255,255,255,.78)}
.seg.lcats button[aria-selected="true"] .lci .none{border-color:rgba(255,255,255,.6)}
.lcat.fresh::after{top:5px;right:5px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.seg.lcats button,.seg.lcats button[aria-selected="true"]{min-height:56px;padding:4px 3px 5px;gap:2px}.seg.lcats button .lci{width:24px;height:24px}.seg.lcats button .lci svg{width:22px;height:22px}.seg.lcats button b{font-size:9.5px}.seg.lcats button small{font-size:8px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

# the cards' labels come from the markup; their faces are drawn by renderLook
rep('data-cat="head" aria-controls="lookRail" aria-selected="true">Headgear</button>', 'data-cat="head" data-label="Headgear" aria-controls="lookRail" aria-selected="true">Headgear</button>')
rep('data-cat="face" aria-controls="lookRail" aria-selected="false" tabindex="-1">Facial</button>', 'data-cat="face" data-label="Facial" aria-controls="lookRail" aria-selected="false" tabindex="-1">Facial</button>')
rep('data-cat="cloth" aria-controls="lookRail" aria-selected="false" tabindex="-1">Clothing</button>', 'data-cat="cloth" data-label="Clothing" aria-controls="lookRail" aria-selected="false" tabindex="-1">Clothing</button>')
rep("    b.classList.toggle('fresh', WEAR.some(w => w.cat === c && owns(w.id) && fresh.has(w.id))); }",
    """    b.classList.toggle('fresh', WEAR.some(w => w.cat === c && owns(w.id) && fresh.has(w.id)));
    const worn = WEAR.filter(w => w.cat === c && myLook[w.slot] === w.id), w0 = worn[0];
    b.innerHTML = '<small>' + b.dataset.label + '</small><span class="lci">' + (w0 ? '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w0.id] + '</svg>' : '<i class="none"></i>') + '</span><b>' + (w0 ? (worn.length > 1 ? w0.name + ' +' + (worn.length - 1) : w0.name) : 'Nothing on') + '</b>'; }""")

# ---- the wall takes your ink on a torn diagonal; a new color pours in along it ----
rep("const lobbyU = { uTime: { value: 0 }, uDim: { value: 0 }, uCol: { value: new THREE.Color(0xE3122F) },",
    "const lobbyU = { uTime: { value: 0 }, uDim: { value: 0 }, uLook: { value: 0 }, uSweep: { value: 2 }, uCol2: { value: new THREE.Color(0xE3122F) }, uCol: { value: new THREE.Color(0xE3122F) },")
rep("fragmentShader: `uniform mat4 uInvPV; uniform vec3 uCam, uBlob, uCol; uniform vec2 uWallN; uniform float uTime, uDim; varying vec2 vUv;",
    "fragmentShader: `uniform mat4 uInvPV; uniform vec3 uCam, uBlob, uCol, uCol2; uniform vec2 uWallN; uniform float uTime, uDim, uLook, uSweep; varying vec2 vUv;")
rep("    c *= 0.84 + 0.2 * pool; c *= 1.0 - 0.14 * smoothstep(1.5, 4.5, wq.y); c *= 0.88 + 0.12 * smoothstep(0.0, 0.45, wq.y);\n  } else { c = paper * 0.78; }",
    """    c *= 0.84 + 0.2 * pool; c *= 1.0 - 0.14 * smoothstep(1.5, 4.5, wq.y); c *= 0.88 + 0.12 * smoothstep(0.0, 0.45, wq.y);
    if (uLook > 0.001) {
      // the locker: a fresh coat of your ink across the upper left of the wall, its edge torn, a few drips hanging; a new color pours
      // in along the same diagonal when you pick one
      vec2 sp = vec2(vUv.x, 1.0 - vUv.y); float d = sp.x * 0.72 + sp.y * 0.62;
      float tear = (vn(sp * 16.0) - 0.5) * 0.07 + (vn(sp * 48.0 + 3.0) - 0.5) * 0.02;
      float col = floor(sp.x * 26.0), dr = step(0.86, hs(vec2(col, 2.0))) * (0.05 + 0.12 * hs(vec2(col, 5.0))) * smoothstep(0.5, 0.0, abs(fract(sp.x * 26.0) - 0.5) * 2.0 - 0.45);
      float inkK = (1.0 - smoothstep(-0.006, 0.006, d + tear - 0.66 - dr)) * (1.0 - 0.75 * uLook * 0.0);
      float pour = 1.0 - smoothstep(-0.008, 0.008, (d + tear) - uSweep * 1.5);
      vec3 ink = mix(uCol2, uCol, pour); vec3 wet = ink * (0.86 + 0.2 * vn(wq * 1.7 + 11.0)) + 0.1 * smoothstep(0.86, 0.97, vn(wq * 3.1 + uTime * 0.05));
      wet *= 0.82 + 0.22 * pool; float lip = smoothstep(0.03, 0.0, abs(d + tear - 0.66 - dr)) * 0.35;
      c = mix(c, wet + lip, inkK * uLook);
    }
  } else { c = paper * 0.78; }""")
rep("lobbyU.uTime.value = clock; lobbyU.uDim.value = lookOpen ? 0.04 : 0; lobbyU.uCol.value.setHex(TEAMS[0].wet);",
    "lobbyU.uTime.value = clock; lobbyU.uDim.value = lookOpen ? 0.04 : 0; lobbyU.uCol.value.setHex(TEAMS[0].wet); lobbyU.uLook.value += ((lookOpen ? 1 : 0) - lobbyU.uLook.value) * 0.1; if (lobbyU.uSweep.value < 2) lobbyU.uSweep.value = Math.min(2, lobbyU.uSweep.value + 0.028);")
rep("  const same = id === colorId; if (!same) { setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); }",
    "  const same = id === colorId; if (!same) { lobbyU.uCol2.value.setHex(TEAMS[0].wet); setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); if (lookOpen) lobbyU.uSweep.value = 0; }")
rep('<p class="ver">Version 79</p>', '<p class="ver">Version 80</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
