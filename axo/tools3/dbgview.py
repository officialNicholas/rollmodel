# write a mesh with a per-vertex category (stored as the dominant 'bone') for view.html 'bones' mode
import numpy as np, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from straighten import write_view
def write_cats(dirp, nm, P, T, cats, catnames):
    class MM: pass
    mm = MM(); mm.T = T; write_view(dirp, nm, mm, P)
    meta = json.load(open(dirp + nm + '.json')); buf = bytearray(open(dirp + nm + '.bin', 'rb').read()); o = meta['off']
    si = np.zeros((len(P), 4), np.uint8); si[:, 0] = cats; buf[o[3]:o[3] + si.nbytes] = si.tobytes(); open(dirp + nm + '.bin', 'wb').write(buf)
    meta['bones'] = [{'name': c, 'pos': [0, 0, 0], 'end': [0, 0.1, 0], 'q': [0, 0, 0, 1], 'parent': None} for c in catnames]; json.dump(meta, open(dirp + nm + '.json', 'w'))
