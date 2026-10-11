#!/bin/bash
# merge the runtime into one axo.js (loadMesh, Puppet, Animator), copy the runtime + assets into ws/axo, save the review sheets as axo/v2_*.jpg
set -e
S=/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad
SRC=$S/ws/axo2; DST=$S/ws/axo
# keep the previous attempt's runtime aside (only the first time)
if [ ! -d $DST/old_v1 ]; then mkdir -p $DST/old_v1; for f in axo.js axo_stand.bin axo_stand.json axo_stand.webp axo_crawl.bin axo_crawl.json axo_crawl.webp axo_stand_h.bin axo_stand_h.json preview.html rig.js debug.html ortho.html view.html; do [ -f $DST/$f ] && mv -f $DST/$f $DST/old_v1/ || true; done; fi
rm -f $DST/stand.glb $DST/crawl.glb
# single-module runtime: core + animator (strip the animator's import of the core)
python3 - <<'EOF'
S='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
core = open(S + '/ws/axo2/axo.js').read(); anim = open(S + '/ws/axo2/anim.js').read(); look = open(S + '/ws/axo2/look.js').read()
anim = anim.replace("import * as THREE from 'three';\nimport { Pose, rot, setRot, mirrorQ, DEG } from './axo.js';\n", '')
anim = anim.replace("const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _q = new THREE.Quaternion();", "const _av = new THREE.Vector3(), _av2 = new THREE.Vector3(), _aq = new THREE.Quaternion();")
import re
# the animator's scratch names must not clash with the core's: rename inside the animator part only
anim = re.sub(r'\b_v3\b', '_av3', anim); anim = re.sub(r'\b_v2\b', '_av2', anim); anim = re.sub(r'\b_v\b', '_av', anim); anim = re.sub(r'\b_q\b', '_aq', anim)
core = core.replace("import { axoMaterial } from './look.js';\n", ''); look = look.replace("import * as THREE from 'three';\n", '')
out = core + '\n// ======================================================================\n' + anim + '\n// ======================================================================\n' + look
open(S + '/ws/axo/axo.js', 'w').write(out)
pv = open(S + '/ws/axo2/preview.html').read().replace("import { loadMesh, Puppet } from './axo.js'; import { Animator } from './anim.js'; import { Look, EXPR } from './look.js';", "import { loadMesh, Puppet, Animator, Look, EXPR } from './axo.js';")
open(S + '/ws/axo/preview.html', 'w').write(pv)
print('merged axo.js', len(out), 'bytes')
EOF
cp $SRC/axo_stand.bin $SRC/axo_stand.json $SRC/axo_stand.webp $SRC/axo_crawl.bin $SRC/axo_crawl.json $SRC/axo_crawl.webp $DST/
ls -la $DST
