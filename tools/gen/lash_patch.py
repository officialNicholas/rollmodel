# long girly lashes (a Blank Canvas find): drawn into the face sheets' mask so they follow every expression and blink, inked by the slime's
# shader when worn (not on the eye under a patch); a flutter of blinks when you put them on. Plus the unlock polish: the Customize note
# floats over the scene instead of pushing the sheet up, the code box takes the link's place (and the link goes once everything's
# yours), newly found items carry a dot until you try them, the item's beam no longer washes it out, and its pointer shows a gift
P = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# ---- the face sheets: the new copy from slab/face.js (with the lashes in the mask's blue) ----
f = open(SP + 'slab/face.js').read(); END = '  return { col, msk };\n}'
fa = f.index('const FACE_EYE = '); fb = f.index(END, fa) + len(END)
ga = src.index('const FACE_EYE = '); gb = src.index(END, ga) + len(END)
src = src[:ga] + f[fa:fb] + src[gb:]

# ---- the item: found on the Blank Canvas, worn in its own slot ----
rep("{ id: 'tiara', name: 'Tiara', slot: 'head', stage: 'blank' },", "{ id: 'tiara', name: 'Tiara', slot: 'head', stage: 'blank' }, { id: 'lashes', name: 'Lashes', slot: 'lash', stage: 'blank' },")
rep("mouth: ok(l.mouth, 'mouth'), eye: ok(l.eye, 'eye'), side: ok(l.side, 'side'), neck: ok(l.neck, 'neck') }; })();",
    "mouth: ok(l.mouth, 'mouth'), eye: ok(l.eye, 'eye'), side: ok(l.side, 'side'), neck: ok(l.neck, 'neck'), lash: ok(l.lash, 'lash') }; })();")
rep("LH.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null }; L2.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null };",
    "LH.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null }; L2.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null };")
rep("neck: Math.random() < (head === 'tophat' ? 0.6 : 0.15) ? 'bowtie' : null }; } }",
    "neck: Math.random() < (head === 'tophat' ? 0.6 : 0.15) ? 'bowtie' : null, lash: Math.random() < (head === 'tiara' ? 0.65 : 0.18) ? 'lashes' : null }; } }")
# worn: how much on each eye (they pop on with the other accessories; none on the eye under the patch)
rep("    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = false; }\n",
    "    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = false; }\n    if (SI.setLashes) { const lk = look.lash === 'lashes' && !off ? Math.min(1, pu * 1.4) : 0; SI.setLashes(lk, W.patch.visible ? 0 : lk); }\n")
# the icon, and on the little face in the results
rep("const WEAR_ICON = {\n",
    """const WEAR_ICON = {
  lashes: '<path d="M7.5 25.5c3.2-6.6 15.6-8 21.6-1.6" fill="none" stroke="#D9C8FF" stroke-width="6" stroke-linecap="round"/><ellipse cx="18.4" cy="27.4" rx="9.6" ry="6.4" fill="#FFFFFF" stroke="#D9C8FF" stroke-width="1.4"/><circle cx="19.6" cy="28.2" r="3.6" fill="#231A2B"/><circle cx="20.8" cy="27" r="1.1" fill="#FFFFFF"/>'
    + '<path d="M20.6 19.2c.4-4 2.2-7 5.4-8.6M24.6 20.4c1.4-3.4 4-5.4 7.4-5.8M27.4 22.6c2.2-1.8 4.8-2.4 7.6-1.6" fill="none" stroke="#D9C8FF" stroke-width="4.6" stroke-linecap="round"/>'
    + '<path d="M7.5 25.5c3.2-6.6 15.6-8 21.6-1.6l3.4-3.6" fill="none" stroke="#231A2B" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.6 19.2c.4-4 2.2-7 5.4-8.6M24.6 20.4c1.4-3.4 4-5.4 7.4-5.8M27.4 22.6c2.2-1.8 4.8-2.4 7.6-1.6" fill="none" stroke="#231A2B" stroke-width="2.2" stroke-linecap="round"/>',
""")
rep("  s += '<path d=\"M22 30Q24 31.7 26 30\" fill=\"none\" stroke=\"#1A1030\" stroke-width=\"1.5\" stroke-linecap=\"round\"/>';\n",
    """  s += '<path d="M22 30Q24 31.7 26 30" fill="none" stroke="#1A1030" stroke-width="1.5" stroke-linecap="round"/>';
  if (w.lash === 'lashes') s += '<path d="M17.8 22.6l-2-1.4M18.8 21.9l-1.2-2.1M20.2 21.6l-.3-2.2' + (w.eye === 'patch' ? '' : 'M30.2 22.6l2-1.4M29.2 21.9l1.2-2.1M27.8 21.6l.3-2.2') + '" fill="none" stroke="#1A1030" stroke-width="1.15" stroke-linecap="round"/>';
""")
# putting them on in Customize: it turns to face you and flutters them
rep("else if (w.slot === 'eye' && myLook.eye) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 0.35; };",
    "else if (w.slot === 'eye' && myLook.eye) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 0.35;\n  if (w.slot === 'lash' && myLook.lash) { shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832; setTimeout(() => { if (lookOpen && VP.slime && VP.slime.flutter) VP.slime.flutter(3); }, 380); } };")

