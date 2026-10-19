"""v359: no canvas set for the second match, and playing with friends opens with Play online.

- The second match's canvas vote is a plain vote, like every other: your pick and the rivals' go in and whichever comes up most is
  drawn (a tie is drawn at random). It used to be set to Sludge Sewer: the rival's vote was made Sludge Sewer, and it always won.
- Playing with friends is locked until Play online opens (rank 2, once you've seen the Strokes page, which comes up then): Showdown and
  Time trial open at rank 2 as before. Until then a friend's Duel button shows a lock and says when it opens. A friend who's under rank 2
  has no Duel button. A duel invite that comes in while you're locked is turned down for you, so the friend who sent it is told you
  can't play right now, and it never shows.
- Ol' Bloop's rank 2 card (the way into Strokes) and his rank 3 card wait while the Friends page is open, then come a beat after it
  closes. Opened in the second before the card, Friends had the card pop over it, and Show me opened Strokes underneath it."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the second match's vote: no canvas set for it
    s = rep(s, "  // your vote is the canvas you picked; the rivals' are their own (the lesson: the rival's is Sludge Sewer, and it's the one drawn)\n",
               "  // your vote is the canvas you picked; the rivals' are their own; the one that comes up most is drawn (v359: in the second match too)\n")
    s = rep(s, "  const tutV = tutPh() === 'vote' ? TUT_M2 : null;\n  for (const D of who.slice(1)) votes.set(D, tutV && D === H ? tutV : VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]);",
               "  for (const D of who.slice(1)) votes.set(D, VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]);")
    s = rep(s, "  const win = tutV || (lead.length === 1 ? lead[0] : lead[(Math.random() * lead.length) | 0]);",
               "  const win = lead.length === 1 ? lead[0] : lead[(Math.random() * lead.length) | 0];")
    s = rep(s, "const TUT_SLOW = 0.35, TUT_M2 = 'sewer'; // (the canvas the lesson's vote lands on: the second match is on Sludge Sewer)",
               "const TUT_SLOW = 0.35;")
    # ---- playing with friends: a friend's Duel button is locked until Play online opens (and a friend under rank 2 has none)
    s = rep(s, "  if (!NET_URL || !f.online || f.status !== 'lobby') return ''; const w = ON.inv && ON.inv.to === f.id, n = frEsc(hdOf(f.name));",
               "  if (!NET_URL || !f.online || f.status !== 'lobby' || (f.rank != null && (f.rank | 0) < ABIL_RANK)) return ''; const w = ON.inv && ON.inv.to === f.id, n = frEsc(hdOf(f.name));\n"
               "  if (!mpOpen()) return '<button class=\"frb ghost lk\" data-on=\"duellock\" type=\"button\" aria-disabled=\"true\" aria-label=\"Duel ' + n + ', locked\">' + ABIL_LOCK + 'Duel</button>'; // (v359: you play friends once Play online opens)")
    s = rep(s, "  else if (a === 'duel') { const f = FR.box && FR.box.friends.find(x => x.id === id); if (f) onlineInvite(f); }",
               "  else if (a === 'duel') { const f = FR.box && FR.box.friends.find(x => x.id === id); if (f) onlineInvite(f); }\n"
               "  else if (a === 'duellock') { AU.nope(); buzz(8); frToast('<span>' + (repOf(store.xp || 0).lv < ABIL_RANK ? 'Reach rank ' + ABIL_RANK + ' to play with friends' : 'Open Strokes in the lobby to play with friends') + '</span>'); }")
    s = rep(s, "  if (!NET_URL || !f || !f.id || !FR.me || state !== 'menu' || (ON.gate && !ON.gate())) return;\n  if (FR.open) closeFriends();",
               "  if (!NET_URL || !f || !f.id || !FR.me || state !== 'menu' || (ON.gate && !ON.gate()) || !mpOpen()) return;\n  if (FR.open) closeFriends();")
    # ---- a duel invite while you're locked: turned down for you (the sender hears you can't play right now), never shown
    s = rep(s, "fresh = list.filter(i => !ON.seen.has(i.id));\n",
               "fresh = list.filter(i => !ON.seen.has(i.id));\n"
               "    if (list.length && !mpOpen()) { for (const i of list) { ON.nope.add(i.id); sbRpc('rm_answer_invite', { p_id: i.id, p_accept: false }).catch(() => {}); } list.length = 0; fresh.length = 0; } // (v359: not till Play online opens)\n")
    s = rep(s, ".frrow .frbtns .frb.go.onwt{background:rgba(23,19,32,.07);color:var(--black);box-shadow:none}",
               ".frrow .frbtns .frb.go.onwt{background:rgba(23,19,32,.07);color:var(--black);box-shadow:none}\n"
               ".frrow .frbtns .frb.lk{color:rgba(23,19,32,.55)}.frrow .frbtns .frb.lk svg{flex:none;width:13px;height:13px} /* (v359: Duel, locked till Play online opens) */")
    # ---- Ol' Bloop's rank 2 and rank 3 cards: not over the Friends page, and a fresh beat of the lobby once it's closed
    for f in ('tutCommsDue', 'tutStrokesDue'):
        s = rep(s, "function " + f + "() { return tutPh() === 'done' && ", "function " + f + "() { return $('friendsModal').hidden && tutPh() === 'done' && ") # (v359)
    s = rep(s, "if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } /* (a beat of the lobby, then the praise) */",
               "if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } else tutStrokesAt = 0; /* (a beat of the lobby, then the praise; v359: a fresh beat after the Friends page) */")
    s = rep(s, "if (performance.now() - tutCommsAt > 1200) { menu.classList.add('tutoring'); tutWelcome(); } return; } /* (rank 3: commissions open) */",
               "if (performance.now() - tutCommsAt > 1200) { menu.classList.add('tutoring'); tutWelcome(); } return; } else tutCommsAt = 0; /* (rank 3: commissions open) */")
    return s
