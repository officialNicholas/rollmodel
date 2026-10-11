"""Settle the half beat: bass-note chroma and melody chroma (and their onsets) scored at fine shifts between 14 and 18 beats"""
import numpy as np, sys, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2')
SR = 22050; HOP = 128
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def mag(x, nfft):
    w = np.hanning(nfft).astype(np.float32); n = 1 + (len(x) - nfft) // HOP; out = np.empty((n, nfft // 2 + 1), np.float32)
    for i0 in range(0, n, 2048):
        i1 = min(n, i0 + 2048); idx = np.arange(nfft)[None, :] + HOP * np.arange(i0, i1)[:, None]; out[i0:i1] = np.abs(np.fft.rfft(x[idx] * w, axis=1))
    return out, nfft
def chroma_band(M, nfft, lo, hi):
    f = np.fft.rfftfreq(nfft, 1 / SR); ok = (f > lo) & (f < hi); pc = (np.round(12 * np.log2(f[ok] / 440.0)) + 69) % 12; P = M[:, ok] ** 2
    C = np.stack([P[:, pc == k].sum(1) for k in range(12)], 1); return np.log1p(C / (np.median(C) + 1e-12))
FPS = SR / HOP
S = {}
bt2 = {n: np.load(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/{n}_bt2.npy') for n in ['menu', 'spook']}
for name, a, b in [('menu', 6.928, 43.72223), ('spook', 7.32, 46.21)]:
    x = load('/home/claude/music/' + name + '.mp3'); ia, ib = int(round(a * SR)), int(round(b * SR)); st = np.concatenate([x[:ib], x[ia:ib], x[ia:ib]])
    Mb, nb = mag(st, 8192); Mt, nt = mag(st, 2048)
    # the two STFTs are centred differently: shift the 8192 one by (8192-2048)/2 samples so frame i means the same time
    sh = (8192 - 2048) // 2 // HOP
    bass = chroma_band(Mb, nb, 40, 260); treb = chroma_band(Mt, nt, 300, 3000)
    S[name] = dict(bass=(bass, (8192 / 2) / SR), treb=(treb, (2048 / 2) / SR), s0=b, L=b - a)
G = 48
def grid(name, feat):
    d = S[name]; v, cen = d[feat]; bt = bt2[name]; k = np.arange(len(bt)); b0 = np.interp(d['s0'], bt, k)
    gb = b0 + np.arange(68 * G) / G; ts = np.interp(gb, k, bt); fr = (ts - cen) * FPS
    Cg = np.stack([np.interp(fr, np.arange(len(v)), v[:, j]) for j in range(12)], 1)
    Cg = Cg - Cg.mean(1, keepdims=True); return Cg / (np.linalg.norm(Cg, axis=1, keepdims=True) + 1e-9)
def flux(Cg): d = np.diff(Cg, axis=0, prepend=Cg[-1:]); d[d < 0] = 0; return d
N = 68 * G
for feat in ['bass', 'treb']:
    m, s = grid('menu', feat), grid('spook', feat)
    def score(k): return float((m * np.roll(s, -k, axis=0)).sum(1).mean())
    fm, fs = flux(m), flux(s)
    def fscore(k): a = fm.ravel() - fm.mean(); b = np.roll(fs, -k, axis=0).ravel() - fs.mean(); return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    full = [score(k) for k in range(N)]; kb = int(np.argmax(full))
    print(feat, 'global best shift', round(kb / G, 3), 'score', round(full[kb], 3), '| at 0:', round(full[0], 3), '32:', round(full[32 * G], 3), '48:', round(full[48 * G], 3))
    row = []
    for sh in np.arange(15.0, 17.01, 0.125):
        k = int(round(sh * G)); row.append((round(sh, 3), round(score(k), 3), round(fscore(k), 3)))
    print('  shift / chroma sim / chroma-onset corr:'); print('  ' + '  '.join(f'{a}:{b}/{c}' for a, b, c in row))
