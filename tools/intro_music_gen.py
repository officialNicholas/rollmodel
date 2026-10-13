#!/usr/bin/env python3
"""v257 intro: ask Ludo.ai for the intro music material. Usage: intro_music_gen.py <out.mp3> <duration> "<description>" [request_id]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ludo
out, dur, desc = sys.argv[1], int(sys.argv[2]), sys.argv[3]
body = {'description': desc, 'duration': dur}
if len(sys.argv) > 4: body['request_id'] = sys.argv[4]
r = ludo.submit('/audio/music', body); r = r[0] if isinstance(r, list) else r
print(json.dumps({k: v for k, v in r.items() if k != 'url'})[:400])
ludo.download(r['url'], out); print(out, r['url'])
