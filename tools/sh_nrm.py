#!/usr/bin/env python3
"""Add a GLB's normal map to its wear-pack entry (glb2pack's default mode leaves it out): sh_nrm.py in.glb entry.json [size] [quality]"""
import sys, struct, json, base64, io
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; size = int(sys.argv[3]) if len(sys.argv) > 3 else 256; q = int(sys.argv[4]) if len(sys.argv) > 4 else 80
b = open(src, 'rb').read(); cl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + cl]); bin0 = 28 + cl
mat = j['materials'][j['meshes'][0]['primitives'][0]['material']]; im = j['images'][j['textures'][mat['normalTexture']['index']]['source']]; v = j['bufferViews'][im['bufferView']]
o = bin0 + v.get('byteOffset', 0); img = Image.open(io.BytesIO(b[o:o + v['byteLength']])).convert('RGB'); img.thumbnail((size, size), Image.LANCZOS)
bo = io.BytesIO(); img.save(bo, 'JPEG', quality=q, optimize=True); e = json.load(open(out)); e['nrm'] = base64.b64encode(bo.getvalue()).decode(); json.dump(e, open(out, 'w'))
print(out, 'normal map', len(e['nrm']), 'chars')
