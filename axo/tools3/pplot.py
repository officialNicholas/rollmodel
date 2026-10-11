# tiny PIL plotter: scatter / polyline in data coordinates
from PIL import Image, ImageDraw
import numpy as np
class Plot:
    def __init__(s, xr, yr, W=900, flipy=True):
        s.xr, s.yr = xr, yr; s.W = W; s.H = int(W * (yr[1] - yr[0]) / (xr[1] - xr[0])); s.im = Image.new('RGB', (s.W, s.H), 'white'); s.d = ImageDraw.Draw(s.im); s.flipy = flipy
    def tx(s, x, y):
        X = (np.asarray(x) - s.xr[0]) / (s.xr[1] - s.xr[0]) * (s.W - 1); Y = (np.asarray(y) - s.yr[0]) / (s.yr[1] - s.yr[0]) * (s.H - 1)
        return X, (s.H - 1 - Y) if s.flipy else Y
    def scatter(s, x, y, col=(0, 0, 0), r=1):
        X, Y = s.tx(x, y)
        for a, b, c in zip(X, Y, col if (isinstance(col, np.ndarray) and col.ndim == 2) else [col] * len(X)):
            s.d.ellipse([a - r, b - r, a + r, b + r], fill=tuple(int(v) for v in c))
    def line(s, x, y, col=(0, 0, 0), w=2):
        X, Y = s.tx(x, y); s.d.line(list(zip(X.tolist(), Y.tolist())), fill=col, width=w)
    def text(s, x, y, t, col=(0, 0, 0)):
        X, Y = s.tx([x], [y]); s.d.text((float(X[0]), float(Y[0])), t, fill=col)
    def save(s, f): s.im.save(f)
def jet(v):
    v = np.clip(np.asarray(v, float), 0, 1); r = np.clip(1.5 - np.abs(4 * v - 3), 0, 1); g = np.clip(1.5 - np.abs(4 * v - 2), 0, 1); b = np.clip(1.5 - np.abs(4 * v - 1), 0, 1)
    return (np.stack([r, g, b], 1) * 255).astype(int)
