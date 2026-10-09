# the Ludo takes: the blob's voice and the gameplay effects, loaded from the generated clips and trimmed. Registered last, so they
# replace the synthesized designs of the same name (level and channel kept from those, so the calibrated gains still hold)
import glob, os, subprocess, importlib, numpy as np
from dsp import *
import dsp
LA = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/la'
REG = {}
OLD = {}
for mn in ('s_play', 's_ui', 's_magic', 's_vox'): OLD.update(importlib.import_module(mn).REG)

def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', f, '-ac', '1', '-ar', str(dsp.SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(float)

def env_of(x, ms=8):
    w = max(1, N(ms / 1000)); return np.convolve(np.abs(x), np.ones(w) / w, 'same')

def trim_lead(x, thr_db=-40):
    e = env_of(x); th = 10 ** (thr_db / 20) * (e.max() + 1e-9); i = int(np.argmax(e > th)); return x[max(0, i - N(0.004)):]

def first_phrase(x, maxlen, gap=0.07, thr_db=-30):
    """the first burst of a voice clip: from its onset to the first real pause, capped"""
    x = trim_lead(x); e = env_of(x, 12); th = 10 ** (thr_db / 20) * (e.max() + 1e-9)
    quiet = e < th; n = N(gap); run = 0; end = len(x)
    for i in range(N(0.08), len(x)):
        run = run + 1 if quiet[i] else 0
        if run >= n: end = i - n; break
    end = min(end, N(maxlen)); return fade(x[:end], 0.003, min(0.06, maxlen * 0.25))

def reg(name, files, kind):
    o = OLD.get(name, {}); lvl = o.get('lvl', -15.0); ch = o.get('ch', 'm'); maxlen = o.get('maxlen')
    def fn(v, files=files, kind=kind, maxlen=maxlen):
        x = load(files[v % len(files)])
        if kind == 'vox': x = first_phrase(x, (maxlen or 0.6) + 0.25)
        else: x = trim_lead(x, -45); x = fade(x, 0.002, 0.02)
        if x.ndim == 1 and ch == 's': x = stereo(x, 0.3)
        return x
    REG[name] = dict(fn=fn, takes=len(files), ch=ch, lvl=lvl, cat=o.get('cat', kind), maxlen=(maxlen + 0.25) if (kind == 'vox' and maxlen) else maxlen)

names = {}
for f in sorted(glob.glob(LA + '/sfx/*_[0-9].mp3')): names.setdefault(os.path.basename(f).rsplit('_', 1)[0], []).append(f)
for n, fs in names.items(): reg(n, fs, 'sfx')
vox = {}
for f in sorted(glob.glob(LA + '/vox/vox_*_[0-9].mp3')): vox.setdefault(os.path.basename(f).rsplit('_', 1)[0], []).append(f)
for n, fs in vox.items(): reg(n, fs, 'vox')
