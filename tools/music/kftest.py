import sys; sys.path.insert(0, '.')
import numpy as np, subprocess
import rb
from rb import lib, FP, U
sr = 48000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', '/home/claude/music/spook.mp3', '-ac', '2', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
mus = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()[:, :sr * 20]
n = mus.shape[1]
# a wobbly map like the real one: anchors every 0.5714 s, local ratio 0.947 +- 1 percent
ain = np.arange(0.5714, 19.5, 0.5714); rng = np.random.RandomState(3)
loc = 0.947 * (1 + 0.01 * np.sin(np.arange(len(ain)) * 0.4))
aout = np.concatenate([[ain[0] * 0.947], ain[0] * 0.947 + np.cumsum(np.diff(ain) * loc[1:])])
ratio = (aout[-1] + (n / sr - ain[-1]) * 0.947) / (n / sr)
clk = np.zeros((1, n), np.float32)
for t in ain: i = int(round(t * sr)); clk[0, i:i + 16] = 1.0
def run(x, finer, precise=False):
    if precise: rb.FASTER = 0x10
    else: rb.FASTER = 0
    y, eng = rb.stretch(x, sr, ratio, (ain * sr).round(), (aout * sr).round(), finer=finer)
    return y, eng
for finer, precise in [(True, False), (False, True), (False, False)]:
    # clicks alone, then clicks as a third channel next to the music
    for mode in ['alone', 'with music']:
        x = clk if mode == 'alone' else np.concatenate([mus, clk])
        y, eng = run(x, finer, precise)
        e = y[-1]; err = []
        for t in aout:
            j = int(round(t * sr)); w = e[max(0, j - 1200):j + 1200]; k = int(np.argmax(w)) + max(0, j - 1200); err.append((k - j) / sr * 1000)
        err = np.array(err[1:-1])
        print('R%d%s %-10s err ms: mean %+.2f  sd %.2f  max %.2f' % (eng, ' precise' if precise else '', mode, err.mean(), err.std(), np.abs(err).max()))
