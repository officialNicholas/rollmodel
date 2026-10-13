import subprocess, concurrent.futures as cf, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; D = S + '/art/stroke'
PICK = {'rocket': 1, 'giant': 3, 'freeze': 3, 'swim': 1, 'repel': 3, 'pockets': 1, 'soon': 4}
def cut(n):
    src, out = f'{D}/{n}_{PICK[n]}.png', f'{D}/{n}_cut.png'
    if os.path.exists(out): return n, 'exists'
    r = subprocess.run(['python3', '-I', S + '/tools/ludo.py', 'rmbg', out, src, '--crop'], capture_output=True, text=True)
    return n, 'ok' if r.returncode == 0 and os.path.exists(out) else 'FAIL ' + (r.stderr or r.stdout)[-300:]
with cf.ThreadPoolExecutor(4) as ex:
    for n, st in ex.map(cut, PICK): print(n, st, flush=True)
