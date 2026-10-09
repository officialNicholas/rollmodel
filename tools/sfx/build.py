# render every designed sound, pack them into two sprite sheets (mono and stereo), encode to mp3, and write the index
import sys, json, time, subprocess, importlib, numpy as np, soundfile as sf
import dsp
MODS = ['s_play', 's_ui', 's_magic', 's_vox', 's_ludo']
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/sfx'
GAP = 0.06
import os
os.makedirs(OUT, exist_ok=True)

def render_all():
    clips = {}
    for mn in MODS:
        M = importlib.import_module(mn)
        for name, d in M.REG.items():
            takes = []
            for v in range(d['takes']):
                dsp.seed(abs(hash((name, v, 'v1'))) % (2**31))
                x = dsp.finish(d['fn'](v))
                if d.get('maxlen'): x = dsp.tail(x, d['maxlen'])
                if d['ch'] == 'm': x = dsp.tomono(x)
                elif x.ndim == 1: x = dsp.stereo(x, 0.3)
                x = x * 10 ** ((d['lvl'] - dsp.loud(x)) / 20)
                if np.max(np.abs(x)) > 0.89: x = dsp.limit2(x, 0.89)
                takes.append(x)
            clips[name] = dict(ch=d['ch'], takes=takes, cat=d['cat'], lvl=d['lvl'])
    return clips

def marker(st):
    n = dsp.N(0.004)
    t = np.arange(n) / dsp.SR
    m = 0.9 * np.sin(2 * np.pi * 4000 * t) * np.hanning(n)
    lead = np.zeros(dsp.N(0.03))
    y = np.concatenate([lead, m, np.zeros(dsp.N(0.03))])
    return np.stack([y, y]) if st else y

def first_over(y, thr=0.45):
    a = np.abs(y if y.ndim == 1 else y[0])
    return int(np.argmax(a > thr))

def pack(clips, ch):
    st = ch == 's'
    parts = [marker(st)]
    pos = parts[0].shape[-1]
    idx = {}
    for name, c in clips.items():
        if c['ch'] != ch: continue
        lst = []
        for x in c['takes']:
            lst.append([round(pos / dsp.SR, 5), round(x.shape[-1] / dsp.SR, 5)])
            parts.append(x)
            g = np.zeros((2, dsp.N(GAP))) if st else np.zeros(dsp.N(GAP))
            parts.append(g)
            pos += x.shape[-1] + g.shape[-1]
        idx[name] = lst
    y = np.concatenate(parts, axis=-1)
    mk = first_over(y) / dsp.SR
    return y, idx, mk

t0 = time.time()
clips = render_all()
print('rendered', len(clips), 'sounds,', sum(len(c['takes']) for c in clips.values()), 'takes in %.1fs' % (time.time() - t0))
index = {'v': 1, 'sheets': {}, 'snd': {}}
for ch in ('m', 's'):
    y, idx, mk = pack(clips, ch)
    wav = OUT + '/%s.wav' % ch
    sf.write(wav, y.T if y.ndim == 2 else y, dsp.SR, subtype='FLOAT')
    mp3 = OUT + '/%s.mp3' % ch
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'libmp3lame', '-q:a', '4', '-ar', '48000'] + (['-ac', '1'] if ch == 'm' else ['-ac', '2']) + [mp3], check=True)
    os.remove(wav)
    index['sheets'][ch] = {'mk': round(mk, 5), 'dur': round(y.shape[-1] / dsp.SR, 3)}
    for name, lst in idx.items():
        index['snd'][name] = [ch, lst]
    print(ch, 'sheet %.1fs' % (y.shape[-1] / dsp.SR), os.path.getsize(mp3) // 1024, 'KB')
json.dump(index, open(OUT + '/index.json', 'w'), separators=(',', ':'))
print('index', len(index['snd']), 'sounds', os.path.getsize(OUT + '/index.json'), 'bytes')
