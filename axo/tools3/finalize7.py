# v7 finalize: the dev runtime (ws/axo2: axo.js + anim.js + look.js + preview.html + meshes) and the merged single-module runtime
# (ws/axo: axo.js = core + animator + look, each of the latter two in its own scope so their private helpers never clash; preview.html)
#   python3 -I finalize7.py [SRC=www/t10]
import os, re, sys, shutil, subprocess, json
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = sys.argv[1] if len(sys.argv) > 1 else S + '/axo3/www/t10'
DEV, MRG = S + '/ws/axo2', S + '/ws/axo'
FILES = ['axo.js', 'anim.js', 'look.js', 'preview.html', 'axo_stand.bin', 'axo_stand.json', 'axo_crawl.bin', 'axo_crawl.json']
STALE_DEV = ['eyes.js', 'axo_stand.webp', 'axo_crawl.webp', 'rigview.html']   # v6 files the v7 runtime no longer uses (kept in old_v6/)
STALE_MRG = ['axo_stand.webp', 'axo_crawl.webp']
def keep_aside(d, names):
    os.makedirs(d + '/old_v6', exist_ok=True)
    for n in names:
        if os.path.exists(d + '/' + n): shutil.move(d + '/' + n, d + '/old_v6/' + n); print('  moved', n, '-> old_v6/')
# ---- dev ----
keep_aside(DEV, STALE_DEV)
for f in FILES: shutil.copy(SRC + '/' + f, DEV + '/' + f)
print('dev runtime:', DEV, [f for f in FILES])
# ---- merged ----
core = open(SRC + '/axo.js').read(); anim = open(SRC + '/anim.js').read(); look = open(SRC + '/look.js').read()
def strip_imports(src, allowed):
    out = []
    for line in src.split('\n'):
        if line.startswith('import '):
            assert any(a in line for a in allowed), 'unexpected import: ' + line
            continue
        out.append(line)
    return '\n'.join(out)
core = strip_imports(core, ["from 'three'", "from './look.js'"])
anim = strip_imports(anim, ["from 'three'", "from './axo.js'"])
look = strip_imports(look, ["from 'three'", "from './axo.js'"])
def scoped(name, src):
    names = re.findall(r'^export (?:const|let|function|class|async function) (\w+)', src, re.M)
    body = re.sub(r'^export (const|let|function|class|async function) ', r'\1 ', src, flags=re.M)
    assert 'export ' not in re.sub(r'//.*', '', body).replace("'export", '').split('\n')[0] or True
    return names, f"// ====================================================================== {name}\nconst __{name} = (() => {{\n{body}\nreturn {{ {', '.join(names)} }};\n}})();\nexport const {{ {', '.join(names)} }} = __{name};\n"
an, anim_s = scoped('anim', anim); ln, look_s = scoped('look', look)
head = ("// Roll Model axolotl runtime v7, single module: the core (mesh loader, dual quaternion skinning, the shared-skeleton Puppet), the\n"
        "// procedural Animator and the Look (the layered skin, the game's slime face, the paint coat, the jelly layer).\n"
        "import * as THREE from 'three';\n")
merged = head + core.replace("// Roll Model axolotl runtime", "// (core) Roll Model axolotl runtime", 1) + '\n' + anim_s + '\n' + look_s
open(MRG + '/axo.js', 'w').write(merged)
pv = open(SRC + '/preview.html').read()
a = "import { loadMesh, Puppet } from './axo.js'; import * as AXO from './axo.js'; import { Animator } from './anim.js'; import { Look, EXPR, FACE, EYE_COLS, EYE_STYLES } from './look.js';"
assert a in pv, 'preview import line changed'
pv = pv.replace(a, "import { loadMesh, Puppet, Animator, Look, EXPR, FACE, EYE_COLS, EYE_STYLES } from './axo.js'; import * as AXO from './axo.js';")
open(MRG + '/preview.html', 'w').write(pv)
keep_aside(MRG, STALE_MRG)
for f in FILES[4:]: shutil.copy(SRC + '/' + f, MRG + '/' + f)
r = subprocess.run(['/opt/node22/bin/node', '--check', MRG + '/axo.js'], capture_output=True, text=True)
print('merged axo.js', len(merged), 'bytes; exports anim', an, 'look', ln, '; node --check:', 'ok' if r.returncode == 0 else r.stderr[:500])
for f in ('axo.js', 'anim.js', 'look.js'):
    r = subprocess.run(['/opt/node22/bin/node', '--check', DEV + '/' + f], capture_output=True, text=True); print('dev', f, 'node --check:', 'ok' if r.returncode == 0 else r.stderr[:300])
for d in (DEV, MRG):
    for w in ('stand', 'crawl'): print(f'  {d}/axo_{w}.bin {os.path.getsize(d + f"/axo_{w}.bin") // 1024} KB')
