# check-in contact sheets of the current state (t9 runtime: v7 meshes, DQS, v7 look; animation still the v6/t7 animator)
import asyncio, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
URL = 'http://localhost:8811/t9/preview.html?manual'; OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo_checkin/'
def st(state, settle, cam, lab, extra=''):
    return (f"axo.setLook(0,0); axo.setState('{state}'); axo.step(1/60,{settle}); {extra} axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},30);", lab)
A = [st('stand', 120, (0.55, 0.12, 3.6, 0.85, 0, 0), 'standing idle'),
     st('crawl', 150, (0.85, 0.42, 4.6, 0.3, 0, -0.55), 'crawl cycle f0'),
     ("axo.step(1/60,18); axo.view(0.85,0.42,4.6,0.3,0,-0.55,30);", 'crawl cycle f18 (0.30 s later)'),
     ("axo.step(1/60,18); axo.view(0.85,0.42,4.6,0.3,0,-0.55,30);", 'crawl cycle f36 (0.60 s later)'),
     st('pound', 90, (0.55, 0.12, 4.4, 1.0, 0, 0), 'ground pound pose (old pose, not yet reworked)'),
     st('jetpack', 90, (0.55, 0.12, 4.4, 1.05, 0, 0), 'jetpack pose (old pose, not yet reworked)'),
     st('crouch', 90, (0.55, 0.15, 3.6, 0.6, 0, 0), 'crouch pose (old pose, not yet reworked)'),
     st('stand', 120, (0.0, 0.02, 1.45, 1.27, 0, 0.25), 'face close-up, standing'),
     st('crawl', 150, (0.25, 0.3, 1.7, 0.55, 0.05, 0.4), 'face close-up, crawl (head pitched down by the gait)')]
B = [st('stand', 120, (0.75, 0.3, 4.6, 0.55, 0, -0.35), 'stand -> crawl: before (stand idle)')]
for f in (8, 8, 8, 8, 8, 10, 20):
    B.append((f"{'axo.setState(\"crawl\");' if len(B) == 1 else ''} axo.step(1/60,{f}); axo.view(0.75,0.3,4.6,0.55,0,-0.35,30);", ''))
acc = 0
for i in range(1, len(B)):
    acc += (8, 8, 8, 8, 8, 10, 20)[i - 1]; B[i] = (B[i][0], f'stand -> crawl  +{acc} frames ({acc / 60:.2f} s)')
asyncio.run(render(URL, A, 3, 520, 520, OUT + 'checkin_poses.png', size_js='axo.size(520,520)', title='v7 work in progress: rig + materials + face (animation of pound / jetpack / crouch / transition not yet reworked)'))
asyncio.run(render(URL, B, 4, 480, 480, OUT + 'checkin_transition.png', size_js='axo.size(480,480)', title='stand -> crawl transition as it is now (v6 transition logic on the v7 meshes; to be redesigned)'))
