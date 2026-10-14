"""Check the menu song's bar grid against the intro loop: chords per bar (bars 3..20 of the menu, from MENU_AT = bar 8) against the
intro's progression, and the beat phase from onsets."""
import sys, numpy as np
sys.path.insert(0, '/home/user/rollmodel/tools')
from intro_audio_an import load, stft_mag, onset_env
SR = 22050; BPM = 110.89; BEAT = 60 / BPM; BAR = 4 * BEAT; MENU_AT = 17.605
x = load('/home/user/rollmodel/game/music/menu.mp3', SR)
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def tmpl(root, minor): t = np.zeros(12); t[root % 12] = 1; t[(root + (3 if minor else 4)) % 12] = 0.8; t[(root + 7) % 12] = 0.7; return t
CHS = {'Dm': tmpl(2, 1), 'Am': tmpl(9, 1), 'Bb': tmpl(10, 0), 'E': tmpl(4, 0), 'F': tmpl(5, 0), 'C': tmpl(0, 0), 'G': tmpl(7, 0), 'Em': tmpl(4, 1), 'Gm': tmpl(7, 1)}
def chroma_seg(a):
    n = 8192; f = np.fft.rfftfreq(n, 1 / SR); ok = (f > 60) & (f < 1000); pc = (np.round(12 * np.log2(f[ok] / 440)) + 9) % 12
    M = np.abs(np.fft.rfft(a[:n] * np.hanning(min(n, len(a))) if len(a) >= n else np.pad(a, (0, n - len(a))), n)) if False else None
    # average over frames
    c = np.zeros(12); h = 2048
    for i in range(0, len(a) - n, h):
        m = np.abs(np.fft.rfft(a[i:i + n] * np.hanning(n)))[ok] ** 2
        for k in range(12): c[k] += m[pc == k].sum()
    return c / (c.sum() + 1e-9)
def best(c): sc = {k: float(np.dot(c, v) / np.linalg.norm(v)) for k, v in CHS.items()}; return sorted(sc.items(), key=lambda kv: -kv[1])[:2]
print('menu bars (k: start s: best chords)')
for k in range(3, 21):
    t0 = MENU_AT + (k - 8) * BAR; a = x[int(t0 * SR):int((t0 + BAR) * SR)]
    if len(a) < BAR * SR * 0.9: break
    print(k, round(t0, 3), best(chroma_seg(a)))
# beat phase: onset envelope folded on the beat grid anchored at MENU_AT
e, h = onset_env(x); fps = SR / h; tt = np.arange(len(e)) / fps
sel = (tt > 7) & (tt < 43.5); ph = ((tt[sel] - MENU_AT) / BEAT) % 1.0
bins = np.zeros(40); np.add.at(bins, (ph * 40).astype(int) % 40, e[sel])
pk = int(np.argmax(bins)); print('onset peak phase (beats) relative to MENU_AT grid:', round(pk / 40, 3), ' => offset', round((pk / 40 if pk < 20 else pk / 40 - 1) * BEAT * 1000, 1), 'ms')
# intro keys stem chords per bar
y = load('/home/user/rollmodel/game/music/intro_keys.mp3', SR); A = 0.25
print('intro keys stem bars:')
for i in range(8):
    t0 = A + i * BAR; print(i, best(chroma_seg(y[int(t0 * SR):int((t0 + BAR) * SR)])))
d = load('/home/user/rollmodel/game/music/intro_drive.mp3', SR); e2, _ = onset_env(d); tt2 = np.arange(len(e2)) / fps; ph2 = ((tt2 - A) / BEAT) % 1.0
b2 = np.zeros(40); np.add.at(b2, (ph2 * 40).astype(int) % 40, e2); pk2 = int(np.argmax(b2)); print('intro drive onset phase vs its own grid:', round(pk2 / 40, 3))
