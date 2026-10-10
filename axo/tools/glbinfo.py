import json, struct, sys
def load(p):
    b = open(p, 'rb').read(); mag, ver, ln = struct.unpack('<III', b[:12]); o = 12; js = None; bin_ = None
    while o < ln:
        cl, ct = struct.unpack('<II', b[o:o+8]); d = b[o+8:o+8+cl]
        if ct == 0x4E4F534A: js = json.loads(d)
        else: bin_ = d
        o += 8 + cl
    return js, bin_
for p in sys.argv[1:]:
    j, bn = load(p); print('==', p.split('/')[-1], 'bin', len(bn))
    print('asset', j.get('asset')); print('scenes', len(j.get('scenes', [])), 'nodes', len(j.get('nodes', [])), 'meshes', len(j.get('meshes', [])), 'skins', len(j.get('skins', [])), 'anims', len(j.get('animations', [])), 'materials', len(j.get('materials', [])), 'textures', len(j.get('textures', [])), 'images', len(j.get('images', [])))
    for m in j.get('meshes', []):
        for pr in m['primitives']:
            acc = j['accessors'][pr['attributes']['POSITION']]
            print(' mesh', m.get('name'), 'verts', acc['count'], 'attrs', list(pr['attributes'].keys()), 'idx', j['accessors'][pr['indices']]['count'] if 'indices' in pr else None, 'min', [round(v, 3) for v in acc.get('min', [])], 'max', [round(v, 3) for v in acc.get('max', [])], 'mat', pr.get('material'))
    for i, im in enumerate(j.get('images', [])):
        bv = j['bufferViews'][im['bufferView']] if 'bufferView' in im else None
        print(' image', i, im.get('mimeType'), im.get('name'), bv['byteLength'] if bv else im.get('uri'))
    for mt in j.get('materials', []): print(' material', json.dumps(mt)[:300])
    for s in j.get('skins', []): print(' skin joints', len(s['joints']), 'root', s.get('skeleton'))
    names = [n.get('name') for n in j.get('nodes', [])]; print(' node names', names[:80])
    for a in j.get('animations', []): print(' anim', a.get('name'), 'channels', len(a['channels']))
    for i, n in enumerate(j.get('nodes', [])[:6]): print(' node', i, json.dumps({k: n[k] for k in n if k != 'children'})[:200], 'children', n.get('children'))
