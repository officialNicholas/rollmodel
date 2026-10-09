#!/usr/bin/env python3
"""The animated UI sprites (Ludo: a still, then animateSprite on Hydra). Idempotent by request_id and by output file."""
import os, subprocess, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ART = S + '/art'; LUDO = S + '/tools/ludo.py'
def run(args, timeout=1200):
    r = subprocess.run(['python3', '-I', LUDO] + args, capture_output=True, text=True, timeout=timeout)
    print(' '.join(args[:3])[:90], '->', 'ok' if r.returncode == 0 else 'FAIL', (r.stderr.strip().splitlines() or [''])[-1][:200], flush=True)
    return r.returncode == 0
STILLS = [
  ('xp_base', 'ui_asset', 'a horizontal game HUD meter: a wide rounded-rectangle glass tube with a thick dark navy outline, empty and transparent inside, with a small round bright lime green cap on its left end, cel-shaded flat game UI, clean vector look, two colors navy and lime green only, isolated on transparent background, no text', ART + '/meter_base_2.png'),
  ('splat_still', 'sprite-vfx', 'a single small round glossy bright red paint drop seen from above, thick dark navy outline, cel-shaded, flat vector game VFX, isolated on transparent background', None),
  ('drip_still', 'sprite', 'a single glossy bright red paint droplet hanging down, teardrop shape, thick dark navy outline, one small white highlight, cel-shaded flat vector game sprite, isolated on transparent background', None),
  ('burst_still', 'sprite-vfx', 'a small bright lime green star spark with a thick dark navy outline, cel-shaded flat vector game VFX, isolated on transparent background', None),
]
ANIMS = [
  ('xp_fill', 'xp_base', 'the empty tube fills up from the left end to the right end with thick glossy lime green paint that sloshes and settles, the tube itself stays still', 3, 36, 'ui_asset'),
  ('splat_burst', 'splat_still', 'the drop bursts outward into a big wide glossy paint splat with flying droplets, then settles flat', 3, 36, 'sprite-vfx'),
  ('drip_loop', 'drip_still', 'the droplet stretches down, wobbles, and a small drip falls off its tip, looping', 3, 25, 'sprite'),
  ('burst_lime', 'burst_still', 'the spark explodes outward into a ring of sparkles and streaks that fly out and fade', 3, 25, 'sprite-vfx'),
]
for name, itype, prompt, ref in STILLS:
    out = f'{ART}/{name}.png'
    if os.path.exists(out): continue
    args = ['gen', out, itype, prompt, '--rid', 'rm4-' + name]
    args += ['--ref', ref] if ref else ['--style', 'Cel-Shaded']
    run(args)
for name, still, prompt, dur, frames, itype in ANIMS:
    out = f'{ART}/{name}.png'
    if os.path.exists(out) or not os.path.exists(f'{ART}/{still}.png'): continue
    run(['anim', out, f'{ART}/{still}.png', prompt, '--model', 'hydra', '--dur', str(dur), '--frames', str(frames), '--type', itype, '--rid', 'rm4-' + name])
