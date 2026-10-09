# Black boxes on the power-up bubbles: the bubble's rim term took pow() of a value that can dip a hair below zero where the surface
# faces the camera dead on (pow of a negative is NaN on the GPU), and its alpha could pass 1 on the highlight, which subtracts the
# background and leaves negative color. One bad pixel in the HDR frame then smears through the bloom blur into a black square.
# Fix the source (normalize, clamp), harden the other rim terms written the same way, and scrub NaN/Inf/negatives wherever the
# frame gets sampled for blur (bloom, depth of field, composite, mirror, jelly refraction) so no stray pixel can ever grow into a box.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# the bubble
rep("fragmentShader: 'uniform float uTime; varying vec3 vN; varying vec3 vV; void main(){ float d = max(dot(vN, vV), 0.0), f = pow(1.0 - d, 2.2); float hl = smoothstep(0.92, 0.97, dot(vN, normalize(vec3(-0.45, 0.6, 0.66)))); vec3 film = 0.55 + 0.45 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + d * 1.7 + vN.y * 0.4 + uTime * 0.06)); vec3 c = mix(mix(vec3(0.82, 0.94, 1.0), film, 0.75 * smoothstep(0.05, 0.75, 1.0 - d)), vec3(1.0), hl); gl_FragColor = vec4(c, 0.1 + 0.72 * f + hl * 0.85);",
    "fragmentShader: 'uniform float uTime; varying vec3 vN; varying vec3 vV; void main(){ vec3 n = normalize(vN), v = normalize(vV); float d = clamp(dot(n, v), 0.0, 1.0), f = pow(max(1.0 - d, 1e-5), 2.2); float hl = smoothstep(0.92, 0.97, dot(n, normalize(vec3(-0.45, 0.6, 0.66)))); vec3 film = 0.55 + 0.45 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + d * 1.7 + n.y * 0.4 + uTime * 0.06)); vec3 c = mix(mix(vec3(0.82, 0.94, 1.0), film, 0.75 * smoothstep(0.05, 0.75, 1.0 - d)), vec3(1.0), hl); gl_FragColor = vec4(c, clamp(0.1 + 0.72 * f + hl * 0.85, 0.0, 1.0));")
# the giant orb, written the same way
rep("vec3 p = normalize(vP); float f = pow(1.0 - max(dot(vN, vV), 0.0), 1.5);",
    "vec3 p = normalize(vP); float f = pow(max(1.0 - clamp(dot(normalize(vN), normalize(vV)), 0.0, 1.0), 1e-5), 1.5);")
# water and paint rim terms
rep("float fr = 0.02 + 0.98 * pow(1.0 - max(dot(n, V), 0.0), 5.0);", "float fr = 0.02 + 0.98 * pow(max(1.0 - clamp(dot(n, V), 0.0, 1.0), 1e-5), 5.0);")
rep("fres = pow(1.0 - max(dot(nb, V), 0.0), 3.0) * 0.28;", "fres = pow(max(1.0 - clamp(dot(nb, V), 0.0, 1.0), 1e-5), 3.0) * 0.28;")
rep("float fr = 0.035 + 0.965 * pow(1.0 - max(dot(nb, V), 0.0), 5.0);", "float fr = 0.035 + 0.965 * pow(max(1.0 - clamp(dot(nb, V), 0.0, 1.0), 1e-5), 5.0);")

# the scrub: NaN and Inf have an all-ones exponent; checked on the bits, so fast-math compilers can't optimize it away
FIN = "vec3 fin3(vec3 c){ return mix(clamp(c, 0.0, 6e4), vec3(0.0), equal(floatBitsToUint(c) & uvec3(0x7f800000u), uvec3(0x7f800000u))); }\n    "
rep("vec3 pick(vec2 uv){ vec3 c = texture2D(tSrc, uv).rgb; float l",
    FIN + "vec3 pick(vec2 uv){ vec3 c = fin3(texture2D(tSrc, uv).rgb); float l")
rep("""`uniform sampler2D tSrc; uniform vec2 uPx; varying vec2 vUv;
    void main(){ gl_FragColor = vec4((texture2D(tSrc, vUv + uPx * vec2(-0.5, -0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(0.5, -0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(-0.5, 0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(0.5, 0.5)).rgb) * 0.25, 1.0); }`""",
    """`uniform sampler2D tSrc; uniform vec2 uPx; varying vec2 vUv;
    """ + FIN + """void main(){ gl_FragColor = vec4((fin3(texture2D(tSrc, vUv + uPx * vec2(-0.5, -0.5)).rgb) + fin3(texture2D(tSrc, vUv + uPx * vec2(0.5, -0.5)).rgb) + fin3(texture2D(tSrc, vUv + uPx * vec2(-0.5, 0.5)).rgb) + fin3(texture2D(tSrc, vUv + uPx * vec2(0.5, 0.5)).rgb)) * 0.25, 1.0); }`""")
rep("    vec3 toSRGB(vec3 c){ c = max(c, 0.0);", "    " + FIN + "vec3 toSRGB(vec3 c){ c = max(c, 0.0);")
rep("      vec3 c = texture2D(tScene, uv).rgb;\n      // tilt-shift", "      vec3 c = fin3(texture2D(tScene, uv).rgb);\n      // tilt-shift")
# the mirror's mip chain and the jelly's view through itself sample the frame too
rep("vec3 mir = textureLod(uMirror, muv, clamp(material.roughness * 10.0 - 0.6, 0.0, 6.0)).rgb; radiance = mix(radiance, mir, k);",
    "vec3 mir = textureLod(uMirror, muv, clamp(material.roughness * 10.0 - 0.6, 0.0, 6.0)).rgb; mir = mix(clamp(mir, 0.0, 6e4), vec3(0.0), equal(floatBitsToUint(mir) & uvec3(0x7f800000u), uvec3(0x7f800000u))); radiance = mix(radiance, mir, k);")
rep("vec3 bg = vec3(texture2D(uGrab, suv + off * 1.08).r, texture2D(uGrab, suv + off).g, texture2D(uGrab, suv + off * 0.92).b);",
    "vec3 bg = vec3(texture2D(uGrab, suv + off * 1.08).r, texture2D(uGrab, suv + off).g, texture2D(uGrab, suv + off * 0.92).b); bg = mix(clamp(bg, 0.0, 6e4), vec3(0.0), equal(floatBitsToUint(bg) & uvec3(0x7f800000u), uvec3(0x7f800000u)));")
open(p, 'w').write(s)
print('ok')
