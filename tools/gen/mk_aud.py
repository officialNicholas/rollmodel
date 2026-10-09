# builds aud/audiotest.html from the game's current makeAudio, plus render helpers
import sys, re
src = open(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.html').read()
out = sys.argv[2] if len(sys.argv) > 2 else 'aud/audiotest.html'
i = src.index('function makeAudio() {'); j = src.index('\nconst AU = makeAudio();', i)
eng = src[i:j]
head = """<!doctype html><html><body><script>
const store = { muted: false }; const P = { x: 0, z: 0 }; const camera = { matrixWorld: { elements: [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1] } };
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
"""
helpers = r"""
function b64(f32) { const u8 = new Uint8Array(f32.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }
function stats(buf, keep, from) {
  const sr = buf.sampleRate, i0 = Math.floor((from || 0) * sr), L = buf.getChannelData(0).subarray(i0), R = buf.getChannelData(1).subarray(i0), n = L.length; let pk = 0, ss = 0, bal = 0, sm = 0, sd = 0, nan = 0;
  for (let i = 0; i < n; i++) { if (L[i] !== L[i] || R[i] !== R[i]) { nan++; continue; } const a = Math.abs(L[i]), b = Math.abs(R[i]); if (a > pk) pk = a; if (b > pk) pk = b; ss += L[i] * L[i] + R[i] * R[i]; bal += b - a; const m = (L[i] + R[i]) / 2, s = (L[i] - R[i]) / 2; sm += m * m; sd += s * s; }
  const win = Math.floor(sr * 0.1); let maxst = 0, last = 0;
  for (let i = 0; i + win <= n; i += win) { let s = 0; for (let j = i; j < i + win; j++) s += L[j] * L[j] + R[j] * R[j]; const r = Math.sqrt(s / (2 * win)); if (r > maxst) maxst = r; if (r > 0.001) last = (i + win) / sr; }
  const db = x => +(20 * Math.log10(Math.max(1e-9, x))).toFixed(1);
  const o = { peak: db(pk), rms: db(Math.sqrt(ss / (2 * n))), maxST: db(maxst), audibleUntil: +last.toFixed(2), pan: +(bal / n).toFixed(4), side: db(Math.sqrt(sd / Math.max(1e-12, sm))), nan };
  if (keep === 'stereo') { const m = new Float32Array(n * 2); for (let i = 0; i < n; i++) { m[2 * i] = L[i]; m[2 * i + 1] = R[i]; } o.wav = b64(m); o.sr = sr; o.ch = 2; }
  else if (keep) { const m = new Float32Array(Math.floor(n / 2)); for (let i = 0; i < m.length; i++) m[i] = (L[2 * i] + R[2 * i]) * 0.5; o.wav = b64(m); o.sr = sr / 2; o.ch = 1; }
  return o;
}
window.renderFx = async (name, args, sec, keep) => { const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A[name].apply(null, args || []); return stats(await oc.startRendering(), keep, 1); };
window.renderMusic = async (mode, mood, sec, keep, mute) => { const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); if (mute && A._mute) A._mute(mute); A._offset(1); A.music(mode); if (mood) A.mood.apply(null, mood); A._pump(sec + 0.5); return stats(await oc.startRendering(), keep, 1); };
window.renderMix = async (mode, fxlist, sec, keep) => { const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A.music(mode); A._pump(sec + 0.5); for (const [at, n, a] of fxlist) { A._offset(1 + at); A[n].apply(null, a || []); } return stats(await oc.startRendering(), keep, 1); };
window.buildTime = () => { const oc = new OfflineAudioContext(2, 44100, 44100), A = makeAudio(), t0 = performance.now(); A._build(oc); return performance.now() - t0; };
window.ready = true;
</script></body></html>
"""
open(out, 'w').write(head + eng + '\n' + helpers)
print('wrote', out, len(eng))
