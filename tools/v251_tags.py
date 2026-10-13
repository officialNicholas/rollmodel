"""v251: a name tag over each rival in a match: its rank on a little shield in its colour, then its name. Sharp up close, fading away with
distance; gone while that rival hides in a basin, is knocked out or stands behind a wall, and outside of play. One tag per rival, however
many there are (ready for players in place of CPUs: a tag reads nameOf(D) and rankOf(D)). CPU rivals get a rank near yours each match."""

def apply(s):
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
        s = s.replace(old, new)

    # the layer: over the game view, under the HUD and the edge pointers
    rep('<div class="vig" id="vig"></div>', '<div class="vig" id="vig"></div>\n  <div class="ntags" id="ntags" aria-hidden="true"></div>')

    rep('.mworld .world::after{transition:opacity .2s}\n</style>', '.mworld .world::after{transition:opacity .2s}\n'
        '/* v251: a rival\'s name tag: its rank on a shield in its colour, its name on a dark plate, a small point down at it */\n'
        '.ntags{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}\n'
        '.ntag{position:absolute;left:0;top:0;display:flex;align-items:center;padding-bottom:6px;transform-origin:50% 100%;will-change:transform,opacity;--tc:#2E9BFF}\n'
        '.ntag::after{content:"";position:absolute;left:50%;bottom:1px;margin-left:-4.5px;border-style:solid;border-width:5px 4.5px 0;border-color:rgba(23,19,32,.84) transparent transparent}\n'
        '.ntr{position:relative;z-index:1;flex:none;width:21px;height:25px;margin-right:-8px;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.35))}\n'
        '.ntr svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}\n'
        '.ntsh{fill:var(--tc);stroke:#171320;stroke-width:4.5;stroke-linejoin:round}\n'
        '.ntr b{position:absolute;left:0;right:0;top:7px;text-align:center;font:400 10.5px/1 var(--font-display);color:#fff;font-variant-numeric:tabular-nums;text-shadow:0 1px 0 #171320,1px 0 0 #171320,-1px 0 0 #171320,0 -1px 0 #171320}\n'
        '.ntn{max-width:112px;height:18px;box-sizing:border-box;padding:0 9px 0 13px;border-radius:0 9px 9px 0;background:rgba(23,19,32,.84);box-shadow:inset 0 -2px 0 var(--tc);font:900 11px/18px var(--font-head);letter-spacing:.05em;text-transform:uppercase;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n'
        '</style>')

    # CPU rivals: a rank near yours, a little under on gentle critics and over on harsh ones, rolled with their names
    rep('NAMES[2] = pool[Math.floor(Math.random() * pool.length)]; }', 'NAMES[2] = pool[Math.floor(Math.random() * pool.length)]; rollRivalRanks(); }')

    rep('function foePointer(fpEl, H, on) {',
        "// v251: rivals' name tags. Each rides just over its rival's head, in screen space so it stays crisp and the same size to read: full up\n"
        "// close, fading out between NTAG_NEAR and NTAG_FAR metres from the camera and shrinking a touch on the way. It's gone while its rival\n"
        "// hides in a basin, is knocked out or is behind a wall (no reading positions through walls), and outside of play\n"
        "const rankOf = D => D === P ? repOf(store.xp || 0).lv : Math.max(1, D.rank | 0);\n"
        "function rollRivalRanks() { const me = repOf(store.xp || 0).lv, [a, b] = diff === 'easy' ? [-2, 0] : diff === 'hard' ? [1, 3] : [-1, 1];\n"
        "  for (const D of [H, H2]) D.rank = clamp(me + a + Math.floor(Math.random() * (b - a + 1)), 1, 99); }\n"
        "const NTAG_NEAR = 17, NTAG_FAR = 25, NTAG_SH = 'M23 2.6 43 8.6V29c0 11.4-9 18.6-20 22.6C12 47.6 3 40.4 3 29V8.6z', ntagsEl = $('ntags'), ntags = new Map(), ntagV = new THREE.Vector3();\n"
        "function ntagFor(D) {\n"
        "  let t = ntags.get(D); if (t) return t;\n"
        "  const el = document.createElement('div'); el.className = 'ntag'; el.hidden = true;\n"
        "  el.innerHTML = '<span class=\"ntr\"><svg viewBox=\"0 0 46 54\"><path class=\"ntsh\" d=\"' + NTAG_SH + '\"/><path d=\"M9.5 12.4 23 8.3l13.5 4.1\" fill=\"none\" stroke=\"#fff\" stroke-width=\"3\" stroke-linecap=\"round\" opacity=\".75\"/></svg><b></b></span><span class=\"ntn\"></span>';\n"
        "  ntagsEl.appendChild(el); t = { el, rk: el.querySelector('b'), nm: el.querySelector('.ntn'), k: 0, see: 1, seeAt: -9, name: null, rank: -1, col: '', z: -1, x: 0, y: 0, d: 0, w: 0, h: 30, sc: 1, oy: 0, oyT: 0 }; ntags.set(D, t); return t;\n"
        "}\n"
        "function ntagTick(rdt) {\n"
        "  const playing = state === 'play', fs = playing ? foes(P) : [], cp = camera.position, vis = [];\n"
        "  if (playing) { camera.updateMatrixWorld(); for (const D of fs) { ntagFor(D); if (!D.rank) rollRivalRanks(); } }\n"
        "  for (const [D, t] of ntags) {\n"
        "    const L = D.look, mine = playing && fs.includes(D) && !!L; let want = 0, at = false;\n"
        "    if (mine) {\n"
        "      const top = D.y + charTall(L.wearing) * (L.V ? L.V.gk : 1) + NTAG_UP; ntagV.set(D.x, top, D.z).project(camera);\n"
        "      if (ntagV.z < 1 && Math.abs(ntagV.x) < 1.2 && Math.abs(ntagV.y) < 1.2 && Number.isFinite(ntagV.x + ntagV.y)) { at = true; t.x = (ntagV.x * 0.5 + 0.5) * viewW; t.y = (0.5 - ntagV.y * 0.5) * viewH; t.d = Math.hypot(D.x - cp.x, top - cp.y, D.z - cp.z); }\n"
        "      if (at && D.st === 'play' && !kcam && !kof && L.drop.visible) {\n"
        "        if (clock - t.seeAt > 0.15 || t.k <= 0) { t.seeAt = clock; t.see = losClear(cp.x, cp.y, cp.z, D.x, D.y + 0.35, D.z) ? 1 : 0; }\n"
        "        want = t.see * (1 - smoothstep(NTAG_NEAR, NTAG_FAR, t.d));\n"
        "      }\n"
        "    }\n"
        "    if (!at) t.k = 0; else t.k += (want - t.k) * Math.min(1, rdt * (want > t.k ? 7 : 12)); if (want <= 0 && t.k < 0.02) t.k = 0;\n"
        "    D.tagK = t.k;\n"
        "    if (t.k <= 0) { if (!t.el.hidden) t.el.hidden = true; t.oy = t.oyT = 0; continue; }\n"
        "    if (t.el.hidden) t.el.hidden = false;\n"
        "    const nm = nameOf(D), rk = rankOf(D), col = TEAMS[D.team].css;\n"
        "    if (t.name !== nm || t.rank !== rk) { t.name = nm; t.rank = rk; t.nm.textContent = nm; t.rk.textContent = rk; t.w = 0; }\n"
        "    if (t.col !== col) { t.col = col; t.el.style.setProperty('--tc', col); }\n"
        "    if (!t.w) { t.w = t.el.offsetWidth || 90; t.h = t.el.offsetHeight || 30; } // (measured once per name)\n"
        "    t.sc = 1 - 0.16 * smoothstep(10, NTAG_FAR, t.d); vis.push(t);\n"
        "  }\n"
        "  // two tags crossing: the farther one steps up over the nearer, so both read\n"
        "  vis.sort((a, b) => a.d - b.d);\n"
        "  for (let i = 0; i < vis.length; i++) { const a = vis[i], aw = a.w * a.sc, ah = (a.h - 5) * a.sc; let lift = 0;\n"
        "    for (let n = 0; n < 3; n++) { let moved = false; for (let j = 0; j < i; j++) { const b = vis[j], bb = b.y - b.oyT, bt = bb - (b.h - 5) * b.sc;\n"
        "      if (Math.abs(a.x - b.x) < (aw + b.w * b.sc) / 2 + 4 && a.y - lift > bt - 2 && a.y - lift - ah < bb && a.y - bt + 3 > lift) { lift = a.y - bt + 3; moved = true; } } if (!moved) break; }\n"
        "    a.oyT = lift; }\n"
        "  for (const t of vis) {\n"
        "    t.oy += (t.oyT - t.oy) * Math.min(1, rdt * 14);\n"
        "    const z = 1000 - Math.min(999, Math.round(t.d * 10)); if (t.z !== z) { t.z = z; t.el.style.zIndex = z; } // (the nearer one on top)\n"
        "    t.el.style.opacity = t.k.toFixed(3);\n"
        "    t.el.style.transform = 'translate3d(' + t.x.toFixed(1) + 'px,' + (t.y - t.oy).toFixed(1) + 'px,0) translate(-50%,-100%) scale(' + t.sc.toFixed(3) + ')';\n"
        "  }\n"
        "}\n"
        "const NTAG_UP = 0.1, NTAG_LIFT = 0.55; // (how far over the head the tag's point sits; how far the '!' rises while a tag shows)\n"
        "function foePointer(fpEl, H, on) {")

    rep('updateSpeedLines(dt, spK); updateSlamBtn(); threatUI();', 'updateSpeedLines(dt, spK); updateSlamBtn(); threatUI(); ntagTick(rdt);')
    # the '!' a rival shows when it spots you rises over its tag
    rep('L.mark.position.set(D.x, D.y + 1.6 - (1 - pop) * 0.35, D.z);', 'L.mark.position.set(D.x, D.y + 1.6 + (D.tagK || 0) * NTAG_LIFT - (1 - pop) * 0.35, D.z);')
    return s
