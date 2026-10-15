# quick build: the release before (game/index.html) + the first-launch intro (v257_intro.py) + its v260 glue -> argv[1]; --test adds window.__T
import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
src = os.path.join(os.path.dirname(HERE), 'game', 'index.html')
s = open(os.environ.get('BASE', src)).read()
OLD, NEW = os.environ.get('VER', '259:260').split(':')
assert s.count('<p class="ver">Version %s</p>' % OLD) == 1; s = s.replace('<p class="ver">Version %s</p>' % OLD, '<p class="ver">Version %s</p>' % NEW)
for m in ['v257_intro', 'v260_intro_glue', 'v269_settings', 'v269_boot', 'v270_loadout', 'v271_whirl', 'v272_tips', 'v273_modes', 'v274_victory', 'v275_strokes', 'v276_claim', 'v277_flat', 'v278_bootbar', 'v279_aggressive', 'v280_ready', 'v281_transforms', 'v282_modes_short', 'v283_skip_sfx_sd', 'v284_vs_center', 'v285_items', 'v285_feed', 'v285_intro_set', 'v285_intro_drum', 'v285_intro_turn', 'v285_first_steer', 'v285_hide', 'v286_items_craft', 'v287_strokes_paper', 'v288_intro_title', 'v289_rookie_line', 'v290_trysd_open', 'v291_strokes_notebook', 'v292_unlock_line', 'v293_trial_board', 'v293_perf', 'v294_lane_soft', 'v295_turn_cam']:
    s = importlib.import_module(m).apply(s); print(m, 'ok')
if '--test' in sys.argv:
    a = '\nrequestAnimationFrame(frame);\n};'; assert s.count(a) == 1; s = s.replace(a, '\nwindow.__T = { ev: s => eval(s) };' + a)
    a = '  api.after = after;\n'; assert s.count(a) == 1; s = s.replace(a, a + '  api.handoff = handoff; api.X = () => X; // (test build only: the probes jump straight to the end, and look inside)\n')
out = sys.argv[1]; open(out, 'w').write(s); print('q260 ok', len(s), out)
