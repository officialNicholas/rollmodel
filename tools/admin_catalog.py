"""admin_catalog.py <test page>: the game's catalog for the dashboard (admin/catalog.json), read out of the game itself.
Items (with their default prices), Strokes, modes, canvases, the tutorial's steps and the ad placements. Run it again when items or
prices change in the game. Needs a test build (window.__T) served on the local test server (port 8786)."""
import asyncio, sys, json, os
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/strokes_gear')
from h import *
PAGE = sys.argv[1] if len(sys.argv) > 1 else 't354.html'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'admin', 'catalog.json')
JS = r"""(() => {
  const keep = store.tut && store.tut.price; if (store.tut) store.tut.price = null; // (the lesson's own prices aside)
  if (store.st) store.st.lp = null; // (and any live prices: these are the game's defaults)
  const items = ITEMS.map(w => ({ id: w.id, name: w.name, slot: w.slot || null, stage: w.stage || null, season: !!w.season, gift: !!w.gift, find: !!needFind(w), price: PRICE(w) }));
  if (store.tut) store.tut.price = keep;
  const st = (kind, L) => L.map(s => ({ id: s.id, name: s.name, kind, craft_min: s.craft || null, rank: s.rank || null }));
  const strokes = [...st('special', SPECIALS), ...st('skill', SKILLS), ...st('transform', ST_ITEMS)];
  const modes = MODES.map(m => ({ id: m[0], name: m[1], sub: m[2] }));
  const stages = VOTE_STAGES.map(id => ({ id, name: (typeof ttName === 'function' ? ttName(id) : null) || id }));
  const lesson = TUT_STEPS.map(s => s.id);
  return JSON.stringify({ items, strokes, modes, stages, lesson });
})()"""
LESSON = {'move': 'steer and jump', 'free0': 'paint freely', 'sling': 'slingshot', 'free1': 'paint freely 2', 'basin': 'refill at a basin', 'rival': 'jump out, the rival arrives', 'pound': 'ground pound',
          'dodge': 'dodge roll', 'item': 'use a transform', 'rollover': 'roll over the rival', 'orb': 'grab the orb', 'free3': 'paint freely 3',
          'rocketdodge': 'dodge the rocket', 'flower': 'grab the gift', 'rest': 'finish the match'}
async def main():
    async with async_playwright() as p:
        br = await browser(p)
        A = await open_page(br, PAGE, '/tmp', save_of(), w=393, h=852)
        await A.until('lobbyOn()', 120)
        d = json.loads(await A.ev(JS))
        await br.close()
    # the tutorial, in the order a new player meets it (see admin/API.md, "tut" events)
    d['tutorial'] = ([{'id': 'intro', 'name': 'First launch intro'}, {'id': 'match', 'name': 'First lesson (match)'}]
        + [{'id': 'l:' + s, 'name': 'Lesson: ' + LESSON.get(s, s)} for s in d.pop('lesson')]
        + [{'id': 'shop', 'name': 'Paint Shop lesson'}, {'id': 'locker', 'name': 'Locker lesson'}, {'id': 'vote', 'name': 'Canvas vote lesson'},
           {'id': 'match2', 'name': 'Second match'}, {'id': 'done', 'name': 'Basics complete'}, {'id': 'rank2', 'name': 'Reached rank 2 (modes open)'},
           {'id': 'strokes', 'name': 'Strokes lesson'}, {'id': 'strokes_done', 'name': 'Strokes lesson done'}])
    d['ads'] = [{'id': 'craft', 'name': 'Skip a craft'}, {'id': 'lesson', 'name': 'Skip in the Strokes lesson'}]
    d['_about'] = 'Read out of the game by tools/admin_catalog.py. Prices here are the game\'s defaults; live prices set in the dashboard override them.'
    json.dump(d, open(OUT, 'w'), indent=1)
    print('items', len(d['items']), 'strokes', len(d['strokes']), 'modes', len(d['modes']), 'stages', len(d['stages']), 'tutorial', len(d['tutorial']))
asyncio.run(main())