# ---- newly found items carry a dot until you try them ----
rep("function unlockItem(id) { if (OWNED.has(id)) return false; OWNED.add(id); store.owned = [...OWNED];",
    "function unlockItem(id) { if (OWNED.has(id)) return false; OWNED.add(id); store.owned = [...OWNED]; store.fresh = [...new Set([...(store.fresh || []), id])];")
rep("""  const wBtn = w => owns(w.id) ? '<button class="lopt" type="button" data-w="' + w.id + '" aria-label="' + w.name + '" title="' + w.name + '" aria-pressed="' + (myLook[w.slot] === w.id) + '">""",
    """  const fresh = new Set(store.fresh || []), wBtn = w => owns(w.id) ? '<button class="lopt' + (fresh.has(w.id) ? ' fresh' : '') + '" type="button" data-w="' + w.id + '" aria-label="' + w.name + (fresh.has(w.id) ? ', new' : '') + '" title="' + w.name + '" aria-pressed="' + (myLook[w.slot] === w.id) + '">""")
rep("  myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook();",
    "  if (store.fresh && store.fresh.includes(w.id)) store.fresh = store.fresh.filter(x => x !== w.id);\n  myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook();")
rep("""  $('lookEyes').textContent = (EYES.find(e => e[0] === myLook.eyes) || EYES[0])[1]; $('lookColor').textContent = colorOf().name;
}""", """  $('lookEyes').textContent = (EYES.find(e => e[0] === myLook.eyes) || EYES[0])[1]; $('lookColor').textContent = colorOf().name;
  $('unlockLink').parentNode.hidden = WEAR.every(w => owns(w.id)); // (nothing left to unlock: no link)
}""")

# ---- the note floats over the scene, just above the sheet (beside it on a wide screen), instead of pushing the sheet up ----
rep('    <p class="lnote" id="lookNote" aria-live="polite"></p>\n    <button class="btn play sm" id="lookDone" type="button">Done</button>', '    <button class="btn play sm" id="lookDone" type="button">Done</button>')
rep('  <section class="newitem" id="newItem" hidden', '  <p class="lnote" id="lookNote" aria-live="polite"></p>\n  <section class="newitem" id="newItem" hidden')
rep("const lookNote = $('lookNote'); let noteT = 0; const note = (t, bad) => { lookNote.textContent = t; lookNote.classList.toggle('bad', !!bad); restartCls(lookNote, 'on');",
    """const lookNote = $('lookNote'); let noteT = 0; const note = (t, bad) => { lookNote.textContent = t; lookNote.classList.toggle('bad', !!bad);
  const r = stage.getBoundingClientRect(), k = lookEl.getBoundingClientRect(), side = endSideMQ.matches;
  lookNote.style.left = (side ? (k.left - r.left) / 2 : k.left - r.left + k.width / 2).toFixed(0) + 'px'; lookNote.style.top = (side ? r.height - 28 : k.top - r.top - 12).toFixed(0) + 'px'; restartCls(lookNote, 'on');""")
rep("function closeLook() { if (!lookOpen) return; lookOpen = false;", "function closeLook() { if (!lookOpen) return; lookOpen = false; lookNote.classList.remove('on'); $('unlockForm').hidden = true; $('unlockLink').hidden = false;")
rep(""".lnote{margin:-2px 0 0;min-height:0;max-height:0;overflow:hidden;font:700 14px/1.35 var(--font-ui);color:var(--gold);text-align:center;text-wrap:balance;transition:max-height .25s}
.lnote.on{max-height:60px}
.lnote.bad{color:#FF8C9E}""",
""".lnote{position:absolute;z-index:5;left:50%;top:0;margin:0;box-sizing:border-box;width:max-content;max-width:min(340px,calc(100% - 32px));padding:10px 16px;border-radius:16px;background:var(--plum);border:3px solid var(--line);box-shadow:0 4px 0 var(--line),0 12px 28px rgba(6,2,16,.45);font:700 14px/1.35 var(--font-ui);color:var(--gold);text-align:center;text-wrap:balance;pointer-events:none;opacity:0;transform:translate(-50%,calc(-100% + 10px)) scale(.94);transition:opacity .18s,transform .3s cubic-bezier(.2,1.5,.4,1)}
.lnote.on{opacity:1;transform:translate(-50%,-100%)}
.lnote.bad{color:#FF8C9E}
.lopt.fresh{position:relative}
.lopt.fresh::after{content:"";position:absolute;top:6px;right:6px;width:10px;height:10px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 2.5px var(--plum),0 0 10px 2px rgba(255,216,107,.6)}""")
# the code box takes the link's place
rep("$('unlockLink').addEventListener('click', () => { AU.init(); AU.ui(); const f = $('unlockForm'); f.hidden = !f.hidden; if (!f.hidden) setTimeout(() => $('unlockCode').focus(), 30); });",
    "$('unlockLink').addEventListener('click', () => { AU.init(); AU.ui(); $('unlockLink').hidden = true; $('unlockForm').hidden = false; setTimeout(() => $('unlockCode').focus(), 30); });")
