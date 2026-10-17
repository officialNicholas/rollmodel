#!/usr/bin/env python3
"""Image to 3D on Ludo.ai (POST /assets/3d-model). Auth is injected by the session proxy.
  sh_ludo3d.py <in.png> <out.glb> [--faces 3000] [--tex 1024] [--model prop|hero] [--back back.png]
Saves the GLB and the preview snapshots next to it (out_snap_1.webp ...)."""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ludo import submit, download, b64

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--faces', type=int, default=3000); ap.add_argument('--tex', type=int, default=1024)
ap.add_argument('--model', default='prop'); ap.add_argument('--back')
a = ap.parse_args()
body = {'image': b64(a.src), 'model': a.model, 'target_num_faces': a.faces, 'texture_size': a.tex, 'texture_type': 'pbr'}
if a.back: body['back_image'] = b64(a.back)
r = submit('/assets/3d-model', body)
download(r['model_url'], a.out); print(a.out)
for i, u in enumerate(r.get('snapshots') or []):
    p = os.path.splitext(a.out)[0] + '_snap_%d.webp' % (i + 1); download(u, p); print(p)
