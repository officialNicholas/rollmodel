p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
# title and logo
rep('<title>Paint the World Red</title>', '<title>Roll Model</title>')
rep('<h1 class="logo paint" id="logo"><span class="l1">Paint the World</span>', '<h1 class="logo paint" id="logo" aria-label="Roll Model"><span class="l1">Roll</span>')
rep('<span class="cw" id="logoWord">Red</span>', '<span class="cw" id="logoWord">Model</span>')
rep("$('logoWord').textContent = c.name; document.title = 'Paint the World ' + c.name; canvas.setAttribute('aria-label', 'Paint the World ' + c.name + ' game view');",
    "document.title = 'Roll Model';")
rep('aria-label="Paint the World Red game view"', 'aria-label="Roll Model game view"')
# rivals are just other blobs now, with names of their own each match
rep("const MODES = [['solo', 'Solo', 'Just you, 60 seconds'], ['duel', '1v1', 'You vs the holy water'], ['trio', '3-way', 'You vs the holy water vs wolfsbane']];",
    "const MODES = [['solo', 'Solo', 'Just you, 60 seconds'], ['duel', '1v1', 'You and one rival'], ['trio', '3-way', 'You and two rivals']];")
rep("const NAMES = ['You', 'Holy water', 'Wolfsbane'], nameOf = D => D === P ? playerName() : NAMES[D.team];",
    "const NAMES = ['You', 'Smudge', 'Doodle'], nameOf = D => D === P ? playerName() : NAMES[D.team];\nconst RIVAL_NAMES = ['Smudge', 'Blot', 'Splodge', 'Dribble', 'Doodle', 'Squiggle', 'Speckle', 'Glop', 'Drizzle', 'Swirl', 'Dabs', 'Gloop', 'Sploosh', 'Tinty', 'Smear', 'Daub'];\nfunction pickRivalNames() { const me = playerName().toLowerCase(), pool = RIVAL_NAMES.filter(n => n.toLowerCase() !== me); const a = pool.splice(Math.floor(Math.random() * pool.length), 1)[0]; NAMES[1] = a; NAMES[2] = pool[Math.floor(Math.random() * pool.length)]; }")
rep("const NAME_MAX = 12, NAME_IDEAS = ['Nightshade', 'Crimson', 'Vesper', 'Count Drip', 'Velvet', 'Lady Fang', 'Noir', 'Rouge', 'Vlad', 'Mina', 'Hemlock', 'Ruby', 'Bat Boy', 'Midnight', 'Carmilla', 'Dusk'];",
    "const NAME_MAX = 12, NAME_IDEAS = ['Rollo', 'Spatter', 'Brushy', 'Glossy', 'Pixel', 'Dabble', 'Swatch', 'Sprinkle', 'Mosaic', 'Primer', 'Inky', 'Neon', 'Jelly', 'Marble', 'Gumdrop', 'Picasso Jr'];")
# paint, not blood
rep("tip: 'Roller! Wide stripes for 9 seconds. Blood refilled.'", "tip: 'Roller! Wide stripes for 9 seconds. Paint refilled.'")
rep("popText('Out of blood!');", "popText('Out of paint!');")
rep("hint('dry', 'Out of blood: reach a coffin or your own color in ' + DRY_KO + ' seconds', 3.2);", "hint('dry', 'Out of paint: reach a ' + potWord() + ' or your own color in ' + DRY_KO + ' seconds', 3.2);")
rep("popText('No blood');", "popText('No paint');")
rep("(up ? 'Burst out of the coffin' : fwd ? 'Fire a missile' : 'Ground pound') : P.slamCD > 0 ? 'Ground pound building up' : 'Ground pound needs at least one bar of blood'",
    "(up ? 'Burst out of the ' + potWord() : fwd ? 'Fire a missile' : 'Ground pound') : P.slamCD > 0 ? 'Ground pound building up' : 'Ground pound needs at least one bar of paint'")
rep("banner('Sunrise in ' + SUN_WARN, sunsSeen ? '' : 'Hide in a coffin or a shadow', true);", "banner('Sunrise in ' + SUN_WARN, sunsSeen ? '' : 'Hide in a ' + potWord() + ' or the shade', true);")
rep("const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt', crush: 'Crushed!', dry: 'Dried up!' };",
    "const KO_MSG = { pound: 'Pounded!', coffin: 'Nailed!', fall: 'Fell off', sun: 'Baked!', crush: 'Crushed!', dry: 'Dried up!' };")
rep("const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!', crush: 'Crushed it!', dry: 'It dried up!' };",
    "const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Nailed it!', fall: 'It fell off', sun: 'Baked it!', crush: 'Crushed it!', dry: 'It dried up!' };\nconst koLine = (reason, mine) => reason === 'coffin' && TH.pot === 'can' ? (mine ? 'Canned!' : 'Canned it!') : (mine ? KO_MSG : CPU_KO_MSG)[reason];")
