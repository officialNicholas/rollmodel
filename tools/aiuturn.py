"""What sets off the CPU's U-turns (heading reversed by more than 2.4 rad within 1.2 s while rolling): reads the steering traces
aiwiggle.py saved (scratchpad/aiwig_<stage>_<diff>_<team>[_tag].json) and puts each U-turn down to a re-plan (new target), a mode
change, the hazard check, reaching the target, or the route itself doubling back.
usage: aiuturn.py <trace json> [...]"""
import json, math, sys
wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
tot = {}; n = 0; dur = 0
for p in sys.argv[1:]:
    tr = json.load(open(p)); dur += (tr[-1][0] - tr[0][0]) if tr else 0
    # rows: t, tx, tz, x, z, yaw, steer, mode, urgent, precise, safeWant, safeRes, charging, spd, pi, pathLen, tgt, turn
    i0 = 0; cd = -9; causes = {}
    for i, r in enumerate(tr):
        if r[12] or r[13] < 1.5: i0 = i + 1; continue
        while tr[i0][0] < r[0] - 1.2: i0 += 1
        if r[0] - cd > 1.2 and abs(wrap(r[5] - tr[i0][5])) > 2.4:
            seg = tr[i0:i + 1]; cd = r[0]
            if any(s[16] != seg[0][16] for s in seg): k = 'replan'
            elif any(s[7] != seg[0][7] for s in seg): k = 'mode change'
            elif any(s[10] is not None and abs(wrap(s[11] - s[10])) > 0.5 for s in seg): k = 'hazard'
            elif any(s[14] >= s[15] - 1 for s in seg): k = 'at target'
            else: k = 'route doubles back'
            causes[k] = causes.get(k, 0) + 1
    n += sum(causes.values()); print(p.split('/')[-1], causes)
    for k, v in causes.items(): tot[k] = tot.get(k, 0) + v
print(f'ALL: {n} U-turns in {dur:.0f}s ({60 * n / max(1, dur):.1f}/min)', tot)
