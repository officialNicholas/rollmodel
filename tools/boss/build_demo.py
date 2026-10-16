"""Build a test page with the boss demo (v315): the test build, then the Sunken Keep stage, the boss and the demo over it if
tools/q260.py doesn't apply them already (since v315 it does). usage: BASE=<base page> VER=259:315 python3 tools/boss/build_demo.py game/_v315t.html"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
out = sys.argv[1]
subprocess.run([sys.executable, os.path.join(TOOLS, 'q260.py'), out, '--test'], check=True, env=os.environ)
s = open(out).read()
import v309_conquest_stage, v311_conquest_boss, v315_boss_demo
if 'function conqPreview()' not in s: s = v309_conquest_stage.apply(s); print('v309_conquest_stage ok')
if 'var BOSS = (() => {' not in s: s = v311_conquest_boss.apply(s); print('v311_conquest_boss ok')
if 'function cqbStart()' not in s: s = v315_boss_demo.apply(s); print('v315_boss_demo ok')
open(out, 'w').write(s); print('boss demo ok', len(s), out)
