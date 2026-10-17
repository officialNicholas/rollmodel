# cq01: the Conquest level back on top of v335

`tools/cq01_conquest_restore.py` applies the ten v309 to v319 Conquest modules, in v319's order, after the v335 release list. Two anchors had moved since v319, both from v332_lesson_perf: the last pass's shader uniforms and the edge overlay's condition. cq01 swaps those anchors for today's form; the old modules stay untouched.

Build (test page): `EXTRA=cq01_conquest_restore BASE=<v259 page> VER=259:cq python3 tools/q260.py game/_cq.html --test`

Preview page for the Conquest artifact: `BASE=<v259 page> python3 tools/cq/mk_preview.py <out>/index.html "<label>"`. It seeds a first visit's save so it starts at the menu. The assets are game/'s files (and music/spook.mp3, which the main artifact holds).

Probe: serve game/ on :8765, then `node tools/cq/shot.mjs _cq.html <outdir> [w h]` with STEPS (` ~ `-separated: `e=<js>`, `w=<ms>`, `s=<name>`, `c=<selector>`, `t=x,y`, `f=<seconds>`). `f` fast-forwards game time without drawing, because software rendering in the container runs at about 3 fps. Timers run on real time, so fast-forward in 1 s steps with short waits between them.

Checked in Chromium, upright (390x844) and sideways (844x390):
- the card opens the Sunken Keep;
- the entrance plays: the charge, the stare, the roar and the bar;
- the fight works: the lives, the moves panel, Slam, Sea mines, and Defeat with its "Boss defeated!" stamp;
- Pause > Menu lets the boss go, and a regular match starts after it;
- there are no page errors.
