import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:120])); sys.exit(1)
    s = s.replace(a, b)

# ---------- banners: the big word says it; subtitles only the first time something new happens ----------
rep("banner('Giant!', 'Roll into the holy water to squish it.')", "banner('Giant!')")
rep("banner('The holy water went giant!', 'Keep away for 5 seconds.')", "banner('It went giant!', 'Keep away')")
rep("banner('Blasted!', 'Watch the edges')", "banner('Blasted!')")
rep("banner('Blasted it!', 'Knock it off the edge')", "banner('Blasted it!')")
rep("banner('Shrunk!', 'Pounded out of giant mode')", "banner('Shrunk!')")
rep("banner('Shrunk it!', 'Back to normal size')", "banner('Shrunk it!')")
rep("banner('Knocked out of your coffin!')", "banner('Bounced out!')")
rep("banner('Blood refilled')", "popText('Refilled!')")
rep("banner((reason === 'fall' && by ? 'Knocked off!' : KO_MSG[reason]) || 'Out!', 'Back in ' + Math.ceil(D.koT))", "banner((reason === 'fall' && by ? 'Knocked off!' : KO_MSG[reason]) || 'Out!')")
rep("banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Holy water out!', 'Out for ' + Math.ceil(D.koT) + (D.koT > 1.5 ? ' seconds' : ' second'))", "banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Got it!')")
rep("banner(how === 'giant' ? 'Squished!' : 'Flattened!', 'Stuck for 2 seconds')", "banner(how === 'giant' ? 'Squished!' : 'Flattened!')")
rep("banner(how === 'stomp' ? 'Stomped it!' : how === 'giant' ? 'Squished it!' : 'Flattened it!', 'Pound it now!')", "banner(how === 'stomp' ? 'Stomped it!' : how === 'giant' ? 'Squished it!' : 'Flattened it!', 'Pound it!')")
rep("banner('Overtime!', 'Dead even. ' + OT_T + ' more seconds.', true)", "banner('Overtime!', OT_T + ' more seconds', true)")
rep("banner('Sunrise in ' + SUN_WARN, 'Hide in a coffin or a shadow.', true)", "banner('Sunrise in ' + SUN_WARN, sunsSeen ? '' : 'Hide in a coffin or a shadow', true)")
rep("banner('Rain!', 'Puddles are forming. Everyone speeds up.')", "banner('Rain!', rainsSeen++ ? '' : 'Everyone speeds up')")
rep("banner('Rain!', 'Paint softens and puddles form.')", "banner('Rain!', rainsSeen++ ? '' : 'Hard paint softens')")
rep("banner('Same canvas', TH.label)", "banner('Same canvas')")
rep("banner('Paint it red!', TH.label + ' · beat the ' + diff + ' holy water in ' + MATCH_T + ' seconds', true)", "banner('Paint it red!', TH.label, true)")
rep("let lives = 1, overtimeUsed = false,", "let rainsSeen = 0, lives = 1, overtimeUsed = false,")
rep("runT = 0; matchLeft = MATCH_T; lastCount = 99; overtimeUsed = false;", "runT = 0; matchLeft = MATCH_T; lastCount = 99; overtimeUsed = false; rainsSeen = 0;")
rep("const KO_MSG = { pound: 'Pounded!', coffin: 'Staked in your coffin!', fall: 'Fell off', sun: 'Sunburnt', dry: 'Drained' };", "const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt' };")
rep("const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Crushed it in the coffin!', fall: 'It fell off', sun: 'Evaporated!', dry: 'It ran dry' };", "const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!' };")

# ---------- little pops: keep the ones that tell you something you need ----------
rep("if (D === P) popText('Back to size');", "")
rep("if (D === P && D.st !== 'ko') popText('Blood back!');", "")
rep("popText('Giant orb!')", "popText('Orb!')")
rep("if (giant) popText('Giant slam!'); else if (missile) popText('Missile!');", "")
rep("if (B === P) { holdCharge = false; slingOff(); popText('Quake!'); }", "if (B === P) { holdCharge = false; slingOff(); }")
rep("if (B === P) { shake = Math.max(shake, 0.12); buzz(10); popText('Splashed!'); } else if (A === P) popText('Splashed it!');", "if (B === P) { shake = Math.max(shake, 0.12); buzz(10); }")
rep("popText('Bounced it!')", "popText('Bounced it!')")
rep("popText('It jumped it!')", "popText('It dodged!')")
rep("popText('No blood to fling')", "popText('No blood')")
rep("popText(ld > 0 ? 'You take the lead!' : 'Holy water leads')", "popText(ld > 0 ? 'You lead!' : 'It leads')")

