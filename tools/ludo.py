#!/usr/bin/env python3
"""Small Ludo.ai client. Auth is injected by the session proxy.

Usage:
  ludo.py account
  ludo.py gen  <out.png> <image_type> "<prompt>" [--style "Art style"] [--ar ar_1_1] [--n 1] [--ref style.png]
  ludo.py edit <out.png> <in.png> "<prompt>" [--type ui_asset]
  ludo.py rmbg <out.png> <in.png> [--crop]
  ludo.py job  <id>
Results with n>1 are saved as out_1.png, out_2.png ...
"""
import sys, json, time, base64, argparse, urllib.request, urllib.error, os

BASE = 'https://api.ludo.ai/api'


def call(method, path, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or 'null')
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {'raw': txt}


def wait_job(jid, log=True):
    t0 = time.time()
    while True:
        st, j = call('GET', f'/assets/jobs/{jid}?wait=10', timeout=60)
        if st != 200:
            print(f'  poll {st}, retrying', file=sys.stderr); time.sleep(4); continue
        s = j.get('status')
        if s == 'succeeded':
            if log: print(f'  done in {time.time()-t0:.0f}s, credits {j.get("credits_charged")}', file=sys.stderr)
            return j['result']
        if s in ('failed', 'canceled'):
            raise SystemExit(f'job {s}: {j.get("error")}')
        time.sleep(max(1, j.get('poll_after_ms', 3000) / 1000))


def submit(path, body):
    st, j = call('POST', path, body)
    if st == 202:
        print(f'  queued {j["id"]}', file=sys.stderr)
        return wait_job(j['id'])
    if st == 200:
        return j
    raise SystemExit(f'{path} failed {st}: {json.dumps(j)[:800]}')


def download(url, out):
    with urllib.request.urlopen(url, timeout=120) as r, open(out, 'wb') as f:
        f.write(r.read())


def save_results(res, out):
    if isinstance(res, dict):
        res = [res]
    outs = []
    for i, r in enumerate(res):
        o = out if len(res) == 1 else out.replace('.png', f'_{i+1}.png')
        download(r['url'], o)
        outs.append(o)
        print(o, r['url'])
    return outs


def b64(path):
    ext = path.rsplit('.', 1)[-1].lower()
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('args', nargs='*')
    ap.add_argument('--style')
    ap.add_argument('--ar', default='default')
    ap.add_argument('--n', type=int, default=1)
    ap.add_argument('--ref')
    ap.add_argument('--type')
    ap.add_argument('--crop', action='store_true')
    ap.add_argument('--persp')
    ap.add_argument('--rid')
    ap.add_argument('--model', default='hydra')
    ap.add_argument('--dur', type=float, default=3)
    ap.add_argument('--frames', type=int, default=36)
    a = ap.parse_args()
    if a.cmd == 'account':
        print(json.dumps(call('GET', '/assets/account')[1], indent=1)); return
    if a.cmd == 'job':
        print(json.dumps(call('GET', f'/assets/jobs/{a.args[0]}')[1], indent=1)); return
    if a.cmd == 'fetch':
        save_results(wait_job(a.args[1]), a.args[0]); return
    if a.cmd == 'gen':
        out, itype, prompt = a.args[:3]
        if a.ref:
            body = {'style_image': b64(a.ref), 'prompt': prompt, 'image_type': itype, 'n': a.n}
            if a.rid: body['request_id'] = a.rid
            res = submit('/assets/image/style', body)
        else:
            body = {'image_type': itype, 'prompt': prompt, 'n': a.n, 'aspect_ratio': a.ar}
            if a.style: body['art_style'] = a.style
            if a.persp: body['perspective'] = a.persp
            if a.rid: body['request_id'] = a.rid
            res = submit('/assets/image', body)
        save_results(res, out); return
    if a.cmd == 'edit':
        out, src, prompt = a.args[:3]
        body = {'image': b64(src), 'prompt': prompt, 'n': a.n}
        if a.type: body['image_type'] = a.type
        if a.ref: body['reference_image'] = b64(a.ref)
        save_results(submit('/assets/image/edit', body), out); return
    if a.cmd == 'rmbg':
        out, src = a.args[:2]
        save_results(submit('/assets/image/remove-background', {'image': b64(src), 'crop': a.crop, 'creative_edit': False}), out); return
    if a.cmd == 'anim':
        out, src, prompt = a.args[:3]
        body = {'initial_image': b64(src) if not src.startswith('http') else src, 'motion_prompt': prompt, 'model': a.model, 'duration': a.dur, 'frames': a.frames, 'image_type': a.type or 'ui_asset', 'loop': True, 'crop': False, 'frame_size': 0}
        if a.rid: body['request_id'] = a.rid
        r = submit('/assets/sprite/animate', body)
        print(json.dumps({k: v for k, v in r.items() if k != 'individual_frame_urls'}, indent=1))
        download(r['spritesheet_url'], out); print(out)
        if r.get('video_url'): download(r['video_url'], out.rsplit('.', 1)[0] + '.mp4')
        if r.get('audio_url'): download(r['audio_url'], out.rsplit('.', 1)[0] + '.' + r['audio_url'].rsplit('.', 1)[-1].split('?')[0])
        return
    if a.cmd == 'voice':
        out, desc, text = a.args[:3]
        body = {'voice_description': desc, 'text': text, 'type': a.type or 'non-human'}
        if a.rid: body['request_id'] = a.rid
        r = submit('/audio/voice', body); r = r[0] if isinstance(r, list) else r; download(r['url'], out); print(out, r['url']); return
    if a.cmd == 'speech':
        out, sample, text = a.args[:3]
        body = {'text': text, 'sample': sample if sample.startswith('http') else 'data:audio/mp3;base64,' + base64.b64encode(open(sample, 'rb').read()).decode()}
        if a.rid: body['request_id'] = a.rid
        r = submit('/audio/speech', body); r = r[0] if isinstance(r, list) else r; download(r['url'], out); print(out, r['url']); return
    if a.cmd == 'sfx':
        out, desc = a.args[:2]
        body = {'description': desc, 'duration': 0 if a.dur == 3 else a.dur}
        if a.rid: body['request_id'] = a.rid
        r = submit('/audio/sound-effect', body); r = r[0] if isinstance(r, list) else r; download(r['url'], out); print(out, r['url']); return
    raise SystemExit('unknown cmd')


if __name__ == '__main__':
    main()
