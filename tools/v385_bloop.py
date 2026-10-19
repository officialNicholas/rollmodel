"""v385: Ol' Bloop's new look everywhere he turns up, in three moods.

- The pictures are the user's (made into the coach frame by tools/v385_bloop_art.py): normal, talking and making a point, a finger
  up; serious, arms crossed; laughing, eyes shut and hands out. They replace the old picture in the corner of the screen, on the
  lesson's plate, over the lesson's cards, and on the Events page's little round face.
- Which one: his line decides. A win or a gift ("Learned!", "It's ready!", "You found a flower", "You earned dabs", "All yours!",
  "Hey, rookie!", "Take a look around") gets the laugh; a warning ("Out of paint!", "The sun's coming out!", "Rivals pound too",
  "Missiles eliminate players!", "Don't forget to slingshot") gets the serious one; everything else (how to do a thing) the normal,
  pointing one. The lesson's cards laugh at the news (new modes, commissions, more to learn) and look serious for "Now win it!".
- All three are loaded (and given his soft shadow) as the game starts, so a change of mood never shows an empty frame."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    i = s.index("{ const im = new Image(); im.onload = () => { try { const W = im.naturalWidth, H = im.naturalHeight, c = document.createElement('canvas');")
    j = s.index("im.src = 'art/coach.webp'; }", i) + len("im.src = 'art/coach.webp'; }")
    s = s[:i] + (
        "// (v385) his three moods: normal (talking, making a point), serious, laughing. Each baked with his shadow as it loads\n"
        "const COACH_ART = { normal: 'art/coach.webp', serious: 'art/coach_serious.webp', laugh: 'art/coach_laugh.webp' }, coachBaked = {};\n"
        "for (const m in COACH_ART) { const im = new Image(); im.onload = () => { try { const W = im.naturalWidth, H = im.naturalHeight, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');\n"
        "    g.shadowColor = 'rgba(23,19,32,.35)'; g.shadowBlur = Math.round(W / 16); g.drawImage(im, 0, 0);\n"
        "    c.toBlob(bl => { if (!bl) return; coachBaked[m] = URL.createObjectURL(bl); if ((coachEl.dataset.mood || 'normal') === m) coachMood(m, true); }, 'image/png'); } catch (e) {} };\n"
        "  im.src = COACH_ART[m]; }\n"
        "// which mood a line wants: a win or a gift laughs, a warning is serious, the rest (how to do a thing) is the normal one\n"
        "const COACH_LAUGH = /^(Learned|Looking good|Nice|It[\\u2019']s ready|You found|You earned|All yours|Hey, rookie|Take a look around|It[\\u2019']s Spooky|Safe in)/, COACH_SERIOUS = /(Out of paint|sun[\\u2019']s coming|Rivals pound|eliminate|Don[\\u2019']t forget|Now win it)/;\n"
        "const coachMoodOf = text => { const t = String(text || '').replace(/<[^>]+>|\\*/g, ''); return COACH_LAUGH.test(t) ? 'laugh' : COACH_SERIOUS.test(t) ? 'serious' : 'normal'; };\n"
        "function coachMood(m, force) { m = COACH_ART[m] ? m : 'normal'; if (tutEl.dataset.mood !== m) tutEl.dataset.mood = m; if (!force && coachEl.dataset.mood === m) return; coachEl.dataset.mood = m;\n"
        "  const b = coachEl.firstChild; b.style.backgroundImage = 'url(' + (coachBaked[m] || COACH_ART[m]) + ')'; b.classList.toggle('baked', !!coachBaked[m]); }") + s[j:]
    # his line sets his mood (the corner and the plate); the lesson's cards set theirs from the title
    s = rep(s, "  tutTip = { text, at: at || null, key, call: !!call, nodim: !!(nodim || loose), side: side || null, loose: !!loose, low: !!low };",
               "  coachMood(coachMoodOf(text)); // (v385)\n  tutTip = { text, at: at || null, key, call: !!call, nodim: !!(nodim || loose), side: side || null, loose: !!loose, low: !!low };")
    s = rep(s, "function tutCardText(t) { $('tgTitle').innerHTML = t[0];",
               "function tutCardText(t) { $('tutGo').dataset.mood = coachMoodOf(t[0]) === 'serious' ? 'serious' : 'laugh'; /* (v385: the news makes him laugh; 'Now win it!' doesn't) */ $('tgTitle').innerHTML = t[0];")
    # the plate's bust and the card's picture follow the mood (the corner one is set from the script, with its shadow baked in)
    s = rep(s, ".coachpop[data-side=\"l\"] b{scale:-1 1}\n",
               ".coachpop[data-side=\"l\"] b{scale:-1 1}\n"
               "/* (v385) his moods on the lesson's plate and over its cards */\n"
               ".tut[data-coach=\"bust\"][data-mood=\"serious\"] .tbust{background-image:url(art/coach_serious.webp)}.tut[data-coach=\"bust\"][data-mood=\"laugh\"] .tbust{background-image:url(art/coach_laugh.webp)}\n"
               ".tutgo[data-mood=\"serious\"] .tgcard .tava{background-image:url(art/coach_serious.webp)}.tutgo[data-mood=\"laugh\"] .tgcard .tava{background-image:url(art/coach_laugh.webp)}\n")
    # the Events page's round face: the new picture's face sits higher in its frame
    s = rep(s, "background:#2A2437 url(art/coach.webp) 50% 16%/165% no-repeat;", "background:#2A2437 url(art/coach.webp) 52% 4%/150% no-repeat;")
    return s
