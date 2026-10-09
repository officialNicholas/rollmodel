p='/home/claude/paint-the-canvas.html'
s=open(p).read()
for a,b in [("#cvName.pop{display:inline-block;animation:cvpop .35s cubic-bezier(.3,1.7,.5,1)}","#cvName.bump{display:inline-block;animation:cvpop .35s cubic-bezier(.3,1.7,.5,1)}"),
            (".pchip.win svg,#cvName.pop{animation:none}",".pchip.win svg,#cvName.bump{animation:none}"),
            ("renderStages(); kick($('cvName'), 'pop');","renderStages(); kick($('cvName'), 'bump');")]:
    assert s.count(a)==1,a; s=s.replace(a,b)
open(p,'w').write(s); print('ok')
