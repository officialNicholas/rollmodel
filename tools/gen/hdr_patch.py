# Linear HDR: color management on (colors and color textures are sRGB, lighting is done in linear light), the Graphics
# mode frame renders into a half-float target so lights can run brighter than white, and the composite tone maps
# (Khronos PBR Neutral, which keeps hues and saturation as authored) before grading and encoding to sRGB.
# Performance mode gets the same tone mapping from three itself. Every custom shader ends with three's tone mapping
# and color space chunks, so it is right whether it draws to the screen or into the HDR target.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:110]); s = s.replace(old, new)

rep("THREE.ColorManagement.enabled = false; // colors are authored as-is: the picture handles its own tone and grade\n", "")
rep("renderer.outputColorSpace = THREE.LinearSRGBColorSpace;", "renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.NeutralToneMapping;")

# color textures are sRGB; normal maps and baked data stay linear
i = s.index('const canvasTex = (() => {'); j = s.index('return t;', i)
s = s[:i] + s[i:j].replace('const t = new THREE.CanvasTexture(cv);', 'const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;', 1) + s[j:]
i = s.index('const woodTex = (() => {'); j = s.index('return t;', i)
s = s[:i] + s[i:j].replace('const t = new THREE.CanvasTexture(cv);', 'const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;', 1) + s[j:]
i = s.index('function makeTex(S, draw) {'); j = s.index('\n', i)
assert 'const t = new THREE.CanvasTexture(cv);' in s[i:j]
s = s[:i] + s[i:j].replace('const t = new THREE.CanvasTexture(cv);', 'const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;', 1) + s[j:]
rep("const t = new THREE.CanvasTexture(cv); t.anisotropy = 8; return t;", "const t = new THREE.CanvasTexture(cv); t.anisotropy = 8; t.colorSpace = THREE.SRGBColorSpace; return t;")
rep("gr.addColorStop(0, 'rgba(255,128,170,0.95)'); gr.addColorStop(0.55, 'rgba(255,128,170,0.6)'); gr.addColorStop(1, 'rgba(255,128,170,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(cv); })();",
    "gr.addColorStop(0, 'rgba(255,128,170,0.95)'); gr.addColorStop(0.55, 'rgba(255,128,170,0.6)'); gr.addColorStop(1, 'rgba(255,128,170,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();")
rep("g.fillText(k, 64, 69); return new THREE.CanvasTexture(c); };", "g.fillText(k, 64, 69); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };")
rep("if (!snapRT) snapRT = new THREE.WebGLRenderTarget(S, S);", "if (!snapRT) snapRT = new THREE.WebGLRenderTarget(S, S, { colorSpace: THREE.SRGBColorSpace });")

# vertex colors are authored in sRGB; three reads them as linear now
rep("const smoothstep = (a, b, x) => {", "const linArr = a => { for (let i = 0; i < a.length; i++) { const v = a[i]; a[i] = v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); } return a; }; // sRGB vertex colors to linear\nconst smoothstep = (a, b, x) => {")
rep("mg.setAttribute('color', new THREE.BufferAttribute(colA, 3));", "mg.setAttribute('color', new THREE.BufferAttribute(linArr(colA), 3));")
rep("c[i * 3] = k[0]; c[i * 3 + 1] = k[1]; c[i * 3 + 2] = k[2]; } g.setAttribute('color', new THREE.BufferAttribute(c, 3)); return g; };",
    "c[i * 3] = k[0]; c[i * 3 + 1] = k[1]; c[i * 3 + 2] = k[2]; } g.setAttribute('color', new THREE.BufferAttribute(linArr(c), 3)); return g; };")
rep("wood.setAttribute('color', new THREE.BufferAttribute(col, 3));", "wood.setAttribute('color', new THREE.BufferAttribute(linArr(col), 3));")
rep("body.setAttribute('color', new THREE.BufferAttribute(col, 3));", "body.setAttribute('color', new THREE.BufferAttribute(linArr(col), 3));")
# rainbow effects keep their authored look
rep("c.setHSL((clock * 2.5) % 1, 0.95, 0.6);", "c.setHSL((clock * 2.5) % 1, 0.95, 0.6, THREE.SRGBColorSpace);")
rep("c.setHSL((clock * 0.55) % 1, 0.9, 0.6);", "c.setHSL((clock * 0.55) % 1, 0.9, 0.6, THREE.SRGBColorSpace);")
rep("orb.col.setHSL((clock * 0.2) % 1, 0.9, 0.62);", "orb.col.setHSL((clock * 0.2) % 1, 0.9, 0.62, THREE.SRGBColorSpace);")
rep("sp.material.color.setHSL(((clock * 0.2) + i / 6) % 1, 0.9, 0.7);", "sp.material.color.setHSL(((clock * 0.2) + i / 6) % 1, 0.9, 0.7, THREE.SRGBColorSpace);")

# custom shaders end with three's tone mapping and color space chunks
OUT = "\n  #include <tonemapping_fragment>\n  #include <colorspace_fragment>\n"
rep("vec3 g = vec3(dot(c, vec3(0.3, 0.5, 0.2))) * vec3(0.62, 0.64, 0.76); c = mix(c, g, rain * 0.7);\n    gl_FragColor = vec4(c, 1.0); }",
    "vec3 g = vec3(dot(c, vec3(0.3, 0.5, 0.2))) * vec3(0.62, 0.64, 0.76); c = mix(c, g, rain * 0.7);\n    gl_FragColor = vec4(c, 1.0);" + OUT + "  }")
