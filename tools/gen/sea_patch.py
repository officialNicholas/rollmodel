# water seen through the island's holes: calm, no shore foam (the noise-driven foam made square blotches there)
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
rep = [
("    if (dA < 0.0) d = 0.45; // water under the island, seen through its holes: shallow and calm\n",
 "    float calm = dA < 0.0 ? 1.0 : 0.0; if (calm > 0.5) d = 0.45; // water under the island, seen through its holes: shallow and calm\n"),
("    #endif\n    vec3 n = normalize(vec3(-g.x, 1.0, -g.y));\n    float fr = 0.02",
 "    #endif\n    g *= 1.0 - 0.65 * calm;\n    vec3 n = normalize(vec3(-g.x, 1.0, -g.y));\n    float fr = 0.02"),
("    float foam = smoothstep(0.55, 0.05, d + (nz - 0.5) * 0.35);\n",
 "    float foam = smoothstep(0.55, 0.05, d + (nz - 0.5) * 0.35) * (1.0 - calm);\n"),
("    float surf = step(0.72, fract(d * 0.55 - t * 0.28 + nz * 0.3)) * smoothstep(3.2, 0.6, d) * smoothstep(0.35, 0.7, nz);\n    col = mix(col, vec3(1.0), clamp(foam * 0.9 + surf * 0.5, 0.0, 1.0));\n",
 "    float surf = step(0.72, fract(d * 0.55 - t * 0.28 + nz * 0.3)) * smoothstep(3.2, 0.6, d) * smoothstep(0.35, 0.7, nz) * (1.0 - calm);\n    col = mix(col, vec3(1.0), clamp(foam * 0.9 + surf * 0.5, 0.0, 1.0));\n    // in the holes, just soft light rippling over the shallow bottom\n    float rl = 0.5 + 0.5 * sin(p.x * 2.6 + t * 1.1 + 1.7 * sin(p.y * 1.9 - t * 0.8)) * sin(p.y * 2.3 - t * 0.9 + 1.5 * sin(p.x * 1.6 + t * 0.7));\n    col += calm * uSunC * 0.08 * rl * rl;\n"),
]
for a, b in rep:
    assert s.count(a) == 1, (s.count(a), a[:60])
    s = s.replace(a, b)
open(p, 'w').write(s)
print('ok')
