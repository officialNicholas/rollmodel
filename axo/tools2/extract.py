# extract the user's rigged standing GLB: mesh, mixamo skin (joint idx/weights), node hierarchy with rest TRS, inverse bind matrices, clips
import sys, json, io, numpy as np
from PIL import Image
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
import glb
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
IN = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/in2/x/Meshy_AI_Rigged_Axolotl_Refine_biped/Meshy_AI_Rigged_Axolotl_Refine_biped_Animation_'
out = {}
for clip in ('Walking', 'Running'):
    j, bn = glb.load(IN + clip + '_withSkin.glb')
    if clip == 'Walking':
        pr = j['meshes'][0]['primitives'][0]
        P = glb.acc(j, bn, pr['attributes']['POSITION']); N = glb.acc(j, bn, pr['attributes']['NORMAL']); UV = glb.acc(j, bn, pr['attributes']['TEXCOORD_0'])
        JN = glb.acc(j, bn, pr['attributes']['JOINTS_0']); WT = glb.acc(j, bn, pr['attributes']['WEIGHTS_0']); I = glb.acc(j, bn, pr['indices'])
        sk = j['skins'][0]; joints = sk['joints']; ibm = glb.acc(j, bn, sk['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)  # column-major -> row-major
        nodes = j['nodes']; names = [nodes[i]['name'] for i in joints]
        par = []
        for jn in joints:
            p = [k for k, n in enumerate(nodes) if jn in n.get('children', [])]; par.append(joints.index(p[0]) if p and p[0] in joints else -1)
        T = np.array([nodes[i].get('translation', [0, 0, 0]) for i in joints], float); Rq = np.array([nodes[i].get('rotation', [0, 0, 0, 1]) for i in joints], float)
        root_scale = 0.01
        print('names', names); print('par', par)
        print('verts', len(P), 'tris', len(I) // 3, 'bbox', P.min(0), P.max(0), 'JN dtype', JN.dtype, 'WT', WT.dtype, WT.min(), WT.max(), 'sum', WT.sum(1).min(), WT.sum(1).max())
        print('joint usage', {names[k]: int(((JN == k) & (WT > 0.01)).sum()) for k in range(len(names))})
        im = Image.open(io.BytesIO(glb.image(j, bn, 0))); print('tex', im.size, im.mode); im.save(D + 'stand_tex.png')
        np.savez(D + 'stand_src.npz', P=P, N=N, UV=UV, JN=JN, WT=WT, I=I, ibm=ibm, names=names, par=par, T=T, Rq=Rq)
    a = j['animations'][0]; chans = {}
    for ch in a['channels']:
        sm = a['samplers'][ch['sampler']]; tn = ch['target']['node']
        if tn in joints: chans.setdefault(names[joints.index(tn)], {})[ch['target']['path']] = (glb.acc(j, bn, sm['input']).copy(), glb.acc(j, bn, sm['output']).copy())
    out[clip] = chans
    print(clip, 'channels for', len(chans), 'joints; hips T range', chans['mixamorig:Hips']['translation'][1].min(0), chans['mixamorig:Hips']['translation'][1].max(0), 'times', chans['mixamorig:Hips']['rotation'][0][:3], '...', chans['mixamorig:Hips']['rotation'][0][-1])
np.save(D + 'clips.npy', out, allow_pickle=True)