rep("    gl_FragColor = vec4(col, 1.0);\n    #include <fog_fragment>\n  }", "    gl_FragColor = vec4(col, 1.0);" + OUT + "    #include <fog_fragment>\n  }")
rep("#else\n  gl_FragColor = vec4(col * lit, dilA);\n#endif\n}", "#else\n  gl_FragColor = vec4(col * lit, dilA);\n#endif" + OUT + "}")
rep("  else gl_FragColor = vec4(mix(dark, uColor * 0.32, inner * 0.6), uOp * 0.55);\n}", "  else gl_FragColor = vec4(mix(dark, uColor * 0.32, inner * 0.6), uOp * 0.55);" + OUT + "}")
rep("  c = mix(c, vec3(1.0), smoothstep(0.82, 0.9, vE));\n  gl_FragColor = vec4(c, 1.0);\n}", "  c = mix(c, vec3(1.0), smoothstep(0.82, 0.9, vE));\n  gl_FragColor = vec4(c, 1.0);" + OUT + "}")
rep("  c += hsv(fract(h + 0.33), 0.8, 1.0) * f * 0.8;\n  gl_FragColor = vec4(c, 1.0);\n}", "  c += hsv(fract(h + 0.33), 0.8, 1.0) * f * 0.8;\n  gl_FragColor = vec4(c, 1.0);" + OUT + "}")
rep("gl_FragColor = vec4(c, 0.08 + 0.72 * f + hl * 0.85); }'", "gl_FragColor = vec4(c, 0.08 + 0.72 * f + hl * 0.85);\\n#include <tonemapping_fragment>\\n#include <colorspace_fragment>\\n}'")
rep("    gl_FragColor = vec4(mix(c, hot, uHeat * 0.85), 1.0); }", "    gl_FragColor = vec4(mix(c, hot, uHeat * 0.85), 1.0);" + OUT + "  }")
rep("  gl_FragColor = vec4(mix(vec3(1.0), col, smoothstep(0.0, 0.5, uK)), 1.0);\n}", "  gl_FragColor = vec4(mix(vec3(1.0), col, smoothstep(0.0, 0.5, uK)), 1.0);" + OUT + "}")
# Performance mode's heat shimmer reads the frame back: keep it in half float so dark linear values don't band
rep("postRT = new THREE.WebGLRenderTarget(w, h, { samples: 4 });", "postRT = new THREE.WebGLRenderTarget(w, h, { samples: 4, type: THREE.HalfFloatType });")

# Graphics mode post: half-float targets, a bloom that takes what's brighter than white, then expose, tone map, grade, encode
rep("  const opt = { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat, depthBuffer: false, stencilBuffer: false };",
    "  const opt = { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat, type: THREE.HalfFloatType, depthBuffer: false, stencilBuffer: false };")
rep("uTh: { value: 0.74 }, uKnee: { value: 0.22 } }", "uTh: { value: 1.0 }, uKnee: { value: 0.35 } }")
rep("uVig: { value: 0.22 }, uHeat: { value: 0 }, uTime: { value: 0 } };", "uVig: { value: 0.22 }, uHeat: { value: 0 }, uTime: { value: 0 }, uExpo: { value: 1 } };")
rep("const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2, tDof; uniform vec4 uDof; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime; uniform vec3 uLift, uTint; varying vec2 vUv;\n    void main(){ vec2 uv = vUv;",
    "const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2, tDof; uniform vec4 uDof; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime, uExpo; uniform vec3 uLift, uTint; varying vec2 vUv;\n"
    "    // Khronos PBR Neutral: colors pass through as authored until they near white, then roll off softly and wash toward white\n"
    "    vec3 neutralTM(vec3 c){ float x = min(c.r, min(c.g, c.b)), off = x < 0.08 ? x - 6.25 * x * x : 0.04; c -= off; float pk = max(c.r, max(c.g, c.b)); if (pk < 0.76) return c; float d = 0.24, np = 1.0 - d * d / (pk + d - 0.76); c *= np / pk; float g = 1.0 - 1.0 / (0.15 * (pk - np) + 1.0); return mix(c, vec3(np), g); }\n"
    "    vec3 toSRGB(vec3 c){ c = max(c, 0.0); return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }\n"
    "    void main(){ vec2 uv = vUv;")
rep("      c += (texture2D(tB1, uv).rgb * 0.75 + texture2D(tB2, uv).rgb * 0.6) * uBloom;\n      float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, uSat);",
    "      c += (texture2D(tB1, uv).rgb * 0.75 + texture2D(tB2, uv).rgb * 0.6) * uBloom;\n      c = toSRGB(neutralTM(c * uExpo));\n      float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, uSat);")
rep("cu.uBloom.value = g.bloom || 0.5; bright.uniforms.uTh.value = g.th || 0.78;", "cu.uBloom.value = g.bloom || 0.5; bright.uniforms.uTh.value = g.thL || 1.0; cu.uExpo.value = g.expo || 1;")
open(p, 'w').write(s)
print('ok')
