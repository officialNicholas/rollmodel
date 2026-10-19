"""v376: the character is never see-through over itself (the pale veil over it climbing out of the paint at the start of a match).

- Each character carries a see-through copy of itself (its ghost, in its colour) that shows only where something stands in front of it,
  so you can still see where it is behind a wall. It was drawn after everything solid, so "something in front" included the character's
  own body. The body puffs out where the ghost doesn't (the paint coat it climbs out of the basin in, and its jelly squash and wobble), so
  the ghost sat a little inside the body, counted as behind it, and was laid over it: a pale, flat copy of the head and body on top of the
  real one, the face showing twice. Most of all at the start of a match (coated, squashed, with the camera close), a little whenever it
  wobbled.
- Now the ghost is drawn before the characters, straight after the stage, so only the stage (walls, crates, the floor) can put it on
  show. Behind a wall it shows as before."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "    const xray = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), ghosts = [];\n",
               "    // (v376) the ghost goes in with the solid things (not transparent, blended by hand), in its order before the bodies (30 < 32): only the\n"
               "    // stage is drawn by then, so only the stage can put it on show. Drawn after the bodies it took the body's own skin, puffed out by the\n"
               "    // coat and the squash where the ghost isn't, for something in front of it, and laid a pale copy of itself over itself\n"
               "    const xray = new THREE.MeshBasicMaterial({ color: col, transparent: false, blending: THREE.CustomBlending, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), ghosts = [];\n")
    return s
