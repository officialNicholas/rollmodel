#!/usr/bin/env python3
"""v316: the Jellyfish Boss's sounds (b_*) and the Sunken Keep's (k_*), finished from the raw Ludo.ai takes into game/sfx/<name>.mp3.
The takes: two of each sound, made with tools/ludo.py sfx <name>_<take>.mp3 "<prompt>" --dur <seconds> --rid rm316-<name>-<take>
(the prompts and lengths in TAKES). Which take, and why, is in ONE: chosen by measurement (onset, length, how it dies away, clipping,
loudness, spectral balance, how much is lost going to mono, and how much of it is left on a phone's speaker, above about 250 Hz).

One-shots: mono (the two channels mixed down), the rumble under 35 Hz off (zero phase), a 2 ms fade in at the onset (the takes start
right on it), the tail cut 40 ms after it has died away (-48 dB under its loudest, over 20 ms) or at a set length, and faded. Two are
built from two takes: b_slam (the slam's deep boom has nothing a phone can play, so the punch's smash on top, twice) and b_launch (its
whoomp has no splash, so the gloves' slime burst under it, pitched down). Each is set to its own loudness, as the loudest 400 ms,
K-weighted (BS.1770), in LUFS: the mix is in the files, the game plays them at about full level (as with ribbon, w_wind, w_ting: their
loudest 400 ms -7, -5 and -12 LUFS; the intro's i_* -20 to -24). Peaks are held under -1.5 dBFS by a look-ahead limiter that may take
at most 6 dB off them. mp3, 44.1 kHz mono 96 kb/s, as the game's other effects. Loops: k_amb (the stage's bed, stereo, 80 kb/s) and
k_bubble (the slime pool, mono, 80 kb/s), each stitched from both its takes as tools/desert_wind.py stitches the intro's wind: the quiet
starts and ends trimmed, the second take's tone matched to the first's, each crossfaded into the next (equal power) and the end into
the start, the level evened out, set to its loudness (integrated, LUFS), and the file holds the loop with 0.4 s of itself either side
(loop points 0.4 s and 0.4 s + the loop, printed), so the points hold whatever start offset the decoder adds. The same takes give the
same files, byte for byte.
Usage: boss_sfx_build.py <takes folder> [<out folder> (game/sfx)] [names...]"""
import os, sys, subprocess, numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, lfilter
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
U = ', underwater, cartoon game sound effect, no music'
TAKES = {  # name: (seconds asked for, the prompt), two takes each
    'b_churn': (2.5, 'a pool of thick slime churning and boiling violently, deep gloopy bubbling and glugging, something huge stirring beneath' + U),
    'b_burst': (1.2, 'two giant fists bursting up out of a pool of thick slime, a big wet gloopy splash eruption' + U),
    'b_grab': (1.0, 'huge rubbery gloves slamming down onto stone and gripping hard, a heavy wet slap and a deep stone thud' + U),
    'b_haul': (2.5, 'a giant jellyfish monster straining to haul itself out of thick slime, deep rubbery creaking and stretching, slime pouring and sloshing off it' + U),
    'b_launch': (1.6, 'a giant jellyfish monster blasting upward with one huge pulse of its bell, a deep powerful whoomp, rushing water and a big splash' + U),
    'b_bump': (1.0, 'two huge boxing gloves bumping together, a punchy heavy thump with crackling electric sparks' + U),
    'b_roar': (2.0, 'a giant underwater jellyfish monster roaring, deep bubbly gurgling roar, menacing but cartoonish, boss monster sound effect'),
    'b_pulse': (0.6, 'a soft deep whoomp of a jellyfish bell pulsing, a muffled push of water, gentle' + U),
    'b_windup': (0.7, 'a giant boxing glove winding up for a punch, rubbery stretching creak and a rising whoosh' + U),
    'b_punch': (0.8, 'a huge boxing glove punch smashing into a stone floor, a heavy muffled boom with a wet splash' + U),
    'b_slam': (1.8, 'a giant monster slamming both fists into a stone floor, a massive deep boom with a shockwave rumble and falling rubble' + U),
    'b_sweep': (1.0, 'a giant arm sweeping fast through deep water, a heavy swoosh with churning bubbles' + U),
    'b_charge': (1.2, 'a jellyfish charging up electricity, crackling rising electric hum with fizzing bubbles' + U),
    'b_zap': (0.9, 'a jellyfish electric sting discharge, a sharp crackling electric zap and sizzle' + U),
    'b_hurt': (0.9, 'a giant jelly monster being hit hard, a wobbly rubbery squelch and a pained bubbly groan' + U),
    'b_dizzy': (1.6, 'a dazed jelly monster wobbling dizzily, a wobbly boing and a woozy bubbly warble' + U),
    'b_taunt': (1.6, 'a giant jellyfish monster laughing mockingly, a deep bubbly gurgling laugh, cartoon boss monster sound'),
    'b_defeat': (2.5, 'a giant jelly monster deflating and sinking into slime, a long descending rubbery deflate with a sad bubbling gurgle and a final gloopy plop' + U),
    'k_amb': (10, 'deep underwater ambience in a sunken stone ruin, muffled water, a soft distant rumble, gentle bubbles rising, faint creaking wood and chains, calm, seamless, no music'),
    'k_bubble': (4, 'a pool of thick slime bubbling, slow gloopy bubbles swelling and popping, steady, loopable' + U),
    'k_drip': (0.6, 'a single heavy drop of thick slime falling into a puddle, a deep gloopy plop with a small splash' + U),
    'k_cage': (1.5, 'a rusty iron cage swinging on a chain and rattling, creaking metal and clanking chain' + U),
    'k_laugh': (1.5, 'a cartoon pirate skeleton laughing, a rattly bony cackle with a clacking jaw, spooky but fun, game sound effect, no music'),
    'k_fall': (1.0, 'a small jelly creature falling into a pool of thick slime, a deep gloopy splash and a sinking glug' + U),
}
# the one-shots: t the take, lu the loudness (LUFS, the loudest 400 ms; the hits, grab, punch and slam, as loud as their peaks allow
# with 6 dB taken off them: their loudest 100 ms, -11 to -12 LUFS, is in line with the rest's), max the longest it may run (s) before
# its fade, fade (s), lay the layers (a take, its gain in dB, when it comes in (s), its speed (1: as it is; under 1 lower and longer),
# a high-pass (Hz), its length (s))
ONE = {
    # the entrance
    'b_churn': dict(t='b_churn_1', lu=-15, max=2.0),   # 1: dense, broad, boiling all through and dying away; 2: sparse low glugs, nothing over 2.5 kHz
    'b_burst': dict(t='b_burst_2', lu=-13),            # 2: the splash's spray is there (1: a low thump with little splash)
    'b_grab': dict(t='b_grab_1', lu=-15),              # 1: the slap and a deeper, longer thud (2 much the same, shorter)
    'b_haul': dict(t='b_haul_1', lu=-15),              # 1: the strain builds to the middle and eases (2: all at the start)
    'b_launch': dict(t='b_launch_1', lu=-11, lay=[('b_burst_2', -4, 0.02, 0.85, 120, 1.0)]),  # 1: one big whoomp (2 swells twice); with the burst's slime under it
    'b_bump': dict(t='b_bump_2', lu=-13),              # 2: thump and sparks dying away cleanly (1 stops short)
    'b_roar': dict(t='b_roar_1', lu=-12),              # 1: the pitch rises and falls as a roar does (2 climbs again at its end)
    # the moves
    'b_pulse': dict(t='b_pulse_2', lu=-24),            # both (quiet: every beat of the bell)
    'b_pulse2': dict(t='b_pulse_1', lu=-24),
    'b_windup': dict(t='b_windup_2', lu=-17, fade=0.12),  # both (each punch, slam and zap)
    'b_windup2': dict(t='b_windup_1', lu=-17),
    'b_punch': dict(t='b_punch_2', lu=-15),            # 2 only: the smash on stone is there (1 is a boom under 120 Hz, near silent on a phone)
    'b_slam': dict(t='b_slam_1', lu=-14.5, lay=[('b_punch_2', 0, 0.0, 1.0, 300, 0.45), ('b_punch_2', -3, 0.035, 0.9, 300, 0.45)]),  # 1: the longer shockwave rumble (both all under 120 Hz): with the punch's smash, twice (two fists, a hair apart)
    'b_sweep': dict(t='b_sweep_2', lu=-15),            # 2: swells and falls away, a swoosh (1: all at the start)
    'b_charge': dict(t='b_charge_1', lu=-16, fade=0.18),  # 1: a hum under the crackle, 1.1 s to the zap's 1.25 (2: hiss only)
    'b_zap': dict(t='b_zap_1', lu=-13),                # 1: the crackle holds, then dies (2: its two channels apart, 3 dB lost in mono)
    'b_hurt': dict(t='b_hurt_1', lu=-15),              # both
    'b_hurt2': dict(t='b_hurt_2', lu=-15),
    'b_dizzy': dict(t='b_dizzy_1', lu=-16),            # 1: dies away at its end (2 is cut off)
    'b_taunt': dict(t='b_taunt_1', lu=-15, fade=0.15),  # 1: a laugh in syllables, clear on a phone (2 deeper and duller, half of it silence)
    'b_defeat': dict(t='b_defeat_1', lu=-14),          # 1: bubbling, its loudest plop at the end (2: smooth, its loudest at the start)
    # the keep
    'k_drip': dict(t='k_drip_2', lu=-19),              # both
    'k_drip2': dict(t='k_drip_1', lu=-19),
    'k_cage': dict(t='k_cage_2', lu=-18),              # 2: more of the iron's clank
    'k_laugh': dict(t='k_laugh_2', lu=-15, fade=0.12),  # 2: straight in, the cackle clearer
    'k_fall': dict(t='k_fall_1', lu=-14),              # 1: a deeper splash (2 thin and bright)
}
# the loops: the takes and the stretch of each used (s), the crossfade (s), the evening-out window (s) and how far, the loudness
# (integrated LUFS), the channels and the bit rate
LOOP = {
    'k_amb': dict(t=[('k_amb_2', 0.9, 7.9), ('k_amb_1', 0.35, 7.0)], xf=1.6, win=1.6, even=0.85, lu=-20, ch=2, br='80k', shelf=-6),
    'k_bubble': dict(t=[('k_bubble_1', 0.03, 3.97), ('k_bubble_2', 0.03, 3.97)], xf=0.6, win=2.0, even=0.5, lu=-22, ch=1, br='80k', shelf=0),
}
CEIL, MAXGR = -1.5, 6.0   # dBFS, the limiter's ceiling (the mp3 can overshoot it a little); the most it may take off a peak, dB

