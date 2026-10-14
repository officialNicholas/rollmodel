#!/usr/bin/env python3
"""v257 intro: cut the adaptive intro music from a Ludo.ai track separated into stems (demucs htdemucs).
Finds the exact tempo and the downbeat, takes N bars, bakes a crossfade over the loop seam (so it loops without a click), and writes
each stem with a short pre-roll; the loop points (a, b, seconds) are printed for the page's table. Usage:
  intro_music_build.py <stems dir> <out dir> [bars] [start bar]"""
import sys, os, json, subprocess, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_audio_an import load
SR = 44100
def env(x, h=128, n=1024):
    w = np.hanning(n); fr = 1 + (len(x) - n) // h; idx = np.arange(n)[None, :] + h * np.arange(fr)[:, None]
    M = np.abs(np.fft.rfft(x[idx] * w, axis=1)); L = np.log1p(50 * M); e = np.maximum(0, np.diff(L, axis=0)).sum(1); e = np.concatenate([[0], e])
    e -= np.convolve(e, np.ones(64) / 64, 'same'); return np.maximum(e, 0), SR / h
def grid(x):
    e, fps = env(x); best = (0, 0, 0)
    for bpm in np.arange(97, 103, 0.005):
        per = 60 / bpm * fps; nb = int((len(e) - 2) / per) - 1
        for ph in np.arange(0, per, per / 48):
            pos = (ph + per * np.arange(nb)).astype(int); s = e[pos].sum() + 0.5 * e[pos + 1].sum()
            if s > best[0]: best = (s, bpm, ph / fps)
    return best[1], best[2]
if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; bars = int(sys.argv[3]) if len(sys.argv) > 3 else 16; b0 = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    st = {k: load(os.path.join(src, k + '.wav'), SR, 2) for k in ('drums', 'bass', 'other', 'vocals')}
    st['other'] = st['other'] + st.pop('vocals')
    bpm, ph = grid(st['drums'].mean(1)); beat = 60 / bpm
    # the downbeat: of the four beat phases, the one with the most low-end punch (the kick)
    lo = st['drums'].mean(1); sc = []
    for k in range(4):
        t = ph + k * beat + 4 * beat * np.arange(int(len(lo) / SR / (4 * beat)) - 1); sc.append(sum(np.abs(lo[int(u * SR):int(u * SR) + 2000]).sum() for u in t))
    db = ph + int(np.argmax(sc)) * beat
    s0 = db + b0 * 4 * beat; L = bars * 4 * beat; pre = 0.25; F = int(0.35 * SR)
    print(json.dumps({'bpm': round(bpm, 3), 'phase': round(ph, 4), 'downbeat': round(db, 4), 'start': round(s0, 4), 'len': round(L, 5)}))
    os.makedirs(out, exist_ok=True)
    i0, n = int(round(s0 * SR)), int(round(L * SR)); p = int(pre * SR)
    for k, x in st.items():
        assert i0 + n + F < len(x), 'not enough track for that many bars'
        loop = x[i0:i0 + n].copy(); tail = x[i0 + n:i0 + n + F]; u = np.linspace(0, 1, F)[:, None]
        loop[:F] = loop[:F] * np.sin(u * np.pi / 2) + tail * np.cos(u * np.pi / 2)
        y = np.concatenate([x[i0 - p:i0] * np.linspace(0, 1, p)[:, None] ** 2, loop, loop[:int(0.5 * SR)]])  # (pre-roll in; half a second of the loop's start after its end, for the decoder's sake)
        wav = os.path.join(out, k + '.wav'); import soundfile as sf; sf.write(wav, y.astype(np.float32), SR)
    print(json.dumps({'a': round(pre, 5), 'b': round(pre + n / SR, 5)}))
