import numpy as np, sys
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
for nm in ('stand_tex0', 'crawl_tex0', 'crawl_tex1', 'stand_tex1'):
    im = Image.open(D + nm + '.png'); a = np.asarray(im.convert('RGB')).astype(float) / 255
    print(nm, im.size, im.mode, 'mean rgb', a.reshape(-1, 3).mean(0).round(3), 'p50', np.percentile(a.reshape(-1, 3), 50, axis=0).round(3), 'p90', np.percentile(a.reshape(-1, 3), 90, axis=0).round(3))