def load(path, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x if ch == 1 else x.reshape(-1, ch)
def enc(x, out, br):   # (lame takes 0.445 dB off everything, a scale of 0.95: given back here, so the file decodes to what was made)
    ch = 1 if x.ndim == 1 else x.shape[1]
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', '-', '-map_metadata', '-1', '-c:a', 'libmp3lame', '-b:a', br, out],
                   input=np.clip(x / 0.95, -1, 1).astype(np.float32).tobytes(), check=True)
# K-weighting (BS.1770) at any rate: the high shelf, then the high-pass
def kw(x):
    K = np.tan(np.pi * 1681.974450955533 / SR); Vh = 10 ** (3.999843853973347 / 20); Vb = Vh ** 0.4996667741545416; Q = 0.7071752369554196; a0 = 1 + K / Q + K * K
    y = lfilter([(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0], [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], x, axis=0)
    K = np.tan(np.pi * 38.13547087602444 / SR); Q = 0.5003270373238773; a0 = 1 + K / Q + K * K
    return lfilter([1, -2, 1], [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], y, axis=0)
def power(x):
    z = kw(x) ** 2; return z if z.ndim == 1 else z.sum(1)
def lufs(p): return -0.691 + 10 * np.log10(max(p, 1e-12))
def loudest(x, w=0.4):   # the loudest w seconds (momentary loudness at its peak)
    z = power(x); n = int(w * SR); z = np.concatenate([z, np.zeros(max(0, n - len(z)))]); c = np.concatenate([[0], np.cumsum(z)])
    return lufs(((c[n:] - c[:-n]) / n).max())
def integrated(x):       # gated (BS.1770): 400 ms blocks, 75% overlap
    z = power(x); n = int(0.4 * SR); h = n // 4; c = np.concatenate([[0], np.cumsum(z)])
    b = np.array([(c[i + n] - c[i]) / n for i in range(0, len(z) - n + 1, h)]); b = b[[lufs(v) > -70 for v in b]]
    if not len(b): return -70.0
    rel = lufs(b.mean()) - 10; b = b[[lufs(v) > rel for v in b]]; return lufs(b.mean())
def hp(x, f, order=2, zero=False): s = butter(order, f, 'highpass', fs=SR, output='sos'); return sosfiltfilt(s, x, axis=0) if zero else sosfilt(s, x, axis=0)
def shelf(x, gdb, f0=120.0, S=0.7):   # a low shelf (RBJ)
    A = 10 ** (gdb / 40); w = 2 * np.pi * f0 / SR; c = np.cos(w); al = np.sin(w) / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2); r = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) - (A - 1) * c + r), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - r)]; a = [(A + 1) + (A - 1) * c + r, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - r]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)
