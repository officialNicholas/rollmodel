import sys, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
import glb
j, bn = glb.load(sys.argv[1])
print('nodes', len(j['nodes']), 'meshes', len(j['meshes']), 'skins', len(j.get('skins', [])), 'anims', [(a['name'], len(a['channels'])) for a in j.get('animations', [])])
for i, n in enumerate(j['nodes']):
    print(i, n.get('name'), 'ch', n.get('children'), 'T', np.round(n.get('translation', [0,0,0]), 4).tolist(), 'R', np.round(n.get('rotation', [0,0,0,1]), 3).tolist(), 'S', n.get('scale'), 'mesh' if 'mesh' in n else '', 'skin' if 'skin' in n else '')
for m in j['meshes']:
    for p in m['primitives']:
        print('prim attrs', p['attributes'], 'mat', p.get('material'), 'count', j['accessors'][p['attributes']['POSITION']]['count'], 'idx', j['accessors'][p['indices']]['count'])
print('materials', json.dumps(j['materials'], indent=1)[:2000])
print('textures', j.get('textures'), 'images', [(im.get('mimeType'), j['bufferViews'][im['bufferView']]['byteLength']) for im in j.get('images', [])])
if j.get('skins'):
    s = j['skins'][0]; print('skin joints', s['joints'], 'skeleton', s.get('skeleton'))
for a in j.get('animations', []):
    ts = set()
    for ch in a['channels']:
        sm = a['samplers'][ch['sampler']]; ts.add((j['accessors'][sm['input']]['count'], sm.get('interpolation', 'LINEAR')))
    inp = glb.acc(j, bn, a['samplers'][0]['input']); print('anim', a['name'], 'keys', ts, 'dur', inp.min(), inp.max(), 'targets', sorted(set(ch['target']['path'] for ch in a['channels'])))
