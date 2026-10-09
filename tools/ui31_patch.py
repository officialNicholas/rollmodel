#!/usr/bin/env python3
"""The winner backdrop, merged: the radial burst behind the hero from the first version, the flecks, ribbon, icons and lip from the second, plus flares. On top of ui30_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui30_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
a = s.index("const VIC_FS = `"); b = s.index("`;", a) + 2
NEW = r'''const VIC_FS = `uniform float uTime, uK; uniform vec3 uA, uB, uC; uniform vec2 uRes, uCen; varying vec2 vUv;
float h1(float n){ return fract(sin(n * 91.345) * 47453.5453); }
float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
float sdDrop(vec2 q){ float c = length(q - vec2(0.0, -0.09)) - 0.19; float tri = max(abs(q.x) - 0.19 * (0.33 - q.y) / 0.42, max(q.y - 0.33, -0.09 - q.y)); return min(c, tri); }
float sdSplat(vec2 q){ float r = length(q), an = atan(q.y, q.x); return r - (0.165 + 0.05 * sin(an * 6.0 + 1.0) + 0.025 * sin(an * 11.0 + 2.0)); }
vec3 hue(float h){ return clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0); }
void main(){
  float asp = uRes.x / uRes.y; vec2 pc = (vUv - uCen) * vec2(asp, 1.0), p = (vUv - 0.5) * vec2(asp, 1.0);
  float r = length(pc), a = atan(pc.y, pc.x) + uTime * 0.03;
  vec3 ink = mix(uB, vec3(0.04, 0.02, 0.06), 0.75), cream = vec3(0.96, 0.93, 0.87);
  // the field: the winner's color, deepening toward the edges, a hot core behind the hero
  vec3 col = mix(uA, mix(uA, ink, 0.45), smoothstep(0.15, 1.35, r));
  col = mix(col, mix(uA, vec3(1.0), 0.55), (1.0 - smoothstep(0.0, 0.5, r)) * 0.7);
  // the burst: rays streaming out from behind the hero in three inks (white, black, a light of the color), each ray its own width,
  // the whole wheel breathing, a few of them dashed and flowing outward
  float f = a / 6.2831853 * 72.0, id = floor(f), u = fract(f) - 0.5;
  float q = h1(id), q2 = h1(id + 17.3), q3 = h1(id + 41.7);
  float w = (0.06 + 0.3 * q2) * (q < 0.3 ? 1.25 : 1.0) * (0.25 + 0.75 * smoothstep(0.04, 0.9, r)) * (0.92 + 0.08 * sin(uTime * 2.3 + q3 * 20.0));
  float ray = 1.0 - smoothstep(w * 0.55, w, abs(u + 0.06 * sin(uTime * 1.7 + q3 * 9.0) * r));
  float flow = fract(r * (0.5 + q) - uTime * (0.7 + 1.2 * q) + q2 * 7.0);
  float dash = q3 > 0.55 ? 1.0 : smoothstep(0.0, 0.08, flow) * (1.0 - smoothstep(0.45, 0.8, flow));
  float m = ray * dash * smoothstep(0.08 + 0.16 * q2, 0.34 + 0.3 * q2, r);
  vec3 lc = q > 0.7 ? vec3(1.0) : q < 0.3 ? vec3(0.05, 0.02, 0.07) : mix(uA, vec3(1.0), 0.4);
  col = mix(col, lc, m * (q > 0.7 ? 0.95 : q < 0.3 ? 0.94 : 0.5));
  // flecks of the color drifting up through it all
  vec2 fu = p * vec2(9.0, 7.0) + vec2(0.0, -uTime * 0.25); vec2 fi = floor(fu), ff = fract(fu) - 0.5; float fh = h2(fi);
  float fleck = step(0.82, fh) * (1.0 - smoothstep(0.0, 0.04 + 0.06 * fract(fh * 9.0), length(ff + 0.3 * (vec2(fract(fh * 3.0), fract(fh * 5.0)) - 0.5))));
  col = mix(col, mix(uA, vec3(1.0), 0.6), fleck * 0.75);
  // sparkles flying outward
  vec2 g = vec2(a * 10.0, r * 7.0 - uTime * 2.4), gi = floor(g), gf = fract(g) - 0.5; float hs = h2(gi);
  col += step(0.88, hs) * (1.0 - smoothstep(0.0, 0.13, length(gf * vec2(1.0, 0.55)))) * (0.55 + 0.45 * sin(uTime * 9.0 + hs * 40.0)) * smoothstep(0.12, 0.5, r) * 0.9;
  // lens flares: soft discs drifting across, one of them fringed with the spectrum
  for (int i = 0; i < 4; i++) { float fi2 = float(i); vec2 c = vec2(sin(uTime * (0.11 + 0.05 * fi2) + fi2 * 2.1) * (0.3 + 0.2 * fi2), cos(uTime * (0.09 + 0.04 * fi2) + fi2 * 1.3) * 0.45);
    float rr = 0.07 + 0.06 * fi2, dd = length(p - c); float disc = (1.0 - smoothstep(rr * 0.6, rr, dd)) * 0.08, ring = (1.0 - smoothstep(0.0, 0.012, abs(dd - rr))) * 0.22;
    vec3 fc = i == 2 ? mix(vec3(1.0), hue(fract(atan(p.y - c.y, p.x - c.x) / 6.2831853 + uTime * 0.05)), 0.7) : vec3(1.0);
    col += fc * (disc + ring); }
  // the ribbon: a dark stripe across the lower part, its edges torn, drops and splats streaming along it, a cream lip
  float ca = cos(-0.2), sa = sin(-0.2); vec2 t = vec2(ca, sa), n = vec2(-sa, ca);
  vec2 bq = vec2(dot(p, t), dot(p, n)); float tear = (vn(bq * 5.0 + uTime * 0.12) - 0.5) * 0.035;
  float inB = 0.16 - abs(bq.y + 0.5) + tear;
  float band = smoothstep(-0.004, 0.004, inB), lip = smoothstep(0.016, 0.0, abs(inB));
  vec3 bc = ink * (0.96 + 0.08 * vn(bq * 6.0));
  vec2 cu = bq * 3.4 + vec2(uTime * 0.42, 0.0); vec2 ci = floor(cu); float odd = mod(ci.y, 2.0); cu.x += odd * 0.5; ci = floor(cu); vec2 cf = fract(cu) - 0.5;
  float ch = h2(ci); float rot = (ch - 0.5) * 0.7; vec2 qq = vec2(cf.x * cos(rot) - cf.y * sin(rot), cf.x * sin(rot) + cf.y * cos(rot)) * (1.55 - 0.3 * fract(ch * 7.0));
  float d = ch > 0.5 ? sdDrop(qq) : sdSplat(qq);
  float icon = (1.0 - smoothstep(-0.012, 0.012, d)) * step(0.18, ch);
  bc = mix(bc, mix(uA, ink, 0.35), icon);
  col = mix(col, bc, band); col = mix(col, cream, lip * 0.9);
  col *= 1.0 - 0.3 * smoothstep(0.75, 1.6, length(p));
  gl_FragColor = vec4(mix(vec3(1.0), col, smoothstep(0.0, 0.5, uK)), 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;'''
s = s[:a] + NEW + s[b:]
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 100</p>', '<p class="ver">Version 101</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