def env(x, ms=5):        # the RMS envelope over ms
    m = x if x.ndim == 1 else x.mean(1); n = max(1, int(ms / 1000 * SR)); return np.sqrt(np.convolve(m * m, np.ones(n) / n, 'same'))
def limit(x, ceil=CEIL, look=0.002, rel=0.025):
    # the gain each sample needs, its minimum over the next `look` (so it's down before the peak arrives), smoothed over the same
    # (never above what's needed), and let back up no faster than `rel`
    c = 10 ** (ceil / 20); a = np.abs(x) if x.ndim == 1 else np.abs(x).max(1); need = np.minimum(1, c / np.maximum(a, 1e-12))
    if need.min() >= 1: return x
    n = max(1, int(look * SR)); hold = np.lib.stride_tricks.sliding_window_view(np.concatenate([need, np.ones(n - 1)]), n).min(1)
    cs = np.concatenate([np.zeros(n), np.cumsum(hold)]); sm = np.minimum(hold, (cs[n:] - cs[:-n]) / n)  # (the trailing mean over n)
    g = np.empty_like(sm); k = np.exp(-1 / (rel * SR)); v = 1.0
    for i in range(len(sm)):
        v = 1 - (1 - v) * k; v = sm[i] if sm[i] < v else v; g[i] = v
    return x * (g if x.ndim == 1 else g[:, None])
