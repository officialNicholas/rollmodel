# Read the Meshy GLB (one mesh, positions / normals / uv, a baked base colour PNG and a metallic-roughness PNG) into an npz plus the two
# images, untouched (the model's own axes and units).
#   python3 -I glbread.py <in.glb> <out dir>
import json, struct, sys, os
import numpy as np
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
b = open(src, 'rb').read(); assert b[:4] == b'glTF'
cl, = struct.unpack('<I', b[12:16]); js = json.loads(b[20:20 + cl]); o = 20 + cl; bl, = struct.unpack('<I', b[o:o + 4]); bin_ = b[o + 8:o + 8 + bl]
def acc(i):
    a = js['accessors'][i]; v = js['bufferViews'][a['bufferView']]; dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a['componentType']]
    nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]; s = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(bin_, dt, a['count'] * nc, s).reshape(a['count'], nc) if nc > 1 else np.frombuffer(bin_, dt, a['count'], s)
pr = js['meshes'][0]['primitives'][0]; at = pr['attributes']
P = acc(at['POSITION']).astype(np.float64); N = acc(at['NORMAL']).astype(np.float64); UV = acc(at['TEXCOORD_0']).astype(np.float64); T = acc(pr['indices']).astype(np.int64).reshape(-1, 3)
np.savez(out + '/src_mesh.npz', P=P, N=N, UV=UV, T=T)
for k, im in enumerate(js['images']):
    v = js['bufferViews'][im['bufferView']]; data = bin_[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
    open(out + f"/{im['name']}.png", 'wb').write(data)
print('verts', len(P), 'tris', len(T), 'bbox', P.min(0).round(3), P.max(0).round(3), 'uv', UV.min(0).round(3), UV.max(0).round(3), 'images', [im['name'] for im in js['images']])
