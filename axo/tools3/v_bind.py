# bind-pose joint check of one runtime mesh in www/rb: hind and front left limbs from six directions each
import sys, asyncio; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(name, out, hind=(0.25, 0.12, -0.80), front=(0.36, 0.15, -0.02), dist=0.9):
    cells = []
    for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.5, 'bottom'), (3.14, 0.05, 'back'), (0, 0.05, 'front'), (1.57, 0.05, 'side out'), (2.4, 0.4, '3/4 back')):
        cells.append((f"(async()=>{{await V.show('{name}','flat',{{joints:true, jr:0.008, only:'^(thigh|shin|foot|toes|hips|tail1|spine)'}}); V.view({yaw},{pitch},{dist},{hind[0]},{hind[1]},{hind[2]},30);}})()", 'hind L bind ' + nm))
    for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.5, 'bottom'), (1.57, 0.05, 'side out'), (0, 0.05, 'front'), (0.8, 0.35, '3/4 front'), (2.4, 0.3, '3/4 back')):
        cells.append((f"(async()=>{{await V.show('{name}','flat',{{joints:true, jr:0.008, only:'^(shoulder|upperarm|forearm|hand|chest|neck|spine1)'}}); V.view({yaw},{pitch},{dist},{front[0]},{front[1]},{front[2]},30);}})()", 'front L bind ' + nm))
    asyncio.run(render('http://localhost:8811/view.html?d=/rb/', cells, 6, 400, 400, out, shot_js='V.shot()', size_js='V.size(400,400)'))
if __name__ == '__main__': run(sys.argv[1], sys.argv[2])