def speed(x, r):         # played r times as fast (pitch with it), as a buffer's playbackRate does
    if r == 1: return x
    t = np.arange(0, len(x) - 1, r); return np.interp(t, np.arange(len(x)), x)
def fade_out(x, sec):
    n = min(len(x), int(sec * SR)); w = np.cos(np.linspace(0, np.pi / 2, n)) ** 2; x = x.copy(); x[len(x) - n:] *= w; return x

def one(name, o, src, out):
    x = hp(load(f'{src}/{o["t"]}.mp3'), 35, zero=True)   # (zero phase: a causal one shifts the boom against the smash and adds 2 to 4 dB of peak)
    for t, gdb, at, r, f, ln in o.get('lay', []):
        y = hp(speed(load(f'{src}/{t}.mp3'), r), f, 4)[:int(ln * SR)]; y = fade_out(y, min(0.12, ln / 3)) * 10 ** (gdb / 20)
        i = int(at * SR); n = max(len(x), i + len(y)); z = np.zeros(n); z[:len(x)] += x; z[i:i + len(y)] += y; x = z
    # the onset (where the 5 ms envelope first passes -40 dB under its loudest), 3 ms before it, faded in over 2 ms
    e = env(x); i0 = max(0, int(np.argmax(e > e.max() * 0.01)) - int(0.003 * SR)); x = x[i0:]
    f = int(0.002 * SR); x[:f] *= np.linspace(0, 1, f)
    # the tail: 40 ms past where it's last above -48 dB under its loudest (over 20 ms; the takes' last 30 ms not counted: some end on a
    # blip), or the longest it may run; faded
    e = env(x, 20); e[-int(0.03 * SR):] = 0; last = len(x) - 1 - int(np.argmax(e[::-1] > e.max() * 10 ** (-48 / 20))); end = min(len(x), last + int(0.04 * SR))
    cut = o.get('max') and end > int(o['max'] * SR)
    if cut: end = int(o['max'] * SR)
    x = fade_out(x[:end], o.get('fade', 0.25 if cut else 0.08))
    # the loudness, then the peaks held; the limiter may take at most MAXGR dB off a peak (a sound too spiky for its loudness stays a
    # little under it, and the report says so); a few rounds, as the limiter takes a little of the loudness
    y = x; g = 10 ** ((o['lu'] - loudest(x)) / 20); pk0 = np.abs(x).max()
    for _ in range(5):
        g = min(g, 10 ** ((CEIL + MAXGR) / 20) / pk0); y = limit(x * g); L = loudest(y)
        if abs(L - o['lu']) < 0.1 or 20 * np.log10(pk0 * g) - CEIL >= MAXGR - 0.01: break
        g *= 10 ** ((o['lu'] - L) / 20)
    enc(y, f'{out}/{name}.mp3', '96k')
    return y, 20 * np.log10(pk0 * g) - CEIL

