p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
# camera: in the customizer, frame your blob big in the space the panel leaves, turning slowly (drag to spin it)
rep("  if (state === 'menu') { const dist = heroFrame(rdt), a = hero.yaw + Math.sin(clock * 0.31) * 0.06; dPos.set(hero.mx + Math.sin(a) * dist, 0.42 + dist * 0.24 + Math.sin(clock * 0.47) * 0.04, hero.mz + Math.cos(a) * dist); dLook.set(hero.mx, 0.4, hero.mz); }",
    "  if (state === 'menu') { const dist = heroFrame(rdt), a = hero.yaw + Math.sin(clock * 0.31) * (lookOpen ? 0 : 0.06), ly = lookOpen ? 0.62 : 0.4; dPos.set(hero.mx + Math.sin(a) * dist, ly + 0.02 + dist * (lookOpen ? 0.2 : 0.24) + Math.sin(clock * 0.47) * 0.04, hero.mz + Math.cos(a) * dist); dLook.set(hero.mx, ly, hero.mz); }")
rep("  if (drop.visible) {\n    const gy = blobVisual(P, VP, dt, ke, kf);",
    "  if (lookOpen && state === 'menu') { if (!lookDrag) lookSpin += rdt * 0.45; P.yaw = hero.yaw + Math.sin(lookSpin) * 0.95; }\n  if (drop.visible) {\n    const gy = blobVisual(P, VP, dt, ke, kf);")
rep("function heroFrame(rdt) {\n  heroT -= rdt; if (heroT > 0) return heroDist; heroT = 0.4;\n  const r = stage.getBoundingClientRect(), d = menu.querySelector('.dock').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;",
    """function heroFrame(rdt) {
  heroT -= rdt; if (heroT > 0) return heroDist; heroT = 0.4;
  if (lookOpen) return lookFrame();
  const r = stage.getBoundingClientRect(), d = menu.querySelector('.dock').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;""")
