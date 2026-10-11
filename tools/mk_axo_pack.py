#!/usr/bin/env python3
"""The axolotl's two bodies (stand and crawl: .bin + .json each, from the axolotl pipeline) as one pack for the game, like the slime's:
'RMA1', the header's length (u32), the header (JSON: each body's metadata and where its data is), then the data. Written as raw bytes
(axo.pack, which the test harness inlines) and as base64 text (axo-pack.txt, which web hosts serve where they won't serve an unknown
binary). usage: mk_axo_pack.py [runtime dir] [out dir]"""
import base64, json, struct, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = sys.argv[1] if len(sys.argv) > 1 else S + '/ws/axo'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/claude'
head, blobs, off = {'meshes': {}}, [], 0
for name in ('stand', 'crawl'):
    b = open(f'{SRC}/axo_{name}.bin', 'rb').read(); meta = json.load(open(f'{SRC}/axo_{name}.json'))
    pad = (-off) % 8; blobs.append(b'\0' * pad); off += pad   # (8-byte aligned, so typed arrays can view it in place)
    head['meshes'][name] = {'meta': meta, 'off': off, 'len': len(b)}; blobs.append(b); off += len(b)
hj = json.dumps(head, separators=(',', ':')).encode()
hj += b' ' * ((-(8 + len(hj))) % 8)   # (the data starts 8-byte aligned too)
pack = b'RMA1' + struct.pack('<I', len(hj)) + hj + b''.join(blobs)
open(OUT + '/axo.pack', 'wb').write(pack); open(OUT + '/axo-pack.txt', 'w').write(base64.b64encode(pack).decode())
print('ok', len(pack), 'bytes,', len(base64.b64encode(pack)), 'as text')