rep("for (const w of WEAR) OWNED.add(w.id); store.owned = [...OWNED]; save(); $('unlockCode').value = ''; $('unlockForm').hidden = true; renderLook();",
    "for (const w of WEAR) OWNED.add(w.id); store.owned = [...OWNED]; save(); $('unlockCode').value = ''; $('unlockForm').hidden = true; $('unlockLink').hidden = false; renderLook();")

# ---- the item on the stage: a beam that glows at its edges (not over the gift), and a gift on its pointer ----
rep("""  vertexShader: 'varying vec2 vU; void main(){ vU = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform float uT; varying vec2 vU; void main(){ float k = (1.0 - vU.y) * (1.0 - vU.y) * (0.75 + 0.25 * sin(vU.x * 37.7 + uT * 3.0)) * (0.8 + 0.2 * sin(uT * 4.0)); gl_FragColor = vec4(vec3(1.0, 0.86, 0.45) * k * 0.55, 1.0); }' }));""",
"""  vertexShader: 'varying vec2 vU; varying vec3 vN, vV; void main(){ vU = uv; vec4 mv = modelViewMatrix * vec4(position, 1.0); vN = normalize(normalMatrix * normal); vV = -mv.xyz; gl_Position = projectionMatrix * mv; }',
  fragmentShader: 'uniform float uT; varying vec2 vU; varying vec3 vN, vV; void main(){ float e = pow(1.0 - abs(dot(normalize(vN), normalize(vV))), 1.7), y = vU.y; float k = (1.0 - y) * (1.0 - y) * smoothstep(0.0, 0.05, y) * (0.72 + 0.28 * sin(vU.x * 37.7 + uT * 3.0 - y * 24.0)) * (0.85 + 0.15 * sin(uT * 4.0)); gl_FragColor = vec4(vec3(1.0, 0.85, 0.42) * k * (0.08 + 0.62 * e), 1.0); }' }));""")
GIFT_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 11h15v9.2a1.6 1.6 0 0 1-1.6 1.6H6.1a1.6 1.6 0 0 1-1.6-1.6z" fill="#FFC61A" stroke="#1A1030" stroke-width="1.7"/><rect x="3" y="7.4" width="18" height="4.4" rx="1.4" fill="#FFD54F" stroke="#1A1030" stroke-width="1.7"/><path d="M10.4 7.6h3.2v14.1h-3.2z" fill="#FF3FA4"/><path d="M12 7.4C10.6 4 7.4 3.4 6.9 5.3c-.4 1.6 2 2.1 5.1 2.1zM12 7.4c1.4-3.4 4.6-4 5.1-2.1.4 1.6-2 2.1-5.1 2.1z" fill="#FF3FA4" stroke="#1A1030" stroke-width="1.4" stroke-linejoin="round"/></svg>'
rep('  <div class="orbptr giftptr" id="giftPtr"><i></i><u><b></b></u></div>', '  <div class="orbptr giftptr" id="giftPtr"><i>' + GIFT_SVG + '</i><u><b></b></u></div>')
rep(""".giftptr i{background:radial-gradient(circle at 50% 40%,#FFE89A,#FFC61A 60%,#E79A00);animation:none;box-shadow:0 0 14px 6px rgba(255,214,79,.7)}
.giftptr i::after{content:"";position:absolute;inset:9px 5px;border-left:3px solid #FF3FA4;border-right:3px solid #FF3FA4;transform:scaleX(.18)}""",
""".giftptr i{inset:3px;display:grid;place-items:center;background:radial-gradient(circle at 50% 38%,#FFFFFF,#FFF2C6 55%,#FFD86B);animation:giftbob 1s ease-in-out infinite alternate;box-shadow:0 0 16px 6px rgba(255,214,79,.75)}
.giftptr.edge i{animation:giftbob 1s ease-in-out infinite alternate,orbpulse .7s ease-in-out infinite alternate}
.giftptr i svg{width:22px;height:22px;display:block}
@keyframes giftbob{from{transform:rotate(-8deg)}to{transform:rotate(8deg)}}""")
open(P, 'w').write(src)
print('ok', len(src))
