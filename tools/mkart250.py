"""The v250 gallery art from the stage photos: the Blank Canvas and Palette Island frames (720x495), the Season 1 frame as the three
Spooky SZN stages side by side (triptych.py), and the season grid's photos (440x302), each as WebP base64 in tools/stage/art/<name>.b64"""
import io, os, base64, subprocess, sys
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; UI = S + '/ws/ui/'; ART = S + '/tools/stage/art/'
def pick(*names):
    for n in names:
        if os.path.exists(UI + n): return UI + n
    raise SystemExit('missing ' + str(names))
def b64(im, q=82):
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6); return base64.b64encode(buf.getvalue()).decode()
def put(name, im):
    open(ART + name + '.b64', 'w').write(b64(im)); im.save(UI + 'art_' + name + '.png'); print(name, im.size, os.path.getsize(ART + name + '.b64'))
blank, island = pick('photo_blank2.png', 'photo_blank.png'), pick('photo_island2.png', 'photo_island.png')
crypt, cath, manor = pick('photo_crypt.png'), pick('photo_cathedral.png'), pick('photo_manor.png')
put('blank', Image.open(blank).convert('RGB').resize((720, 495), Image.LANCZOS)); put('island', Image.open(island).convert('RGB').resize((720, 495), Image.LANCZOS))
subprocess.run([sys.executable, '-I', S + '/tools/triptych.py', crypt, cath, manor, UI + 'season_tri.png', '720', '495'], check=True)
tri = Image.open(UI + 'season_tri.png').convert('RGB'); put('season', tri); put('season_s', tri.resize((440, 302), Image.LANCZOS))
for n, f in (('crypt', crypt), ('cathedral', cath), ('manor', manor)): put(n + '_s', Image.open(f).convert('RGB').resize((440, 302), Image.LANCZOS))
