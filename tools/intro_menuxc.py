"""Fine beat alignment: the menu song's onsets over bars 9..16 against the intro drive stem's loop (8 bars) by cross-correlation."""
import sys, numpy as np
sys.path.insert(0, '/home/user/rollmodel/tools')
from intro_audio_an import load
SR = 22050; BPM = 110.89; BEAT = 60 / BPM; BAR = 4 * BEAT; MENU_AT = 17.605; A = 0.25
def onset(x, n=512, h=64):
    w = np.hanning(n); fr = 1 + (len(x) - n) // h; idx = np.arange(n)[None, :] + h * np.arange(fr)[:, None]
    M = np.abs(np.fft.rfft(x[idx] * w, axis=1)); L = np.log1p(100 * M); fl = np.maximum(0, np.diff(L, axis=0)).sum(1)
    t = (np.arange(len(fl)) + 1) * h / SR + n / 2 / SR  # (frame centre)
    return fl - np.convolve(fl, np.ones(64) / 64, 'same'), t
m = load('/home/user/rollmodel/game/music/menu.mp3', SR); d = load('/home/user/rollmodel/game/music/intro_drive.mp3', SR)
em, tm = onset(m); ed, td = onset(d); h = 64 / SR
def seg(e, t, t0, dur): i0 = int(np.searchsorted(t, t0)); return e[i0:i0 + int(dur / h)]
for k0 in (9, 13):
    M = seg(em, tm, MENU_AT + (k0 - 8) * BAR, 4 * BAR); best = None
    for lag_ms in np.arange(-120, 121, 1):
        D = seg(ed, td, A + (k0 - 9) * BAR + lag_ms / 1000, 4 * BAR); n = min(len(M), len(D)); v = float(np.dot(M[:n] - M[:n].mean(), D[:n] - D[:n].mean()))
        if best is None or v > best[1]: best = (lag_ms, v)
    print('menu bars', k0, '..', k0 + 3, ': intro grid needs a shift of', best[0], 'ms (positive: the menu is late against MENU_AT)')
# also the kick-only comparison: low band onsets
