"""Where the old spook.mp3 sits inside the full Halloween recording (source.wav), and the beat clock of the full recording"""
import sys, subprocess, numpy as np
sys.path.insert(0, '.')
from analyze import SR, stft_mag, onset_env, chroma, FPS
from beats import track
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/'
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
src = load(S + 'spooky/source.wav'); sp = load('/home/claude/music/spook.mp3')
# coarse then fine: correlate a 6 s chunk from inside the old loop
seg = sp[int(12 * SR):int(18 * SR)]
best = (-1, 0)
from numpy.fft import rfft, irfft
n = len(src) + len(seg); nf = 1 << int(np.ceil(np.log2(n)))
c = irfft(rfft(src, nf) * np.conj(rfft(seg, nf)), nf)[:len(src) - len(seg)]
norm = np.sqrt(np.convolve(src ** 2, np.ones(len(seg)), 'valid')[:len(c)] * (seg ** 2).sum()) + 1e-9
cc = c / norm; k = int(np.argmax(cc)); print('chunk at 12 s of spook.mp3 is at %.4f s in source.wav (corr %.3f) -> spook.mp3 t=0 is source %.4f s' % (k / SR, cc[k], k / SR - 12))
for t in [2, 30, 44]:
    seg = sp[int(t * SR):int((t + 3) * SR)]; c = irfft(rfft(src, nf) * np.conj(rfft(seg, nf)), nf)[:len(src) - len(seg)]
    norm = np.sqrt(np.convolve(src ** 2, np.ones(len(seg)), 'valid')[:len(c)] * (seg ** 2).sum()) + 1e-9; cc = c / norm; k = int(np.argmax(cc))
    print('  spook.mp3 %4.1f s -> source %.4f s (corr %.3f), offset %.4f' % (t, k / SR, cc[k], k / SR - t))
M = stft_mag(src); e = onset_env(M); bt = track(e, 105.0); np.save(S + 'music2/src_bt.npy', bt); np.save(S + 'music2/src_e.npy', e); np.save(S + 'music2/src_C.npy', chroma(M))
ib = np.diff(bt); print('source: dur %.2f s, beats %d, median bpm %.2f' % (len(src) / SR, len(bt), 60 / np.median(ib)))
print('  local bpm per 8 beats:', [round(60 / float(np.mean(ib[i:i + 8])), 1) for i in range(0, len(ib) - 8, 8)])
