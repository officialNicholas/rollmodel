"""Sum up aisim runs side by side: steering (flips, U-turns, wiggles per minute moving), coverage, time stuck, knock-outs by cause
(per blob per match), and the planner's cost. usage: aicompare.py <tag> [tag...]  (reads scratchpad/aisim_<tag>.json)"""
import json, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
for tag in sys.argv[1:]:
    R = json.load(open(f'{S}/aisim_{tag}.json'))
    dsp = []; low = []; rf = 0; rfp = 0; fl = []; ut = []; wg = []; cov = []; st = []; why = {}; th = []; fs = []; dj = []; nb = 0; flings = 0; pounds = 0
    for r in R:
        M = r['M']; th += M['think']; fs += M['fling']; dj += M['dij']
        for bl in r['blobs']:
            m = M['D'][str(bl['team'])]; mv = max(1e-6, m['moving']); pl = max(1e-6, m['play']); nb += 1
            fl.append(60 * m['flips'] / mv); ut.append(60 * m['uturn'] / mv); wg.append(60 * m.get('wig', 0) / mv); cov.append(bl['cov']); st.append(100 * m['stuck'] / pl)
            flings += m['flings']; pounds += m['pounds']; dsp.extend(m.get('drySp', [])); low.append(m.get('lowT', 0)); rf += m.get('refills', 0); rfp += m.get('refP', 0)
            for k, v in (bl['why'] or {}).items(): why[k] = why.get(k, 0) + v
    th.sort(); q = lambda a, f: a[min(len(a) - 1, int(f * len(a)))]; mean = lambda a: sum(a) / max(1, len(a))
    self_outs = sum(v for k, v in why.items() if k in ('fall', 'dry'))
    print(f"{tag:8s} {len(R)} matches  flips/min {mean(fl):.1f}  U-turns/min {mean(ut):.1f}  wiggles/min {mean(wg):.1f}  cov {mean(cov):.1f}%  stuck {mean(st):.2f}%  "
          f"flings/blob {flings / nb:.1f}  pounds/blob {pounds / nb:.1f}  outs {dict(sorted(why.items()))}  falls+dry per blob-match {self_outs / nb:.3f}  "
          f"dry spells/blob {len(dsp) / nb:.2f} (by phase {dict((k, sum(1 for d in dsp if d[1] == k)) for k in set(d[1] for d in dsp))})  near-empty s/blob {mean(low):.1f}  refill trips/blob {rf / nb:.1f} at paint {rfp / max(1, rf):.2f}  "
          f"think mean {mean(th):.2f} p95 {q(th, .95):.2f} p99 {q(th, .99):.2f} ms")
