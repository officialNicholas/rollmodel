"""v382: the daily spin's wheel on the paper itself, in a thin gold bezel.

- The dark purple stage and its turning sunburst are gone: the wheel sits straight on the card's paper grid, with a soft shadow under it
  in place of the gold glow.
- The thick Ludo rim is gone too: a thin gold bezel (drawn with the wheel, about a fifth of what it was) rings the slices, with small
  bulbs set in it that still blink, faster while it turns. The slices fill the room the rim took, so they and their amounts are larger."""
import re

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<div class="spstage"><i class="sprays" aria-hidden="true"></i><div class="spwrap">', '<div class="spstage"><div class="spwrap">')
    s, k = re.subn(r'<img class="sprim" alt="" src="data:[^"]+">', '', s); assert k == 1, k
    s = rep(s, '<i class="spbulbs" aria-hidden="true"></i>', '')
    s = rep(s, "padding:18px 0 14px;background:radial-gradient(circle at 50% 46%,#3C3270 0,#211A45 52%,#120E28 100%);border-block:3px solid #171320;overflow:hidden}",
               "padding:22px 0 12px;overflow:hidden}")
    s = rep(s, ".spwrap::before{content:\"\";position:absolute;inset:4%;border-radius:50%;box-shadow:0 0 40px 10px rgba(255,200,80,.35),0 14px 0 rgba(0,0,0,.35)}",
               ".spwrap::before{content:\"\";position:absolute;inset:3%;border-radius:50%;box-shadow:0 7px 0 rgba(23,19,32,.22),0 10px 22px rgba(23,19,32,.18)}")
    s = rep(s, ".spwheel{position:absolute;left:50%;top:50%;width:66%;height:66%;", ".spwheel{position:absolute;left:50%;top:50%;width:88%;height:88%;")
    s = rep(s, ".sppin{position:absolute;left:50%;top:-7%;z-index:3;width:17%;", ".sppin{position:absolute;left:50%;top:-6.5%;z-index:3;width:14%;")
    s = rep(s, ".sphub{appearance:none;position:absolute;left:50%;top:50%;z-index:2;width:27%;", ".sphub{appearance:none;position:absolute;left:50%;top:50%;z-index:2;width:25%;")
    s = rep(s, ".spstage.go .sprays{animation-duration:5s}@keyframes sprays{to{rotate:360deg}}\n",
               ".spbulb{animation:spbulb 1.2s steps(1) infinite}.spbulb.b{animation-delay:-.6s}.spstage.go .spbulb{animation-duration:.25s}.spstage.go .spbulb.b{animation-delay:-.125s}@keyframes spbulb{50%{fill:#E9B23C}}\n")
    s = rep(s, ".spres.big,.sprays,.spbulbs,.sphub,", ".spres.big,.spbulb,.sphub,")
    # the bezel: a thin gold band between two ink lines, outside the turning slices, with bulbs in it
    s = rep(s, "<radialGradient id=\"spCoin\"", "<linearGradient id=\"spBez\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#FFE9A0\"/><stop offset=\".5\" stop-color=\"#F2C14E\"/><stop offset=\"1\" stop-color=\"#B9831F\"/></linearGradient><radialGradient id=\"spCoin\"")
    s = rep(s, "  $('spWheel').innerHTML = defs + '</defs><g id=\"spRot\">' + h + '</g>';\n",
               "  let bz = '<circle r=\"105\" fill=\"none\" stroke=\"#171320\" stroke-width=\"13\"/><circle r=\"105\" fill=\"none\" stroke=\"url(#spBez)\" stroke-width=\"8\"/>';\n"
               "  for (let k = 0; k < 20; k++) { const t = k * Math.PI / 10; bz += '<circle class=\"spbulb' + (k % 2 ? ' b' : '') + '\" cx=\"' + (Math.cos(t) * 105).toFixed(2) + '\" cy=\"' + (Math.sin(t) * 105).toFixed(2) + '\" r=\"2.3\" fill=\"#FFF8DC\" stroke=\"#8A5A12\" stroke-width=\".8\"/>'; }\n"
               "  $('spWheel').innerHTML = defs + '</defs><g id=\"spRot\">' + h + '</g>' + bz; // (v382: a thin bezel in place of the thick rim)\n")
    return s
