# Compare the three versions of the song offline: loudness over the hook bars and the bridge bars, peaks, and voice counts
import asyncio, json, sys, base64, wave, struct
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
SAVE = '--wav' in sys.argv
JS = r"""async ([style, mode, md, sec, keep]) => {
  window.MUSIC_STYLE = style;
  const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A.music(mode); if (md) A.mood.apply(null, md);
  let nodes = 0; const oo = oc.createOscillator.bind(oc), ob = oc.createBufferSource.bind(oc); oc.createOscillator = () => { nodes++; return oo(); }; oc.createBufferSource = () => { nodes++; return ob(); };
  A._pump(sec + 0.5);
  const buf = await oc.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1), db = x => +(20 * Math.log10(Math.max(1e-9, x))).toFixed(1);
  const seg = (a, b) => { const i0 = Math.floor(a * sr), i1 = Math.min(L.length, Math.floor(b * sr)); let ss = 0, pk = 0; for (let i = i0; i < i1; i++) { ss += L[i] * L[i] + R[i] * R[i]; const m = Math.max(Math.abs(L[i]), Math.abs(R[i])); if (m > pk) pk = m; } return [db(Math.sqrt(ss / (2 * (i1 - i0)))), db(pk)]; };
  // a bar is 4 beats; the tempo drifts toward its target from 100, so measure the hook and bridge by time windows that sit inside each
  const bar = mode === 'menu' ? 2.4 : 2.07, o = { all: seg(1, 1 + sec), hook: seg(1 + bar * 1, 1 + bar * 7), bridge: seg(1 + bar * 9, 1 + bar * 15), nodes };
  if (keep) { const m = new Float32Array(L.length); for (let i = 0; i < m.length; i++) m[i] = (L[i] + R[i]) * 0.5; const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); o.wav = btoa(s); }
  return o; }"""
def wav(path, b64):
    import numpy as np
    a = np.frombuffer(base64.b64decode(b64), dtype=np.float32)
    a = (np.clip(a, -1, 1) * 32767).astype('<i2')
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100); w.writeframes(a.tobytes()); w.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('window.ready === true')
        for mode, md, sec in [('play', None, 34), ('menu', None, 38), ('play', [True, False, False, False], 20), ('play', [False, True, False, False], 20)]:
            for style in ['spooky', 'tropical', 'pop']:
                r = await pg.evaluate(JS, [style, mode, md, sec, SAVE and md is None])
                if r.get('wav'): wav(f'aud/m_{style}_{mode}.wav', r.pop('wav'))
                print(f"{mode:5s} {str(md):28s} {style:9s} all {r['all']}  hook {r['hook']}  bridge {r['bridge']}  nodes {r['nodes']}")
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