def stitch(name, o, src, out):
    ch = o['ch']; parts = []
    for t, a, b in o['t']:
        y = hp(load(f'{src}/{t}.mp3', ch), 30)
        if o['shelf']: y = shelf(y, o['shelf'])
        parts.append(y[int(a * SR):int(b * SR)])
    rms = lambda v: np.sqrt((v ** 2).mean())
    A = parts[0]
    # each later take's tone matched to the first's (a smooth spectral correction within 9 dB), and its level
    def mag(v): X = np.abs(np.fft.rfft(v if v.ndim == 1 else v.mean(1))); n = max(3, len(X) // 400) | 1; return np.convolve(X, np.ones(n) / n, 'same') + 1e-12
    mA = mag(A)
    for k in range(1, len(parts)):
        Bt = parts[k]; XB = np.fft.rfft(Bt, axis=0); m = np.interp(np.linspace(0, 1, XB.shape[0]), np.linspace(0, 1, len(mA)), mA)
        g = np.clip(m / np.interp(np.linspace(0, 1, XB.shape[0]), np.linspace(0, 1, len(mag(Bt))), mag(Bt)) * (rms(Bt) / rms(A)), 10 ** (-9 / 20), 10 ** (9 / 20))
        Bm = np.fft.irfft(XB * (g if XB.ndim == 1 else g[:, None]), n=len(Bt), axis=0); parts[k] = Bm * rms(A) / rms(Bm)
    # one after another, each crossfaded into the next (equal power), and the end into the start
    F = int(o['xf'] * SR); r = np.linspace(0, 1, F); fi, fo = np.sin(r * np.pi / 2), np.cos(r * np.pi / 2)
    if ch > 1: fi, fo = fi[:, None], fo[:, None]
    T = parts[0]
    for s in parts[1:]: T = np.concatenate([T[:-F], T[-F:] * fo + s[:F] * fi, s[F:]])
    L = T[F:].copy(); L[-F:] = T[-F:] * fo + T[:F] * fi
    # the level evened out over a window (taken round the loop), then set
    n = len(L); p = L ** 2 if ch == 1 else (L ** 2).mean(1); W = int(o['win'] * SR); ext = np.concatenate([p[-W:], p, p[:W]]); c = np.cumsum(np.concatenate([[0], ext]))
    ev = np.sqrt((c[W + W // 2 + np.arange(n)] - c[W // 2 + np.arange(n)]) / W) + 1e-9; k = (np.exp(np.log(ev).mean()) / ev) ** o['even']
    L = L * (k if ch == 1 else k[:, None])
    L = L * 10 ** ((o['lu'] - integrated(np.concatenate([L, L]))) / 20)
    PAD = int(0.4 * SR); full = np.concatenate([L[-PAD:], L, L[:PAD]])
    pk = 20 * np.log10(np.abs(full).max())
    if pk > CEIL: full = full * 10 ** ((CEIL - pk) / 20)   # (a loop is only turned down, never limited: a limiter's gain wouldn't wrap)
    enc(full, f'{out}/{name}.mp3', o['br'])
    return full, n

def report(name, path, x, loop=None, gr=None, lu=None):
    d = load(path, 1 if x.ndim == 1 else 2); kb = os.path.getsize(path) / 1024
    print('%-10s %6.3f s %5.1f KB  peak %5.1f dBFS  loudest 400 ms %6.1f%s  integrated %6.1f LUFS%s%s' % (
        name, len(d) / SR, kb, 20 * np.log10(np.abs(d).max()), loudest(d), ' (%g)' % lu if lu is not None and abs(loudest(d) - lu) > 0.3 else '',
        integrated(np.concatenate([d, d]) if loop else d), '  limited %.1f dB' % gr if gr and gr > 0.05 else '',
        '  loop %.5f s: points 0.4 to %.5f s' % (loop / SR, 0.4 + loop / SR) if loop else ''))

if __name__ == '__main__':
    src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(HERE), 'game', 'sfx'); want = set(sys.argv[3:])
    os.makedirs(out, exist_ok=True)
    for name, o in ONE.items():
        if want and name not in want: continue
        x, gr = one(name, o, src, out); report(name, f'{out}/{name}.mp3', x, gr=gr, lu=o['lu'])
    for name, o in LOOP.items():
        if want and name not in want: continue
        x, n = stitch(name, o, src, out); report(name, f'{out}/{name}.mp3', x, n)
