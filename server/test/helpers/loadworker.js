// A load-test worker process: runs some of the rooms' bots, so no single process starves (the server runs in its own
// process too). Talks to the test over IPC: 'setup' -> 'started', 'mark' -> 'marked', 'report' -> stats, 'quit'.
import { Bot } from './bot.js';
import { until } from './harness.js';

let bots = [];
const send = m => process.send(m);
process.on('message', async m => {
  try {
    if (m.t === 'setup') {
      const { url, firstRoom, rooms, per, mode } = m;
      bots = Array.from({ length: rooms * per }, (_, i) => new Bot({ url, name: 'Load' + (firstRoom * per + i), behavior: 'wander', hz: 30, autoReconnect: false, seed: 1000 + firstRoom * per + i }));
      for (let i = 0; i < bots.length; i += 25) await Promise.all(bots.slice(i, i + 25).map(b => b.connect()));
      const starts = bots.map(b => b.wait('start', () => true, 120000));
      for (let r = 0; r < rooms; r++) {
        const g = bots.slice(r * per, r * per + per), code = await g[0].net.createRoom(mode);
        await Promise.all(g.slice(1).map(b => b.net.joinRoom(code)));
        for (const b of g) b.net.ready(true);
      }
      await Promise.all(starts);
      const latest = Math.max(...bots.map(b => b.startAt));
      await until(() => bots[0].net.serverNow() > latest + 800, 30000);
      send({ t: 'started', n: bots.length });
    } else if (m.t === 'mark') {
      send({ t: 'marked', bytesOut: bots.reduce((a, b) => a + b.net.stats().bytesOut, 0) });
    } else if (m.t === 'report') {
      send({ t: 'report', bytesOut: bots.reduce((a, b) => a + b.net.stats().bytesOut, 0), snapRates: bots.map(b => b.net.stats().snapshotsPerSec), interp: bots.map(b => b.net.stats().interpDelay), corrections: bots.reduce((a, b) => a + b.stats.corrections, 0), why: bots.flatMap(b => b.events.filter(e => e[0] === 'correction').map(e => e[1])), zero: bots.filter(b => b.net.stats().snapshotsPerSec < 20).map(b => ({ n: b.net.name, shard: b.net._shard, connected: b.net.connected, match: !!b.net.match, ended: !!b.ended, out: b.out, dead: b.dead })).slice(0, 8), kicked: bots.filter(b => b.kicked).map(b => b.kicked), events: bots.filter(b => b.events.length).map(b => b.events).slice(0, 5) });
    } else if (m.t === 'quit') {
      for (const b of bots) b.close();
      setTimeout(() => process.exit(0), 200);
    }
  } catch (e) { send({ t: 'error', message: e.stack || e.message }); }
});
send({ t: 'ready' });