rep("banner((reason === 'fall' && by ? 'Knocked off!' : KO_MSG[reason]) || 'Out!'); }", "banner((reason === 'fall' && by ? 'Knocked off!' : koLine(reason, true)) || 'Out!'); }")
rep("banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Got it!');", "banner((reason === 'fall' && by ? 'Knocked it off!' : koLine(reason, false)) || 'Got it!');")
# results
rep("$('chipCpuName').textContent = solo ? (endInfo.newBest ? 'Old best' : 'Your best') : 'Holy water';", "$('chipCpuName').textContent = solo ? (endInfo.newBest ? 'Old best' : 'Your best') : nameOf(H); $('chipCpu2Name').textContent = nameOf(H2);")
rep('<span id="chipCpuName">Holy water</span>', '<span id="chipCpuName">Rival</span>')
rep('<div><b id="endPctC2">0%</b><span>Wolfsbane</span></div>', '<div><b id="endPctC2">0%</b><span id="chipCpu2Name">Rival</span></div>')
rep("const PT_A = ['Nocturne', 'Requiem', 'Study', 'Elegy', 'Sonata', 'Midnight', 'Duel', 'Etude'];", "const PT_A = ['Nocturne', 'Study', 'Impression', 'Sonata', 'Midnight', 'Duel', 'Etude', 'Rhapsody'];")
rep("const PT_B = ['in ' + w[0] + ' and Blue', 'in ' + w[1], 'in Blood and Holy Water', 'for One Fang', 'in Moonlight and ' + w[2], 'in ' + w[2]];",
    "const PT_B = ['in ' + w[0] + ' and Blue', 'in ' + w[1], 'in Two Colors', 'for One Blob', 'in Moonlight and ' + w[2], 'in ' + w[2]];")
rep('<span id="pMeta">Blood on canvas</span>', '<span id="pMeta">Paint on canvas</span>')
# how to play, written for whichever stage and mode you're on
for a, b in [
  ('<span class="dot ink"></span><span>Your color is a fast lane that refills your blood. Its color slows you down. Run dry and you crawl, with 4 seconds to reach a coffin or your own color before you dry up.</span>', '<span class="dot ink"></span><span id="howInk"></span>'),
  ('<span class="dot hand">↓</span><span>Roll into the holy water to stun it for 2 seconds. Pound to splat a circle. Anything inside is out for a few seconds. Jump it, or time a roll: rolling makes you untouchable for half a second.</span>', '<span class="dot hand">↓</span><span id="howRoll"></span>'),
  ("<span class=\"dot hand\">➚</span><span>Fling into the holy water to knock it flying, or pound mid-fling to fire a missile that steers toward it. Ram it while you're faster, or land on it, to flatten it.</span>", '<span class="dot hand">➚</span><span id="howFling"></span>'),
  ("<span class=\"dot hand\">⇅</span><span>Burst out of a coffin, then swipe up or down in mid-air to dash forward or back. You can't be touched while you dash. Roll into a taken coffin to kick out whoever's inside and climb in.</span>", '<span class="dot hand">⇅</span><span id="howBurst"></span>'),
  ('<span class="dot sun"></span><span>Sunrise: hide in a coffin or a shadow. Rain: everyone speeds up and puddles water your paint down. Pound a puddle to water down their paint all around it.</span>', '<span class="dot sun"></span><span id="howSun"></span>'),
  ("<span class=\"dot orbd\"></span><span>Grab the glowing orb to go giant for 5 seconds. Roll into the holy water while you're giant and it's out.</span>", '<span class="dot orbd"></span><span id="howOrb"></span>'),
]: rep(a, b)
rep("Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.</span>", "</span>")
rep("  $('howGoal').textContent = mode === 'solo' ? 'Cover as much of the canvas as you can in 60 seconds, and beat your best.' : mode === 'trio' ? 'Cover more of the canvas than the holy water and the wolfsbane in 90 seconds. Paint over their colors to take ground back.' : 'Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.';",
    """  const pw = potWord(), riv = mode === 'trio' ? 'a rival' : 'your rival';
  $('howGoal').textContent = mode === 'solo' ? 'Cover as much of the canvas as you can in 60 seconds, and beat your best.' : mode === 'trio' ? 'Cover more of the canvas than both rivals in 90 seconds. Paint over their colors to take ground back.' : 'Cover more of the canvas than your rival in 90 seconds. Paint over their color to take ground back.';
  $('howInk').textContent = 'Your color is a fast lane that refills your paint. A rival\\'s color slows you down. Run dry and you crawl, with 4 seconds to reach a ' + pw + ' or your own color before you dry up.';
  $('howRoll').textContent = 'Roll into ' + riv + ' to stun it for 2 seconds. Pound to splat a circle. Anything inside is out for a few seconds. Jump it, or time a roll: rolling makes you untouchable for half a second.';
  $('howFling').textContent = 'Fling into ' + riv + ' to knock it flying, or pound mid-fling to fire a missile that steers toward it. Ram it while you\\'re faster, or land on it, to flatten it.';
  $('howBurst').textContent = 'Hide in a ' + pw + ' to refill. Burst out of it, then swipe up or down in mid-air to dash forward or back. You can\\'t be touched while you dash. Roll into a taken ' + pw + ' to kick out whoever\\'s inside and climb in.';
  $('howSun').textContent = 'Sunrise bakes anything out in the open, so hide in a ' + pw + ' or the shade. Rain: everyone speeds up and puddles water your paint down. Pound a puddle to water down their paint all around it.';
  $('howOrb').textContent = 'Grab the glowing orb to go giant for 5 seconds. Roll into ' + riv + ' while you\\'re giant and it\\'s out.';""")
# what you hide in: paint cans on the standard stage, coffins this season
rep("const easyOn = () => diff === 'easy' && mode !== 'solo', EASY_DRAIN = 0.85;",
    "const easyOn = () => diff === 'easy' && mode !== 'solo', EASY_DRAIN = 0.85;\nconst potWord = () => TH.pot === 'can' ? 'paint can' : 'coffin';")
rep("kit: { drum: [1, 3], column: [0, 1], rpad: [0, 1], rotunda: [0, 1], rpit: [0, 1] }, fill: 'drum' },", "kit: { drum: [1, 3], column: [0, 1], rpad: [0, 1], rotunda: [0, 1], rpit: [0, 1] }, fill: 'drum', pot: 'can' },")
open(p,'w').write(s); print('ok')
