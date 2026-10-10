# minimal GLB reader (json + bin, accessors incl. MAT4)
import json, struct, numpy as np
CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8, 5122: np.int16, 5120: np.int8}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
def load(p):
    b = open(p, 'rb').read(); o = 12; js = bn = None
    while o < len(b):
        cl, ct = struct.unpack('<II', b[o:o+8]); d = b[o+8:o+8+cl]
        if ct == 0x4E4F534A: js = json.loads(d)
        else: bn = d
        o += 8 + cl
    return js, bn
def acc(j, bn, i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); k = NC[a['type']]; n = a['count'] * k
    arr = np.frombuffer(bn, CT[a['componentType']], n, off)
    if a.get('normalized'): arr = arr.astype(np.float32) / np.iinfo(CT[a['componentType']]).max
    return arr.reshape(a['count'], k) if k > 1 else arr
def image(j, bn, k):
    im = j['images'][k]; bv = j['bufferViews'][im['bufferView']]; return bn[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
