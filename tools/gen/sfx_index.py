# put the sheet index (with the calibrated level of each sound) into the game
import json, re, sys
p = '/home/claude/paint-the-canvas.html'
idx = json.load(open('/home/claude/sfx/index.json'))
gains = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
out = {'sheets': idx['sheets'], 'snd': {}}
for k, (ch, takes) in idx['snd'].items():
    out['snd'][k] = [ch, takes, round(gains.get(k, 1.0), 4)]
js = json.dumps(out, separators=(',', ':'))
s = open(p, encoding='utf-8').read()
a = s.index('/*SFXI*/') + len('/*SFXI*/'); b = s.index('/*SFXI_END*/')
s = s[:a] + js + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('index in', len(js), 'bytes,', len(out['snd']), 'sounds')