rep("// a few strokes and splats in both colors so the menu canvas looks like a match in progress",
    """function lookFrame() {
  const r = stage.getBoundingClientRect(), k = lookEl.getBoundingClientRect(), W = r.width, Hh = r.height, side = endSideMQ.matches;
  let tx, ty, fw, fh;
  if (side) { fw = Math.max(80, k.left - r.left); fh = Hh; tx = fw / 2; ty = Hh * 0.5; } else { fh = Math.max(80, k.top - r.top); fw = W; tx = W / 2; ty = fh * 0.56; }
  heroOff.x = W / 2 - tx; heroOff.y = Hh / 2 - ty; hero.mx = P.x; hero.mz = P.z;
  const tv = Math.tan(heroFov() * Math.PI / 360), asp = W / Math.max(1, Hh), wide = myLook.back === 'wings' ? 1.75 : 1.15, tall = myLook.head === 'hat' ? 1.35 : myLook.head ? 1.15 : 0.95;
  heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.62 * fh), wide * W / (2 * tv * asp * 0.72 * fw)), 1.8, 9);
  return heroDist;
}
// ---------- the customizer: color, eyes and this season's accessories, with your blob turning in front of you ----------
const lookEl = $('look');
let lookOpen = false, lookSpin = 0, lookDrag = null;
const EYE_ICON = {
  round: '<circle cx="13" cy="20" r="7.5" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="27" cy="20" r="7.5" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="14" cy="21" r="3.6" fill="#1A1030"/><circle cx="28" cy="21" r="3.6" fill="#1A1030"/>',
  googly: '<circle cx="12.5" cy="19" r="9" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="28.5" cy="19" r="9" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="11" cy="24" r="3" fill="#1A1030"/><circle cx="30" cy="23.5" r="3" fill="#1A1030"/>',
  sleepy: '<path d="M5.5 20h15a7.5 7.5 0 0 1-15 0zM19.5 20h15a7.5 7.5 0 0 1-15 0z" fill="#fff" stroke="#1A1030" stroke-width="2" stroke-linejoin="round"/><path d="M4 19.5h17.5M18.5 19.5H36" stroke="#C99BFF" stroke-width="2.6" stroke-linecap="round"/><circle cx="13" cy="23.5" r="2.8" fill="#1A1030"/><circle cx="27" cy="23.5" r="2.8" fill="#1A1030"/>',
  angry: '<circle cx="13" cy="22" r="7" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="27" cy="22" r="7" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="14" cy="23" r="3.4" fill="#1A1030"/><circle cx="26" cy="23" r="3.4" fill="#1A1030"/><path d="M5 11.5l13 4.5M35 11.5l-13 4.5" stroke="#FF8C9E" stroke-width="3.2" stroke-linecap="round"/>',
  happy: '<path d="M6 23a7 7 0 0 1 14 0M20 23a7 7 0 0 1 14 0" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>',
  cyclops: '<circle cx="20" cy="20" r="11" fill="#fff" stroke="#1A1030" stroke-width="2"/><circle cx="21" cy="21.5" r="5.2" fill="#1A1030"/><circle cx="23" cy="19" r="1.6" fill="#fff"/>',
};
const WEAR_ICON = {
  fangs: '<path d="M8 15c4 7 20 7 24 0" fill="none" stroke="#FF8CA8" stroke-width="3" stroke-linecap="round"/><path d="M13.5 18.2l1.8 8 2.2-7.4zM22.5 19l2.2 7.4 1.8-8z" fill="#fff" stroke="#1A1030" stroke-width="1.4" stroke-linejoin="round"/>',
  wings: '<path d="M20 22C16 14 9 10 2 12c2 3 2 6 1 9 2-1 4-1 6 1 1-2 3-3 5-2 1-2 3-2 6 2zM20 22c4-8 11-12 18-10-2 3-2 6-1 9-2-1-4-1-6 1-1-2-3-3-5-2-1-2-3-2-6 2z" fill="#6A4AA0" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/>',
  halo: '<ellipse cx="20" cy="20" rx="13" ry="5.5" fill="none" stroke="#FFE27A" stroke-width="4"/>',
  hat: '<path d="M14 26c3-6 5-13 9-19 1 4 2 9 4 13l-1 6z" fill="#4A3378" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><ellipse cx="20" cy="27.5" rx="15" ry="3.6" fill="#4A3378" stroke="#D9C8FF" stroke-width="1.6"/><path d="M14.2 23.2c3.6 1.2 8.4 1.2 12.6 0l.5 2.6c-4.4 1.4-9.4 1.4-13.8 0z" fill="#FF8A1F"/>',
  horns: '<path d="M9 30c-1-8 1-15 6-19-1 5 0 10 3 14zM31 30c1-8-1-15-6-19 1 5 0 10-3 14z" fill="#E1283E" stroke="#FFC2CC" stroke-width="1.6" stroke-linejoin="round"/>',
};
function renderLook() {
  $('eyeOpts').innerHTML = EYES.map(([id, name]) => '<button class="lopt" type="button" data-e="' + id + '" aria-label="' + name + ' eyes" title="' + name + '" aria-pressed="' + (myLook.eyes === id) + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + EYE_ICON[id] + '</svg></button>').join('');
  $('wearOpts').innerHTML = WEAR.map(w => '<button class="lopt" type="button" data-w="' + w.id + '" aria-label="' + w.name + '" title="' + w.name + '" aria-pressed="' + (myLook[w.slot] === w.id) + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg></button>').join('');
  $('lookEyes').textContent = (EYES.find(e => e[0] === myLook.eyes) || EYES[0])[1]; $('lookColor').textContent = colorOf().name;
}
function saveLook() { store.look = Object.assign({}, myLook); save(); }
function openLook() {
  if (state !== 'menu' || building) return;
  lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookEl.hidden = false; drop.visible = true; P.y = 0; heroT = 0; lookSpin = 0;
  if (!store.seen.look) { store.seen.look = 1; save(); $('lookBtn').classList.remove('hot'); }
  setTimeout(() => $('lookDone').focus({ preventScroll: true }), 30);
}
function closeLook() { if (!lookOpen) return; lookOpen = false; menu.classList.remove('looking'); lookEl.hidden = true; drop.visible = false; heroT = 0; menuPose(); setTimeout(() => $('lookBtn').focus({ preventScroll: true }), 30); }
function lookPop() { menuReact = 0.7; AU.pop(); }
$('lookBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLook(); });
$('lookDone').addEventListener('click', () => { AU.init(); AU.ui(); closeLook(); });
$('eyeOpts').addEventListener('click', e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); myLook.eyes = b.dataset.e; saveLook(); renderLook(); lookPop(); });
$('wearOpts').addEventListener('click', e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0; if (w.slot === 'back' && myLook.back) lookSpin = Math.PI / 2; });
canvas.addEventListener('pointerdown', e => { if (lookOpen) lookDrag = { id: e.pointerId, x: e.clientX }; });
canvas.addEventListener('pointermove', e => { if (lookOpen && lookDrag && lookDrag.id === e.pointerId) { lookSpin += (e.clientX - lookDrag.x) * 0.012; lookDrag.x = e.clientX; } });
const endLookDrag = e => { if (lookDrag && lookDrag.id === e.pointerId) lookDrag = null; };
canvas.addEventListener('pointerup', endLookDrag); canvas.addEventListener('pointercancel', endLookDrag);
// a few strokes and splats in both colors so the menu canvas looks like a match in progress""")
rep("  document.querySelectorAll('#swatches .sw').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.c === c.id)));",
    "  document.querySelectorAll('#swatches .sw').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.c === c.id))); const lc = $('lookColor'); if (lc) lc.textContent = c.name;")
rep("  if (!nameModal.hidden) { if (e.key === 'Escape') { e.preventDefault(); closeName(); } return; }",
    "  if (!nameModal.hidden) { if (e.key === 'Escape') { e.preventDefault(); closeName(); } return; }\n  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }")
# leaving the menu closes the customizer; the season badge on Customize until you've opened it once
rep("function start() {\n  if (building) return;", "function start() {\n  if (building) return;\n  if (lookOpen) closeLook();")
rep("colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches();",
    "colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); if (store.seen && store.seen.look) $('lookBtn').classList.remove('hot');")
open(p,'w').write(s); print('ok')
