from PIL import Image
import numpy as np, cv2
SRC = '/root/.claude/uploads/5289d4e8-434a-5c51-91d1-4c1a38d63990/7788721a-image.png'
src = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
mx = src.max(axis=2)
m = (mx > 70).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]); m = (lab == k).astype(np.uint8)
# the icon shape is convex: fill dark details inside it (axle, shadows, handle hole)
cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
hull = cv2.convexHull(max(cnts, key=cv2.contourArea))
m = np.zeros_like(m); cv2.fillPoly(m, [hull], 1)
ys, xs = np.where(m); x0,x1,y0,y1 = xs.min(), xs.max(), ys.min(), ys.max()
cx, cy = (x0+x1)/2, (y0+y1)/2
side = int(min(x1-x0, y1-y0) - 12); L = int(round(cx - side/2)); T = int(round(cy - side/2))
crop = src[T:T+side, L:L+side].copy()
valid = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35,35)))[T:T+side, L:L+side]
def pushpull(img, w):
    if min(img.shape[:2]) <= 2:
        s = (img*w[...,None]).sum((0,1)) / max(w.sum(),1e-6)
        return np.broadcast_to(s, img.shape).copy()
    h, wd = img.shape[:2]; h2, w2 = (h+1)//2, (wd+1)//2
    ip = np.zeros((h2*2, w2*2, 3), np.float32); wp = np.zeros((h2*2, w2*2), np.float32)
    ip[:h,:wd] = img*w[...,None]; wp[:h,:wd] = w
    ws = wp.reshape(h2,2,w2,2).sum((1,3)); isum = ip.reshape(h2,2,w2,2,3).sum((1,3))
    small = np.where(ws[...,None]>0, isum/np.maximum(ws[...,None],1e-6), 0)
    filled = pushpull(small, np.minimum(ws, 1.0))
    up = cv2.resize(filled, (w2*2, h2*2), interpolation=cv2.INTER_LINEAR)[:h,:wd]
    return img*w[...,None] + up*(1-w[...,None])
w = valid.astype(np.float32)
fill = pushpull(crop, w)
# a little smoothing of the fill only, then a soft 3px blend at the seam
fill = cv2.GaussianBlur(fill, (0,0), 3)
wf = cv2.GaussianBlur(w, (0,0), 1.5) * w
res = crop*wf[...,None] + fill*(1-wf[...,None])
# match film grain so the fill isn't flat
rng = np.random.default_rng(7)
res += (rng.standard_normal(res.shape[:2])[...,None]*1.2) * (1-wf[...,None])
im = Image.fromarray(np.clip(res,0,255).astype(np.uint8)).resize((1024,1024), Image.LANCZOS)
im.save(__import__('sys').argv[1] if len(__import__('sys').argv) > 1 else 'icon/AppIcon-1024.png', optimize=True)
print('ok', im.size, im.mode)
