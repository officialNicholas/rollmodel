p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
rep('<li><span class="dot holy"></span><span>Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.</span></li>',
    '<li><span class="dot holy"></span><span id="howGoal">Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.</span></li>')
rep("<span>Burst out of a coffin, then swipe up or down in mid-air to dash forward or back. You can't be touched while you dash.</span>",
    "<span>Burst out of a coffin, then swipe up or down in mid-air to dash forward or back. You can't be touched while you dash. Roll into a taken coffin to kick out whoever's inside and climb in.</span>")
rep('<button class="btn play sm" id="howClose" type="button">Got it</button>\n    </div>',
    '<button class="btn play sm" id="howClose" type="button">Got it</button>\n      <p class="ver">Version 1.0</p>\n    </div>')
rep(".rules{list-style:none;margin:0;padding:0;display:grid;gap:12px}",
    ".rules{list-style:none;margin:0;padding:0;display:grid;gap:12px}\n.ver{margin:-6px 0 0;text-align:center;font-size:12px;font-weight:700;color:var(--muted);opacity:.75}")
rep("function paintHow() { const el = $('howCtl');",
    "function paintHow() {\n  $('howGoal').textContent = mode === 'solo' ? 'Cover as much of the canvas as you can in 60 seconds, and beat your best.' : mode === 'trio' ? 'Cover more of the canvas than the holy water and the wolfsbane in 90 seconds. Paint over their colors to take ground back.' : 'Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.';\n  const el = $('howCtl');")
open(p,'w').write(s); print('ok')
