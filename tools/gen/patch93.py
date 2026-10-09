p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
# rule: out of blood for 4 seconds without refilling and you dry up (everyone, CPUs too)
rep("const DRY_SPD = 0.38, DRY_OUT = 0.25; // drained: crawl at this fraction of your speed until a refill brings you back to one bar",
    "const DRY_SPD = 0.38, DRY_OUT = 0.25, DRY_KO = 4; // drained: crawl at this fraction of your speed until a refill brings you back to one bar, and dry up if that takes longer than DRY_KO seconds")
rep("  if (D.dry && (D.paint >= DRY_OUT || D.giantT > 0 || D.st === 'ko')) { D.dry = false;  }",
    "  if (D.dry && (D.paint >= DRY_OUT || D.giantT > 0 || D.st === 'ko')) { D.dry = false;  }\n  // the clock runs while you're out on the canvas dry (a coffin pauses it while it fills you)\n  if (D.dry && D.st === 'play' && state === 'play') { D.dryT = (D.dryT || 0) + dt; if (D.dryT >= DRY_KO) { knockOut(D, 'dry'); return; } } else if (!D.dry) D.dryT = 0;")
rep("const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt', crush: 'Crushed!' };",
    "const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt', crush: 'Crushed!', dry: 'Dried up!' };")
rep("const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!', crush: 'Crushed it!' };",
    "const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!', crush: 'Crushed it!', dry: 'It dried up!' };")
rep("const deathColor = (D, r) => r === 'sun' ? (D.cpu ? 0xDDEEFF : 0x4A4052) : TEAMS[D.team].wet;",
    "const deathColor = (D, r) => r === 'sun' ? (D.cpu ? 0xDDEEFF : 0x4A4052) : r === 'dry' ? 0x5E4F5C : TEAMS[D.team].wet;")
rep("      if (r === 'garlic' || r === 'brush') hiss(", "      if (r === 'garlic' || r === 'brush' || r === 'dry') hiss(")
rep("hint('dry', 'Out of blood: find a coffin or your own color', 3.2); }",
    "hint('dry', 'Out of blood: reach a coffin or your own color in ' + DRY_KO + ' seconds', 3.2); }")
rep("Run dry and you crawl until a coffin or your own color fills you up.",
    "Run dry and you crawl, with 4 seconds to reach a coffin or your own color before you dry up.")
# the empty tube turns into the countdown
rep('<div class="ttrack" id="ttrack"><span><i></i></span><span><i></i></span><span><i></i></span><span><i></i></span></div>',
    '<div class="ttrack" id="ttrack"><span><i></i></span><span><i></i></span><span><i></i></span><span><i></i></span><em class="tdry" aria-live="assertive">Find a coffin <b id="tdryN">4</b></em></div>')
rep(".tube.dry .ttrack span{background:rgba(255,255,255,.05)}",
    ".tube.dry .ttrack span{background:rgba(255,255,255,.05)}\n.ttrack{position:relative}\n.tdry{position:absolute;inset:2px;display:none;align-items:center;justify-content:center;gap:7px;padding-left:10px;border-radius:99px;background:#FF3B5C;color:var(--white);font:800 14px/1 var(--font-ui);font-style:normal;white-space:nowrap;animation:threatPulse .4s ease-in-out infinite alternate}\n.tdry b{font:400 18px/1 var(--font-display);text-shadow:var(--o2)}\n.tube.dry .tdry{display:flex}")
rep("bar.classList.toggle('dry', !!P.dry && P.st === 'play');",
    "bar.classList.toggle('dry', !!P.dry && P.st === 'play');\n    if (P.dry && P.st === 'play') { const n = Math.max(1, Math.ceil(DRY_KO - (P.dryT || 0))); if (n !== dryShown) { dryShown = n; $('tdryN').textContent = n; if (playing) { AU.count(n); buzz(n <= 2 ? [14, 30, 14] : 10); } } } else dryShown = 0;")
rep("let hold = 0, slow = 0, fovKick = 0,", "let dryShown = 0, hold = 0, slow = 0, fovKick = 0,")
open(p,'w').write(s); print('ok')
