import json, numpy as np
from PIL import Image, ImageDraw
G = json.load(open('rx/geo.json'))
def arr(k, name, n): a = G['geo'][k][name]; return np.array(a, dtype=np.float32).reshape(-1, n) if a else None
for key in ['slime', 'giant', 'turBody', 'turHead']:
    P = arr(key, 'pos', 3); N = arr(key, 'nor', 3); R = arr(key, 'rig', 4); R2 = arr(key, 'rig2', 4); m = G['meta'][{'turBody':'turret','turHead':'turret'}.get(key, key)]
    g0 = m['ground']; H = m['head'][1] + m['head'][3] - g0; Y = (P[:,1] - g0) / H
    print(key, 'meta', m)
    print(' bbox', P.min(0).round(3), P.max(0).round(3))
    sel = (N[:,2] > 0.3) & (R[:,0] < 0.3) & (R[:,1] < 0.05) & (R2[:,0] < 0.05) & (R2[:,1] < 0.05)
    if sel.sum():
        print(' front torso n', sel.sum(), 'x', P[sel,0].min().round(3), P[sel,0].max().round(3), 'y', P[sel,1].min().round(3), P[sel,1].max().round(3), 'Y', Y[sel].min().round(3), Y[sel].max().round(3), 'z', P[sel,2].min().round(3), P[sel,2].max().round(3))
    # front view image: x right, y up, color: head red, ear green, stub blue, spine yellow, torso white; only front facing
    W = 600; img = Image.new('RGB', (W, W), (20, 20, 30)); d = ImageDraw.Draw(img)
    s = W / 2.2
    order = np.argsort(P[:,2])
    for i in order:
        if N[i,2] < 0.0: continue
        x = W/2 + P[i,0]*s; y = W/2 - P[i,1]*s
        c = (255,255,255)
        if R[i,0] > 0.5: c = (220,60,60)
        elif R[i,1] > 0.05: c = (60,200,60)
        elif R2[i,1] > 0.05: c = (60,60,230)
        elif R2[i,0] > 0.05: c = (230,200,40)
        sh = 0.4 + 0.6*N[i,2]; c = tuple(int(v*sh) for v in c)
        d.ellipse((x-2,y-2,x+2,y+2), fill=c)
    # Y grid lines
    for yy in [0.1,0.2,0.3,0.35,0.4,0.5]:
        py = W/2 - (g0 + yy*H)*s; d.line((0,py,W,py), fill=(90,90,120)); d.text((4,py-12), 'Y%.2f'%yy, fill=(200,200,255))
    img.save('rx/geo_front_%s.png' % key)
    # side view (z right, y up)
    img = Image.new('RGB', (W, W), (20, 20, 30)); d = ImageDraw.Draw(img)
    order = np.argsort(-P[:,0])
    for i in order:
        if N[i,0] > 0.05: continue
        x = W/2 + P[i,2]*s; y = W/2 - P[i,1]*s
        c = (255,255,255)
        if R[i,0] > 0.5: c = (220,60,60)
        elif R[i,1] > 0.05: c = (60,200,60)
        elif R2[i,1] > 0.05: c = (60,60,230)
        elif R2[i,0] > 0.05: c = (230,200,40)
        sh = 0.4 + 0.6*max(0,-N[i,0]); c = tuple(int(v*sh) for v in c)
        d.ellipse((x-2,y-2,x+2,y+2), fill=c)
    for yy in [0.1,0.2,0.3,0.35,0.4,0.5]:
        py = W/2 - (g0 + yy*H)*s; d.line((0,py,W,py), fill=(90,90,120)); d.text((4,py-12), 'Y%.2f'%yy, fill=(200,200,255))
    img.save('rx/geo_side_%s.png' % key)
