p='/home/claude/paint-the-canvas.html'
s=open(p).read()
a="const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']), theme = pick(THEMES), TK = theme.kit;"
b="const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']), th0 = pick(THEMES), theme = th0.id === themeAvoid ? THEMES[(THEMES.indexOf(th0) + 1 + Math.floor(R() * (THEMES.length - 1))) % THEMES.length] : th0, TK = theme.kit;"
assert s.count(a)==1; s=s.replace(a,b)
a="function freshMap() { genWorld((Math.random() * 4294967296) >>> 0); mapUsed = false; }"
b="let themeAvoid = null; // a new canvas never comes back in the same look as the one before it\nfunction freshMap() { themeAvoid = TH.id; genWorld((Math.random() * 4294967296) >>> 0); themeAvoid = null; mapUsed = false; }"
assert s.count(a)==1; s=s.replace(a,b)
open(p,'w').write(s); print('ok')
