"""v337: the locker's window twice as close on your character.

- The window framed the whole pad with you standing small in the middle of it, and smaller still with something picked in the Paint
  Shop (its words and button under the window take room, so the camera pulled back further).
- Now the camera comes in twice as close (LK_ZOOM), aimed at you rather than at the pad (LK_TY: the middle of you, hat included), so
  you're twice the size in every view: My Locker, the Paint Shop, and with a pick, upright and sideways. The pad's rim goes out past
  the window's edges. When you hop (a poke), the camera rises with part of the hop, so you stay in the window.
- The close-up on your face (trying on eyes or something for the face) comes in closer to match (LK_FZOOM), so it still zooms in from
  the new view rather than out."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

LK_ZOOM, LK_FZOOM, LK_TY, LK_HOPF = '2', '1.7', '0.4', '0.6'

def apply(s):
    s = rep(s, "const LK_PAD = 0.62; // (the pad in dress mode: a podium, this much of the demo's)\n",
               "const LK_PAD = 0.62; // (the pad in dress mode: a podium, this much of the demo's)\n"
               "// (v337) the dress view this much closer than one that fits the pad, aimed this high (the middle of you, a hat included); the\n"
               "// close-up on your face this much closer than before; it rises this much of a hop with you, so a hop stays in the window\n"
               "const LK_ZOOM = " + LK_ZOOM + ", LK_FZOOM = " + LK_FZOOM + ", LK_TY = " + LK_TY + ", LK_HOPF = " + LK_HOPF + ";\n")
    s = rep(s, "fz = dk ? SGD.fz || 0 : 0, ty = 0.2 + (0.26 + 0.12 * fz - 0.2) * dk,",
               "fz = dk ? SGD.fz || 0 : 0, ty = 0.2 + (LK_TY + (0.38 - LK_TY) * fz - 0.2) * dk + (dk ? LK_HOPF * (SGD.A.D.ip.hop || 0) * dk * (1 - fz) : 0),")
    s = rep(s, "dist = Math.max(R / (0.94 * ht), (R * Math.sin(el) + hc) / (0.9 * vt * fh / r.h)) * (1 + 0.14 * (SGD.zk || 0)),",
               "dist = Math.max(R / (0.94 * ht), (R * Math.sin(el) + hc) / (0.9 * vt * fh / r.h)) * (1 + 0.14 * (SGD.zk || 0)) / (1 + (LK_ZOOM - 1 + (LK_FZOOM - LK_ZOOM) * fz) * dk),")
    return s
