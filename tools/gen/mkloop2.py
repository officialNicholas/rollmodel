# a game-ready loop from a song whose repeats are alike but not sample-identical (each pass rendered fresh):
#   1) find the drum hit right at each end (A early, B late), to the millisecond, from the onset of the highs and the lows
#   2) the seam goes a few ms before both hits: a short equal-power crossfade in the tail of the beat before, so the early pass's
#      own hit lands clean and the change hides under it
#   3) the file: the song to the seam, the crossfade, then a guard stretch copied from the early pass, with the loop points
#      inside identical audio (a decoder shifting the timeline a little can't put a click in), the leading silence trimmed
# usage: mkloop2.py name src.wav A B [xfade_ms] [pre_ms]
import sys, json, os, subprocess, numpy as np, warnings
from scipy.io import wavfile
from scipy import signal
warnings.filterwarnings('ignore')
name, path, A, B = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
XF = (float(sys.argv[5]) if len(sys.argv) > 5 else 14) / 1000; PRE = (float(sys.argv[6]) if len(sys.argv) > 6 else 7) / 1000
G = 0.2
sr, raw = wavfile.read(path); a = raw.astype(np.float64) / 32768.0; m = a.mean(1)
def env(x, ms=1.0):
    h = int(sr * ms / 1000); e = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')); return e
bh, ah = signal.butter(4, 2500 / (sr / 2), 'high'); bl, al = signal.butter(4, 160 / (sr / 2), 'low')
EH, EL = env(signal.filtfilt(bh, ah, m)), env(signal.filtfilt(bl, al, m), 3)
def hit(t, span=0.07):
    # the sharpest rise in the highs (or, failing that, the lows) within span of t
    i0, i1 = int((t - span) * sr), int((t + span) * sr); best = None
    for E, w in ((EH, 1.0), (EL, 0.6)):
        seg = np.log(E[i0:i1] + 1e-6); d = np.diff(seg); k = int(np.argmax(np.convolve(d, np.ones(24), 'same'))); s = float(d[max(0, k - 24):k + 24].sum()) * w
        if best is None or s > best[0]: best = (s, (i0 + k) / sr)
    return best[1], best[0]
tA, sAk = hit(A); tB, sBk = hit(B)
iS, B0 = int(round((tA - PRE) * sr)), int(round((tB - PRE) * sr)); Ls = B0 - iS
print(f'{name}: hits at {tA:.4f} (rise {sAk:.2f}) and {tB:.4f} (rise {sBk:.2f}) -> loop {Ls} samples ({Ls / sr:.4f} s)')
hx = int(XF * sr); g = int(G * sr)
out = np.zeros((B0 + g, 2))
out[:B0 - hx] = a[:B0 - hx]
th = np.linspace(0, np.pi / 2, hx, endpoint=False)
out[B0 - hx:B0] = a[B0 - hx:B0] * np.cos(th)[:, None] + a[iS - hx:iS] * np.sin(th)[:, None]
out[B0:B0 + g] = a[iS:iS + g]
lead = np.where(np.abs(out).max(1) > 10 ** (-60 / 20))[0][0]; cut = max(0, lead - int(0.015 * sr)); out = out[cut:]
loopStart = (iS + g // 2 - cut) / sr; loopEnd = (B0 + g // 2 - cut) / sr
f0 = int(0.005 * sr); out[:f0] *= np.linspace(0, 1, f0)[:, None]
pk = np.abs(out).max(); print(f'  file {len(out) / sr:.3f} s, loop {loopStart:.5f} -> {loopEnd:.5f} s, peak {20 * np.log10(pk):.1f} dB')
os.makedirs('music_out', exist_ok=True); wavfile.write(f'music_out/{name}.wav', sr, (np.clip(out, -1, 1) * 32767).astype(np.int16))
i1, i0 = int(round(loopEnd * sr)), int(round(loopStart * sr))
spl = np.concatenate([out[i1 - int(0.5 * sr):i1], out[i0:i0 + int(0.5 * sr)]]).mean(1)
dd = np.abs(np.diff(spl)); jump = dd[int(0.5 * sr) - 3:int(0.5 * sr) + 3].max(); typ = np.percentile(dd, 99.5)
print(f'  splice check: step at the jump {jump:.5f} vs 99.5th pct {typ:.5f}')
pre = np.concatenate([out[:i1], out[i0:i1], out[i0:i0 + int(4 * sr)]])
wavfile.write(f'music_out/{name}_preview.wav', sr, (np.clip(pre, -1, 1) * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'music_out/{name}_preview.wav', '-b:a', '192k', f'music_out/{name}_preview.mp3'], check=True)
meta = json.load(open('music_out/loops.json')) if os.path.exists('music_out/loops.json') else {}
meta[name] = {'a': round(loopStart, 5), 'b': round(loopEnd, 5), 'len': round(len(out) / sr, 4), 'hits': [round(tA - cut / sr, 4), round(tB - cut / sr, 4)], 'seams': [round(i1 / sr, 2), round((i1 + i1 - i0) / sr, 2)], 'rms': round(float(20 * np.log10(np.sqrt((out ** 2).mean()))), 2), 'src': os.path.basename(path), 'A': A, 'B': B}
json.dump(meta, open('music_out/loops.json', 'w'), indent=1)
