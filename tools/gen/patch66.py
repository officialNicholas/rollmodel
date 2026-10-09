import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# ---------- shadows: a 2x2 bilinear filter instead of 16 taps, on every lit pixel ----------
rep("const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });",
r"""THREE.ShaderChunk.shadowmap_pars_fragment = THREE.ShaderChunk.shadowmap_pars_fragment.replace(/#elif defined\( SHADOWMAP_TYPE_PCF_SOFT \)[\s\S]*?(?=#elif defined\( SHADOWMAP_TYPE_VSM \))/, `#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			vec2 f = fract( shadowCoord.xy * shadowMapSize + 0.5 );
			vec2 uv = shadowCoord.xy - f * texelSize;
			shadow = mix( mix( texture2DCompare( shadowMap, uv, shadowCoord.z ), texture2DCompare( shadowMap, uv + vec2( texelSize.x, 0.0 ), shadowCoord.z ), f.x ),
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, texelSize.y ), shadowCoord.z ), texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ), f.x ), f.y );
		`);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });""")
# ---------- paint: the dried-paint cracks come from a 2D cell pattern on the ground (9 cells, not 27) ----------
rep("""vec2 cell(vec3 p){ vec3 i = floor(p), f = fract(p); float d1 = 8.0, d2 = 8.0;
  for (int x=-1;x<=1;x++) for (int y=-1;y<=1;y++) for (int z=-1;z<=1;z++){ vec3 g = vec3(float(x),float(y),float(z)); vec3 r = g + h3(i+g) - f; float d = dot(r,r); if (d < d1){ d2 = d1; d1 = d; } else if (d < d2) d2 = d; }
  return vec2(sqrt(d1), sqrt(d2)); }""", """vec2 hh2(vec2 p){ p = vec2(dot(p,vec2(127.1,311.7)), dot(p,vec2(269.5,183.3))); return fract(sin(p)*43758.5453); }
vec2 cell(vec2 p){ vec2 i = floor(p), f = fract(p); float d1 = 8.0, d2 = 8.0;
  for (int x=-1;x<=1;x++) for (int y=-1;y<=1;y++){ vec2 g = vec2(float(x),float(y)); vec2 r = g + hh2(i+g) - f; float d = dot(r,r); if (d < d1){ d2 = d1; d1 = d; } else if (d < d2) d2 = d; }
  return vec2(sqrt(d1), sqrt(d2)); }""")
rep("vec3 h3(vec3 p){ p = vec3(dot(p,vec3(127.1,311.7,74.7)), dot(p,vec3(269.5,183.3,246.1)), dot(p,vec3(113.5,271.9,124.6))); return fract(sin(p)*43758.5453); }\n", "")
rep("    vec2 c = cell(vW * 2.2);", "    vec2 c = cell(vW.xz * 2.2 + vW.y * 0.37);")
# ---------- adaptive quality: after resolution bottoms out, shadows get lighter (smaller map, then drawn every other frame) ----------
rep("""  if (avg > 0.0205 && curPR > 1) { curPR = Math.max(1, curPR - 0.25); renderer.setPixelRatio(curPR); resize(); perfGood = 0; }
  else if (avg < 0.0135 && curPR < maxPR) { if (++perfGood >= 4) { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); perfGood = 0; } }
  else perfGood = 0;""", """  if (avg > 0.0205 && curPR > 1) { curPR = Math.max(1, curPR - (avg > 0.03 ? 0.5 : 0.25)); renderer.setPixelRatio(curPR); resize(); perfGood = 0; }
  else if (avg > 0.0205 && shadowLite < 2) { setShadowLite(shadowLite + 1); perfGood = 0; }
  else if (avg < 0.0135 && (shadowLite > 0 || curPR < maxPR)) { if (++perfGood >= 4) { if (shadowLite > 0) setShadowLite(shadowLite - 1); else { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); } perfGood = 0; } }
  else perfGood = 0;""")
rep("function tunePerf(ft) {", """let shadowLite = 0, frameNo = 0;
function setShadowLite(k) {
  shadowLite = k; const sz = k ? 1024 : 2048;
  if (sun.shadow.mapSize.x !== sz) { sun.shadow.mapSize.set(sz, sz); if (sun.shadow.map) { sun.shadow.map.dispose(); sun.shadow.map = null; } }
  sun.shadow.autoUpdate = k < 2; sun.shadow.needsUpdate = true;
}
function tunePerf(ft) {""")
rep("  visuals(dt, rdt); flushTrail();\n  renderFrame();", "  visuals(dt, rdt); flushTrail();\n  if (shadowLite >= 2) sun.shadow.needsUpdate = (++frameNo & 1) === 0;\n  renderFrame();")
open(F, 'w').write(s)
print('ok')
