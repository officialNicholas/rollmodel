"""cq02: the Season Conquest level, a greybox to play and iterate: the Keep (the demo's reveal, then the boss flees and a gate lights),
the Aqueduct Run (a raised causeway in an S over a slimed canal: gaps, cracked slabs to pound through, basins on and off the lane, the
collapse chasing you, the boss ahead slamming the lane, diving to slime it and dropping jellets) and the Sunken Plaza (three waves of
jellets, then the turret's lobs onto four valve pads pin the boss for your pounds). Checkpoints, lives per checkpoint, chip damage by
covering its slime, pops of its babies. The runtime is tools/cq02_level.js, after the boss demo. The Season Conquest card opens it."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    js = open(os.path.join(HERE, 'cq02_level.js')).read()
    s = rep(s, "window.conqPreview = conqPreview;\n", "window.conqPreview = conqPreview;\n" + js)
    # the card opens the level
    s = rep(s, "$('evConq').addEventListener('click', uiClick(conqPreview));", "$('evConq').addEventListener('click', uiClick(cqlvOpen)); // (cq02: the level)")
    s = rep(s, '<span class="evbar"><i>Boss demo</i></span>', '<span class="evbar"><i>Greybox</i></span>')
    s = rep(s, '<small>Sunken Keep, boss demo</small>', '<small>Sunken Keep, the level</small>')
    s = rep(s, '<i class="evsoon">Boss demo</i>', '<i class="evsoon">Greybox</i>')
    # the frame, the pound, the knock-out and its respawn, the demo's life reset, leaving
    s = rep(s, "visuals(dt, rdt); cqbTick(dt, rdt);", "visuals(dt, rdt); cqbTick(dt, rdt); cqlvTick(dt, rdt);")
    s = rep(s, "coneBlast(D.x, D.y, D.z, R);", "coneBlast(D.x, D.y, D.z, R); cqlvSlam(D, R);")
    s = rep(s, "else if (D.elimNow) sdOut(D); else respawnBlob(D); } return; }", "else if (D.elimNow) sdOut(D); else if (CQL && D === P) cqlvRespawn(D); else respawnBlob(D); } return; }")
    s = rep(s, "D.outs++; D.outWhy[reason]", "D.outs++; if (CQL && D === P) cqlvLost(reason); D.outWhy[reason]")
    s = rep(s, "else if (Q.koSeen) { Q.koSeen = false; Q.life = 3; cqlShow('gain'); }", "else if (Q.koSeen) { Q.koSeen = false; if (!CQL || Q.life <= 0) { Q.life = 3; cqlShow('gain'); } }")
    s = rep(s, "if (CQP) { mode = CQP.prevMode; CQP = null; cqbEnd(); }", "if (CQP) { mode = CQP.prevMode; CQP = null; cqlvEnd(); cqbEnd(); }")
    s = rep(s, "cqbPanel(); cqbSfxOn();", "cqbPanel(); cqlvPanel(); cqbSfxOn();")
    s = rep(s, "CQP ? 'Season Conquest \\u00b7 boss demo'", "CQP ? (CQL ? CQL_SECS[0].sub : 'Season Conquest \\u00b7 boss demo')")
    # the boss's Hurt flinch costs it nothing in the level (the level's own numbers rule: a pound on the pinned bell, the chips)
    s = rep(s, "else if (e === 'start' && d.move === 'hurt' && B.vis && B.hp > 0) {", "else if (e === 'start' && d.move === 'hurt' && B.vis && B.hp > 0 && !CQL) {")
    # no pick-ups in the level: nothing spawns, no orb, no start item's banner
    s = rep(s, "function itemTick(dt) {", "function itemTick(dt) { if (CQL) return;")
    s = rep(s, "function updateOrb(dt) {", "function updateOrb(dt) { if (CQL) { if (orb.on) orbReset(); return; }")
    s = rep(s, "else if (state === 'play' && !tut) banner('Paint it '", "else if (state === 'play' && !tut && !CQL) banner('Paint it '")
    return s
