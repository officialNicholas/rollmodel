// pn: after a deploy of several machines, check the routing on the live server: each game machine is reached when
// asked for by name (?s=, Fly's fly-replay), and a room made on one machine is joined from another.
// usage: node bench/flycheck.js wss://rollmodel-game.fly.dev/ws <machine id> <machine id> ...   (ids: fly m list)
import { RMNet } from '../client/rmnet.js';

const [url, ...ids] = process.argv.slice(2);
if (!url || ids.length < 2) { console.log('usage: node bench/flycheck.js <wss url> <game machine id> <game machine id> ...'); process.exit(2); }
let bad = 0;
for (const id of ids) {
  const net = new RMNet({ url: url + '?s=' + id, name: 'Check', autoReconnect: false });
  try { const w = await net.connect(); const ok = w.shard === id; if (!ok) bad++; console.log((ok ? 'ok   ' : 'WRONG') + ' asked for ' + id + ', got ' + w.shard); }
  catch (e) { bad++; console.log('FAIL  ' + id + ': ' + e.message); }
  net.close();
}
// a room across two machines
const host = new RMNet({ url: url + '?s=' + ids[0], name: 'Host', autoReconnect: false }), guest = new RMNet({ url: url + '?s=' + ids[1], name: 'Guest', autoReconnect: false });
try {
  await host.connect(); await guest.connect();
  const code = await host.createRoom('duel'); const r = await guest.joinRoom(code);
  const ok = r.code === code && guest._shard === ids[0]; if (!ok) bad++;
  console.log((ok ? 'ok   ' : 'WRONG') + ' room ' + code + ' made on ' + ids[0] + ', joined from ' + ids[1] + ' (guest now on ' + guest._shard + ')');
  await host.leaveRoom().catch(() => {}); await guest.leaveRoom().catch(() => {});
} catch (e) { bad++; console.log('FAIL  room: ' + e.message); }
host.close(); guest.close();
console.log(bad ? bad + ' problem(s)' : 'all good'); process.exit(bad ? 1 : 0);