# ---------- first-time tips: shorter ----------
rep("hint('dilute', 'Puddles water you down: half-strength paint for 2 seconds', 3)", "hint('dilute', 'Puddles water your paint down', 2.6)")
rep("hint('orb', 'Jump or fling into the glowing orb to go giant', 3.2)", "hint('orb', 'Touch the orb to go giant', 2.8)")
rep("hint('dry', 'Out of blood: get to a coffin to refill', 3.2)", "hint('dry', 'Out of blood: find a coffin or your own color', 3.2)")
rep("hint('airsling', say('Hold and pull on the way down to sling yourself', 'Hold S on the way down to sling yourself'), 3)", "hint('airsling', say('Pull on the way down to sling again', 'Hold S on the way down to sling again'), 2.8)")
rep("hint('hold', say('Hold to stop. Pull down to fling.', 'Hold S to stop and load a fling'), 3.2)", "hint('hold', say('Pull down and let go to fling', 'Hold S, let go to fling'), 2.8)")
rep("hint('burst', say('Pound in a coffin to burst out of it', 'Press E in a coffin to burst out of it'), 3)", "hint('burst', say('Pound to burst out', 'E to burst out'), 2.6)")
rep("hint('pound', say('Pound near the holy water to knock it out', 'Press E near the holy water to pound it'), 3)", "hint('pound', say('Pound it while it\\'s close', 'E to pound it while it\\'s close'), 2.6)")
rep("hint('steer', say('Drag to steer', 'A and D or the arrow keys steer'), 3)", "hint('steer', say('Drag to steer', 'A D or arrows to steer'), 3)")

# ---------- menu: less to read ----------
rep("""<p class="lede">You're a drop of vampire blood. Cover more of the canvas than the holy water in 90 seconds.</p>""", """<p class="lede">Cover more of the canvas than the holy water in 90 seconds.</p>""")
rep("""h += '<button class="tile' + (k === diff ? ' sel' : '') + '" data-d="' + k + '" type="button" aria-pressed="' + (k === diff) + '"><span class="tn">' + name + '</span><span class="tt">' + tag + '</span><span class="tb">' + (pl ? w + (w === 1 ? ' win' : ' wins') : 'New') + '</span></button>';""",
    """h += '<button class="tile' + (k === diff ? ' sel' : '') + '" data-d="' + k + '" type="button" aria-pressed="' + (k === diff) + '" aria-label="' + name + ': ' + tag + '"><span class="tn">' + name + '</span><span class="tb">' + (pl ? w + (w === 1 ? ' win' : ' wins') : '&nbsp;') + '</span></button>';""")

# how to play: seven short lines
i = s.index('      <ul class="rules">'); j = s.index('    </details>', i)
s = s[:i] + """      <ul class="rules">
        <li><span class="dot hand">↔</span><span id="howCtl">Drag sideways to steer. Tap to jump. Hold to stop, then pull down and let go to fling. The arrow button pounds.</span></li>
        <li><span class="dot holy"></span>Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.</li>
        <li><span class="dot ink"></span>Your color is a fast lane that refills your blood. Its color slows you. Run dry and you crawl until a coffin or your own color fills you up.</li>
        <li><span class="dot hand">↓</span>Pound to splat a circle: anything inside is out for a few seconds. Jump to ride over a pound coming at you.</li>
        <li><span class="dot hand">➚</span>Fling into the holy water to knock it flying. Ram it while you're faster, or land on it, to flatten it.</li>
        <li><span class="dot sun"></span>Sunrise: hide in a coffin or a shadow. Rain: everyone speeds up and puddles water your paint down.</li>
        <li><span class="dot ink"></span>Grab the glowing orb to go giant for 5 seconds.</li>
      </ul>
""" + s[j:]

# end screen: one compact line of stats instead of sentences
rep("""  const bits = [];
  if (P.kos) bits.push('You knocked it out ' + times(P.kos) + '.');
  if (H.kos) bits.push('It knocked you out ' + times(H.kos) + '.');
  if (H.flats) bits.push('You flattened it ' + times(H.flats) + '.');
  bits.push('Wins on ' + lv[1] + ': ' + ((store.wins && store.wins[diff]) || 0) + '. Best: ' + ((store.bestCov && store.bestCov[diff]) || 0) + '%.');
  $('endNote').textContent = bits.join(' ');""", """  const bits = ['Knockouts ' + P.kos + '-' + H.kos];
  if (H.flats || P.flats) bits.push('Flattened ' + H.flats + '-' + P.flats);
  bits.push('Best ' + ((store.bestCov && store.bestCov[diff]) || 0) + '%');
  $('endNote').textContent = bits.join('  ·  ');""")
open(F, 'w').write(s)
print('ok')
