#!/usr/bin/env python3
"""The winner screen: a pastel field, a dark band on the diagonal carrying a moving pattern of paint, the name and the stat up left, the big number down left. On top of ui11_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui11_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the backdrop: a pale field of the winner's color with flecks drifting up, a dark band across the diagonal with paint drops and
# splats streaming along it, a cream lip on its torn edges ----
a = s.index('const VIC_FS = `'); b = s.index('`;', a) + 2
s = s[:a] + r'''const VIC_FS = `uniform float uTime, uK; uniform vec3 uA, uB, uC; uniform vec2 uRes, uCen; varying vec2 vUv;
float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
float sdDrop(vec2 q){ float c = length(q - vec2(0.0, -0.09)) - 0.19; float tri = max(abs(q.x) - 0.19 * (0.33 - q.y) / 0.42, max(q.y - 0.33, -0.09 - q.y)); return min(c, tri); }
float sdSplat(vec2 q){ float r = length(q), an = atan(q.y, q.x); return r - (0.165 + 0.05 * sin(an * 6.0 + 1.0) + 0.025 * sin(an * 11.0 + 2.0)); }
void main(){
  vec2 p = (vUv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
  vec3 field = mix(uC, uA, 0.22), dark = mix(uB, vec3(0.07, 0.045, 0.1), 0.7), cream = vec3(0.96, 0.93, 0.87);
  // the field: a fine weave, flecks of the color rising slowly
  vec3 col = field * (0.985 + 0.03 * h2(floor(p * 160.0)));
  vec2 fu = p * vec2(9.0, 7.0) + vec2(0.0, -uTime * 0.25); vec2 fi = floor(fu), ff = fract(fu) - 0.5; float fh = h2(fi);
  float fleck = step(0.8, fh) * (1.0 - smoothstep(0.0, 0.05 + 0.07 * fract(fh * 9.0), length(ff + 0.3 * (vec2(fract(fh * 3.0), fract(fh * 5.0)) - 0.5))));
  col = mix(col, mix(uA, vec3(1.0), 0.35), fleck * 0.8);
  // the band: a dark stripe up the diagonal, its edges torn, paint drops and splats streaming along it
  float ca = cos(-0.36), sa = sin(-0.36); vec2 t = vec2(ca, sa), n = vec2(-sa, ca);
  vec2 bq = vec2(dot(p, t), dot(p, n)); float tear = (vn(bq * 5.0 + uTime * 0.12) - 0.5) * 0.035;
  float half_ = 0.26, inB = half_ - abs(bq.y + 0.03) + tear;
  float band = smoothstep(-0.004, 0.004, inB), lip = smoothstep(0.016, 0.0, abs(inB)) ;
  vec3 bc = dark * (0.96 + 0.08 * vn(bq * 6.0));
  vec2 cu = bq * 3.4 + vec2(uTime * 0.42, 0.0); vec2 ci = floor(cu); float odd = mod(ci.y, 2.0); cu.x += odd * 0.5; ci = floor(cu); vec2 cf = fract(cu) - 0.5;
  float ch = h2(ci); float rot = (ch - 0.5) * 0.7; vec2 q = vec2(cf.x * cos(rot) - cf.y * sin(rot), cf.x * sin(rot) + cf.y * cos(rot)) * (1.55 - 0.3 * fract(ch * 7.0));
  float d = ch > 0.5 ? sdDrop(q) : sdSplat(q);
  float icon = (1.0 - smoothstep(-0.012, 0.012, d)) * step(0.18, ch);
  bc = mix(bc, mix(uA, dark, 0.35), icon);
  col = mix(col, bc, band); col = mix(col, cream, lip * 0.9);
  // sparkles across the band
  vec2 su = bq * 14.0 + vec2(uTime * 0.9, 0.0); float sh = h2(floor(su)); float spark = step(0.93, sh) * (1.0 - smoothstep(0.0, 0.08, length(fract(su) - 0.5))) * (0.5 + 0.5 * sin(uTime * 7.0 + sh * 50.0));
  col += spark * band * 0.6;
  col *= 1.0 - 0.28 * smoothstep(0.7, 1.5, length(p));
  gl_FragColor = vec4(mix(vec3(1.0), col, smoothstep(0.0, 0.5, uK)), 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;''' + s[b:]
rep("vicU.uA.value.copy(col); vicU.uB.value.copy(col).multiplyScalar(0.3); vicU.uC.value.copy(col).lerp(COL_WHITE, 0.62); vicU.uK.value = 0;",
    "vicU.uA.value.copy(col); vicU.uB.value.copy(col).multiplyScalar(0.3); vicU.uC.value.copy(col).lerp(COL_WHITE, 0.72); vicU.uK.value = 0;")

# ---- the words: the name and tag up left with the stage line and the stat box; the big number down left; the rivals' cards down right ----
rep('''    <div class="vtop"><b class="vplace" id="vPlace">1<small>st</small></b><span class="vtag" id="vTag"><i class="reddot" id="vDot" hidden></i><span id="vTagTxt">Winner</span></span></div>
    <div class="vfoot">
      <h2 class="vname" id="vName"></h2>
      <p class="vsub" id="vSub"></p>
      <div class="vcards" id="vCards"></div>
      <p class="vtap" id="vTap">Tap to see your canvas</p>
    </div>''', '''    <div class="vtop">
      <h2 class="vname" id="vName"></h2>
      <div class="vline"><span class="vtag" id="vTag"><i class="reddot" id="vDot" hidden></i><span id="vTagTxt">Winner</span></span><span class="vstage" id="vStage"></span></div>
      <p class="vsub" id="vSub"></p>
    </div>
    <div class="vfoot">
      <b class="vplace" id="vPlace">1<small>st</small></b>
      <div class="vcards" id="vCards"></div>
      <p class="vtap" id="vTap">Tap to see your canvas</p>
    </div>''')
rep("  $('vTap').textContent = 'Tap to see the canvas';", "  $('vTap').textContent = 'Tap to see the canvas'; $('vStage').textContent = TH.label + ' \\u00b7 ' + (solo ? 'Solo' : (MODES.find(m => m[0] === mode) || MODES[0])[1]);")

CSS = '''
/* ===== the winner screen ===== */
.victory{padding:max(14px,calc(env(safe-area-inset-top) + 8px)) 16px max(14px,env(safe-area-inset-bottom))}
.vtop{display:grid;justify-items:start;align-items:start;gap:8px;padding-right:0}
.vname{transform:none;font:900 100px/.9 var(--font-head);font-style:italic;text-transform:uppercase;color:#fff;letter-spacing:-.01em}
.vname i{text-shadow:.03em .03em 0 var(--black),.07em .08em 0 var(--vc),calc(.07em + 3px) calc(.08em + 4px) 0 var(--black)}
.vline{display:flex;align-items:center;gap:10px;flex-wrap:wrap;animation:vrise .4s .55s cubic-bezier(.3,1.5,.5,1) both}
.vtag{margin:0;animation:none}
.vstage{font:900 13px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#fff;text-shadow:.06em .06em 0 var(--black)}
.vsub{margin:4px 0 0;display:grid;gap:2px;padding:9px 16px 10px;border:0;border-radius:8px;background:#171320;color:#fff;box-shadow:3px 4px 0 rgba(0,0,0,.35);font:800 12px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase}
.vsub b{display:block;font:900 34px/1 var(--font-head);font-style:italic;color:#fff;letter-spacing:0;text-transform:none}
.vfoot{position:static;display:grid;grid-template-columns:auto minmax(0,1fr);align-items:end;gap:6px 12px}
.vplace{grid-column:1;grid-row:1/3;margin:0;padding:0;font:900 clamp(96px,32vw,180px)/.8 var(--font-head);font-style:italic;color:#fff;text-shadow:.03em .03em 0 var(--black),.07em .07em 0 var(--vc),calc(.07em + 3px) calc(.07em + 4px) 0 var(--black);transform:rotate(-4deg)}
.vplace::before{display:none}
.vplace small{font-size:.32em;vertical-align:1.2em;margin-left:.04em}
.vplace.word{font-size:clamp(50px,16vw,96px)}
.vcards{grid-column:2;justify-content:end;margin:0}
.vcard{background:#171320;color:#fff;box-shadow:3px 4px 0 rgba(0,0,0,.35)}
.vcard .vcn{color:rgba(255,255,255,.7)}
.vcard .vrank{color:#fff}
.vtap{grid-column:2;justify-self:end;margin:0;background:rgba(23,19,32,.85);color:#fff}
@media (min-aspect-ratio:1/1){.vtop{max-width:48%}.vfoot{grid-template-columns:auto minmax(0,1fr);max-width:60%}.vplace{font-size:min(170px,26vh)}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]
rep('<p class="ver">Version 81</p>', '<p class="ver">Version 82</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
