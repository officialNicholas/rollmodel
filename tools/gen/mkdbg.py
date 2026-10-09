# debug pages: the slime body showing one expression as flat color (no lighting), e.g. albedo or masks
import sys
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
s = open(SP + 'pc_t.html').read()
a = "totalEmissiveRadiance += diffuseColor.rgb * stageLit(vGooW, vec3(0.0, 1.0, 0.0)) * 0.45 * (1.0 - vSlimeAO * 0.6);` : '';"
assert s.count(a) == 1
dbg = "totalEmissiveRadiance += diffuseColor.rgb * stageLit(vGooW, vec3(0.0, 1.0, 0.0)) * 0.45 * (1.0 - vSlimeAO * 0.6);\\n{ reflectedLight.directDiffuse = vec3(0.0); reflectedLight.indirectDiffuse = vec3(0.0); reflectedLight.directSpecular = vec3(0.0); reflectedLight.indirectSpecular = vec3(0.0); totalEmissiveRadiance = EXPR; \\n#ifdef USE_CLEARCOAT\\n material.clearcoat = 0.0;\\n#endif\\n#ifdef USE_SHEEN\\n material.sheenColor = vec3(0.0);\\n#endif\\n }` : '';"
for arg in sys.argv[1:]:
    name, expr = arg.split('=', 1)
    open(SP + name + '.html', 'w').write(s.replace(a, dbg.replace('EXPR', expr)))
    print('wrote', name)
