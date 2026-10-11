"""Beat tracking (Ellis-style dynamic programming) on both songs, to see how steady the tempo is and where the bars fall"""
import numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2')
from analyze import FPS
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/music2/'
def track(e, bpm, tight=200):
    per = 60 / bpm * FPS; n = len(e); score = e.copy(); back = -np.ones(n, int)
    lo, hi = int(per * 0.5), int(per * 2)
    for i in range(hi, n):
        js = np.arange(i - hi, i - lo); pen = -tight * np.log((i - js) / per) ** 2
        k = np.argmax(score[js] + pen); score[i] = e[i] + score[js][k] + pen[k]; back[i] = js[k]
    i = int(np.argmax(score[-int(per * 2):])) + n - int(per * 2); bt = [i]
    while back[bt[-1]] >= 0: bt.append(back[bt[-1]])
    return np.array(bt[::-1]) / FPS
if __name__ == "__main__":
  for name, bpm, a, b in [('menu', 110.0, 6.928, 43.72223), ('spook', 105.45, 7.32, 46.21)]:
      e = np.load(D + name + '_e.npy'); bt = track(e, bpm)
      ib = np.diff(bt); print(name, 'beats', len(bt), 'median ibi', round(float(np.median(ib)), 4), '-> bpm', round(60 / float(np.median(ib)), 2))
      # local tempo over time, in 8-beat windows
      loc = [round(60 / float(np.mean(ib[i:i + 8])), 1) for i in range(0, len(ib) - 8, 8)]
      print('  local bpm', loc)
      # fit a straight line beat_k = t0 + k*per to the beats inside the loop
      sel = (bt > a - 0.3) & (bt < b + 0.3); k = np.arange(sel.sum()); A = np.vstack([k, np.ones_like(k)]).T; per, t0 = np.linalg.lstsq(A, bt[sel], rcond=None)[0]
      res = bt[sel] - (t0 + k * per); print('  fit bpm', round(60 / per, 3), 't0', round(t0, 4), 'resid ms max', round(float(np.abs(res).max()) * 1000, 1), 'rms', round(float(np.sqrt((res ** 2).mean())) * 1000, 1))
      print('  loop a in beats from t0:', round((a - t0) / per, 3), ' loop b:', round((b - t0) / per, 3), ' loop len beats', round((b - a) / per, 3))
      np.save(D + name + '_bt.npy', bt)
      print('  beats near loop start', [round(x, 3) for x in bt[(bt > a - 2) & (bt < a + 3)]])
      print('  beats near loop end', [round(x, 3) for x in bt[(bt > b - 2) & (bt < b + 1)]])
