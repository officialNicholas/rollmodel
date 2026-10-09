#!/usr/bin/env python3
"""Generate the Roll Model UI kit. Idempotent: skips files that exist, tags each request so a re-run returns the same job.
Usage: batch.py [group ...]   groups: icons buttons panels badges cards bg tex all
"""
import sys, os, subprocess, json, time
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ART = S + '/art'; LUDO = S + '/tools/ludo.py'; REF = ART + '/anchor_3.png'
VER = 'rm2'
STY = 'glossy toy-like stylized 3D mobile game UI, candy colors, thick dark navy outline, soft top highlight, small magenta and cyan paint splat flecks, Splatoon-inspired, clean silhouette, isolated on transparent background, no text'
ICO = 'flat-front game UI icon, chunky rounded shape, glossy candy finish, thick dark navy outline, bright color, readable at small size, ' + STY

JOBS = {
 'icons': [
  ('ic_gear',     'icon', 'a chunky settings gear cog, silver-blue, ' + ICO),
  ('ic_locker',   'icon', 'a clothes hanger with a small t-shirt, locker / wardrobe icon, pink, ' + ICO),
  ('ic_sound',    'icon', 'a loudspeaker with two sound waves, speaker on icon, cyan, ' + ICO),
  ('ic_mute',     'icon', 'a loudspeaker with a red X, muted speaker icon, ' + ICO),
  ('ic_music',    'icon', 'a pair of beamed music notes, purple, ' + ICO),
  ('ic_trophy',   'icon', 'a golden trophy cup with handles, ' + ICO),
  ('ic_crown',    'icon', 'a golden king crown with red gems, ' + ICO),
  ('ic_bucket',   'icon', 'a paint bucket tipping over with bright red paint pouring out, ' + ICO),
  ('ic_home',     'icon', 'a simple house home icon, yellow, ' + ICO),
  ('ic_replay',   'icon', 'two circular arrows replay / rematch icon, green, ' + ICO),
  ('ic_shuffle',  'icon', 'a white six-sided dice with red pips, ' + ICO),
  ('ic_help',     'icon', 'a bold question mark, orange, ' + ICO),
  ('ic_pause',    'icon', 'two vertical pause bars, white, ' + ICO),
  ('ic_play',     'icon', 'a right-pointing play triangle, white, ' + ICO),
  ('ic_back',     'icon', 'a bold left-pointing curved back arrow, white, ' + ICO),
  ('ic_edit',     'icon', 'a pencil writing, edit icon, yellow pencil, ' + ICO),
  ('ic_phone_p',  'icon', 'a smartphone standing upright in portrait orientation, front view, screen glowing with a cyan paint splat, ' + ICO),
  ('ic_phone_l',  'icon', 'a smartphone lying sideways in landscape orientation, front view, screen glowing with a cyan paint splat, ' + ICO),
  ('ic_medal1',   'icon', 'a gold first place medal on a red ribbon, with a star emblem, ' + ICO),
  ('ic_medal2',   'icon', 'a silver second place medal on a blue ribbon, with a star emblem, ' + ICO),
  ('ic_medal3',   'icon', 'a bronze third place medal on a green ribbon, with a star emblem, ' + ICO),
  ('ic_ko',       'icon', 'a cartoon impact starburst with dizzy stars, knockout icon, yellow and red, ' + ICO),
  ('ic_clock',    'icon', 'a round stopwatch timer, red and white, ' + ICO),
  ('ic_star',     'icon', 'a five-pointed star, gold, ' + ICO),
  ('ic_check',    'icon', 'a bold check mark, green, ' + ICO),
  ('ic_x',        'icon', 'a bold X close mark, red, ' + ICO),
  ('ic_gfx',      'icon', 'a sparkling diamond gem, graphics quality icon, cyan, ' + ICO),
  ('ic_bolt',     'icon', 'a lightning bolt, performance icon, yellow, ' + ICO),
  ('ic_eye',      'icon', 'a cartoon eye with a colorful iris, ' + ICO),
  ('ic_hat',      'icon', 'a stylish top hat, headgear category icon, purple, ' + ICO),
  ('ic_glasses',  'icon', 'a pair of sunglasses, face accessory icon, ' + ICO),
  ('ic_shirt',    'icon', 'a t-shirt, clothing category icon, teal, ' + ICO),
  ('ic_lock',     'icon', 'a closed padlock, grey, ' + ICO),
  ('ic_gift',     'icon', 'a wrapped gift box with a ribbon bow, pink and yellow, ' + ICO),
  ('ic_solo',     'icon', 'a single cute round slime blob character with big eyes, red glossy, ' + ICO),
  ('ic_duel',     'icon', 'two crossed paint rollers, versus icon, red and blue, ' + ICO),
  ('ic_trio',     'icon', 'three overlapping round paint splats, red blue and purple, ' + ICO),
  ('ic_easy',     'icon', 'a single chili pepper, green, ' + ICO),
  ('ic_hard',     'icon', 'three red chili peppers with fire, ' + ICO),
 ],
 'buttons': [
  ('btn_yellow', 'ui_asset', 'a plain wide rounded pill button, glossy candy yellow face with soft top highlight, thick dark navy outline, flat even edges with no decorations, ' + STY),
  ('btn_red',    'ui_asset', 'a plain wide rounded pill button, glossy bright red face with soft top highlight, thick dark navy outline, flat even edges with no decorations, ' + STY),
  ('btn_blue',   'ui_asset', 'a plain wide rounded pill button, glossy sky blue face with soft top highlight, thick dark navy outline, flat even edges with no decorations, ' + STY),
  ('btn_dark',   'ui_asset', 'a plain wide rounded pill button, deep navy purple glass face with faint top highlight, thick dark outline, flat even edges with no decorations, ' + STY),
  ('btn_cream',  'ui_asset', 'a plain wide rounded pill button, cream white face with soft top highlight, thick dark navy outline, flat even edges with no decorations, ' + STY),
  ('btn_round_red', 'ui_asset', 'a big round circular arcade push button, glossy bright red dome with a strong highlight, thick dark navy rim, ' + STY),
  ('btn_round_dark', 'ui_asset', 'a round circular button, deep navy purple glass with faint highlight, thick dark rim, ' + STY),
 ],
 'panels': [
  ('panel_dark',  'ui_asset', 'a large rounded rectangle UI panel, deep navy purple semi-translucent glass with subtle inner glow and faint top highlight, thick dark outline, flat plain edges with no decorations, ' + STY),
  ('panel_cream', 'ui_asset', 'a large rounded rectangle UI card, cream paper white with a subtle inner shadow, thick dark navy outline, flat plain edges with no decorations, ' + STY),
  ('tab_bar',     'ui_asset', 'a wide rounded capsule tab bar container, deep navy purple, thick dark outline, plain edges, ' + STY),
  ('pill_hud',    'ui_asset', 'a small rounded capsule HUD pill, deep navy glass with faint highlight, thick dark outline, plain edges, ' + STY),
 ],
 'badges': [
  ('badge_laurel', 'ui_asset', 'a golden laurel wreath badge with two curved branches of leaves and an empty center, trophy rank emblem, ' + STY),
  ('badge_ribbon', 'ui_asset', 'a wide red ribbon banner with folded ends and a gold trim, empty center for text, ' + STY),
  ('badge_burst',  'ui_asset', 'a bright yellow starburst badge with a thick dark navy outline, empty center, ' + STY),
  ('badge_new',    'ui_asset', 'a small tilted orange tag badge with a thick outline, empty center, ' + STY),
  ('splat_red',    'sprite-vfx', 'a flat splash of glossy bright red paint with drips and droplets, top-down, ' + STY),
  ('splat_blue',   'sprite-vfx', 'a flat splash of glossy sky blue paint with drips and droplets, top-down, ' + STY),
  ('splat_yellow', 'sprite-vfx', 'a flat splash of glossy yellow paint with drips and droplets, top-down, ' + STY),
  ('splat_purple', 'sprite-vfx', 'a flat splash of glossy purple paint with drips and droplets, top-down, ' + STY),
  ('drip_top',     'sprite-vfx', 'a horizontal strip of thick glossy red paint dripping downward from the top edge, several drips of different lengths, ' + STY),
  ('podium',       'sprite', 'a round glossy paint puddle podium platform seen from a low three-quarter angle, red paint pooled on a dark navy disc with a glowing cyan rim light, ' + STY),
 ],
 'cards': [
  ('card_solo', 'card-art', 'a cute round red glossy slime blob with big happy eyes and floppy ears rolling alone across a wooden floor leaving a thick trail of red paint, dynamic action pose, ' + STY),
  ('card_duel', 'card-art', 'two cute round glossy slime blobs with big eyes, one red and one blue, charging at each other across a floor splattered with red and blue paint, dynamic versus composition, ' + STY),
  ('card_trio', 'card-art', 'three cute round glossy slime blobs, red, blue and purple, bouncing in a chaotic paint fight with splashes of all three colors flying, ' + STY),
 ],
 'bg': [
  ('bg_menu_p', 'fixed_background', 'stylized 3D cartoon paint arena stadium interior at night, a bright empty circular stage in the center lit by colorful spotlights, floor and walls covered in glossy red, blue and yellow paint splashes, confetti in the air, soft depth of field blur, vibrant, no characters, no text, mobile game lobby background, portrait', 'ar_9_16'),
  ('bg_menu_l', 'fixed_background', 'stylized 3D cartoon paint arena stadium interior at night, a bright empty circular stage in the center lit by colorful spotlights, floor and walls covered in glossy red, blue and yellow paint splashes, confetti in the air, soft depth of field blur, vibrant, no characters, no text, mobile game lobby background, landscape', 'ar_16_9'),
  ('bg_results', 'fixed_background', 'dark navy purple abstract background with bold diagonal stripes and large glossy paint splats in red, blue and yellow around the edges, center mostly clear and dark, stylized 3D cartoon, mobile game results screen backdrop, no characters, no text', 'ar_9_16'),
  ('bg_locker', 'fixed_background', 'bright stylized 3D cartoon dressing room with soft pink and cream walls, a round spotlight on an empty wooden floor center, clothes racks blurred at the sides, paint splats on the walls, no characters, no text, mobile game customization background', 'ar_9_16'),
 ],
 'tex': [
  ('tex_splats',  'texture', 'seamless repeating pattern of small glossy cartoon paint splats and droplets in magenta, cyan, yellow and white on a deep navy purple background, sparse, playful mobile game UI wallpaper'),
  ('tex_stripes', 'texture', 'seamless repeating bold diagonal stripe pattern, two tones of deep purple, clean vector look'),
 ],
}

def run(name, itype, prompt, ar=None, ref=True):
    out = f'{ART}/{name}.webp'
    if os.path.exists(out):
        return
    cmd = ['python3', '-I', LUDO, 'gen', out.replace('.webp', '.png'), itype, prompt, '--rid', f'{VER}-{name}']
    if ref and itype not in ('fixed_background', 'texture', 'card-art'):
        cmd += ['--ref', REF]
    else:
        cmd += ['--style', 'Stylized 3D']
        if ar: cmd += ['--ar', ar]
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(out.replace('.webp', '.png'))
    if ok:
        os.rename(out.replace('.webp', '.png'), out)
    print(f'{name:16} {"ok" if ok else "FAIL"} {time.time()-t:.0f}s {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""} {r.stdout.strip()[-120:] if not ok else ""}', flush=True)

groups = sys.argv[1:] or ['all']
for g, jobs in JOBS.items():
    if 'all' in groups or g in groups:
        for j in jobs:
            run(*j)
