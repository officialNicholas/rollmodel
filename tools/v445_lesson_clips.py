"""v445: the lesson cards show the real game (the user: "I want actual images of the game ... real pictures of characters doing the
actions"), and Play online's lock says "Reach rank 2".

- Each card's scene is a clip of the game itself, looping like a GIF: you from behind as the camera has you, on the lesson's canvas,
  doing the move, with the finger drawn into the clip in step with it (art/l_*.webp, animated WebP; captured frame by frame from the
  game, the finger and the Pound button laid over the frames before encoding, so they can never drift apart). Move: steering left and
  right, and a hop on a tap. Rings: rolling through a gold ring, its burst. Slingshot: the hold, the pull down, the launch and the
  landing splat. Out of paint?: rolling into a basin, a tap, hopping out. Ground pound: a tap on Pound, the slam, the rival sent flying.
  Dodge: the rival leaps with its warning ring, a swipe up, you roll clear and its pound lands behind you.
- Play online opens at rank 2 (it opened once the Strokes page had been seen, which itself opens at rank 2). Locked, it says
  "Reach rank 2" (it said "Open Strokes"); its toast, its spoken label and the party's lock say the same."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TV = """const TV = { // (v445) the game itself: clips of the moves, the finger drawn in
  steer: '<img class="tvclip" src="art/l_steer.webp" alt="">', jump: '<img class="tvclip" src="art/l_jump.webp" alt="">',
  rings: '<img class="tvclip" src="art/l_rings.webp" alt="">', sling: '<img class="tvclip" src="art/l_sling.webp" alt="">',
  basin: '<img class="tvclip" src="art/l_basin.webp" alt="">', pound: '<img class="tvclip" src="art/l_pound.webp" alt="">',
  dodge: '<img class="tvclip" src="art/l_dodge.webp" alt="">'
};
"""
CSS = r"""
/* (v445) the lesson cards' clips of the game: they fill their frame */
.tv>img.tvclip{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;background:#E9E6EE}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tlvis .tv{aspect-ratio:16/10}.tlvis.two .tv{aspect-ratio:1/1}.tlvis:not(.two){width:min(100%,calc((100vh - 215px) * 1.6))}.tlvis.two{width:min(100%,calc((100vh - 230px) * 2 + 10px))}}
"""

def apply(s):
    a = s.index("const TV = {\n  steer: "); b = s.index("const LSN_TUNE = ")
    s = s[:a] + TV + s[b:]
    # (fetched as the lesson starts, so a card's clip is there when it comes up)
    s = rep(s, "pips: new Set(), bonus: 0, praiseN: 0 }; tutPipsDraw(); if (AU.xwant) AU.xwant('t_ring');",
               "pips: new Set(), bonus: 0, praiseN: 0 }; tutPipsDraw(); if (AU.xwant) AU.xwant('t_ring'); for (const k in TV) { const im = new Image(); im.src = TV[k].match(/src=\"([^\"]+)\"/)[1]; } /* (v445: the clips) */")
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    # Play online: open at rank 2, and the lock says so
    s = rep(s, "const mpOpen = () => !!(store.abilSeen || (store.tut && store.tut.strokes));",
               "const mpOpen = () => repOf(store.xp || 0).lv >= ABIL_RANK || !!(store.abilSeen || (store.tut && store.tut.strokes)); /* (v445: rank 2 opens it) */")
    s = rep(s, "$('evMatchLock').innerHTML = ABIL_LOCK + (lv < ABIL_RANK ? 'Rank ' + ABIL_RANK : 'Open Strokes');", "$('evMatchLock').innerHTML = ABIL_LOCK + 'Reach rank ' + ABIL_RANK;")
    s = rep(s, "lv < ABIL_RANK ? 'Play online, locked: reach rank ' + ABIL_RANK : 'Play online, locked: open Strokes in the lobby to unlock it'", "'Play online, locked: reach rank ' + ABIL_RANK")
    s = rep(s, "return evToast(c, repOf(store.xp || 0).lv < ABIL_RANK ? 'Reach rank ' + ABIL_RANK : 'Open Strokes in the lobby to unlock it'); }", "return evToast(c, 'Reach rank ' + ABIL_RANK + ' to play online'); }")
    s = rep(s, "const ptLockText = () => repOf(store.xp || 0).lv < ABIL_RANK ? 'Reach rank ' + ABIL_RANK + ' to play with friends' : 'Open Strokes in the lobby to play with friends';",
               "const ptLockText = () => 'Reach rank ' + ABIL_RANK + ' to play with friends';")
    return s
