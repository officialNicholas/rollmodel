// A stand-in for Fly's proxy in front of several machines, for the tests: each new WebSocket connection goes to the
// machine with the fewest open connections (as Fly balances within a region), and a machine that answers with a
// fly-replay header ("instance=<id>") gets the request handed to that machine instead, as Fly does.
import http from 'node:http';

export async function flyProxy(machines, { first = false } = {}) { // machines: [{ id, port }]; first: always the first machine (unless replayed)
  const open = new Map(machines.map(m => [m.id, 0]));
  const stats = { replays: 0, routed: new Map() };
  const server = http.createServer((req, res) => { res.writeHead(404); res.end(); }), conns = new Set();
  server.on('connection', so => { conns.add(so); so.on('close', () => conns.delete(so)); });
  server.on('upgrade', (req, socket, head) => {
    const pick = () => first ? machines[0] : machines.reduce((a, b) => (open.get(b.id) < open.get(a.id) ? b : a));
    const go = (m, hops) => {
      open.set(m.id, open.get(m.id) + 1); // (counted from the moment it is sent there)
      let counted = true; const uncount = () => { if (counted) { counted = false; open.set(m.id, open.get(m.id) - 1); } };
      const up = http.request({ host: '127.0.0.1', port: m.port, path: req.url, method: req.method, headers: req.headers });
      up.on('upgrade', (res, us, uh) => {
        let h = 'HTTP/1.1 101 Switching Protocols\r\n'; for (let i = 0; i < res.rawHeaders.length; i += 2) h += res.rawHeaders[i] + ': ' + res.rawHeaders[i + 1] + '\r\n';
        socket.write(h + '\r\n'); if (uh && uh.length) socket.write(uh);
        stats.routed.set(m.id, (stats.routed.get(m.id) || 0) + 1);
        us.on('close', uncount); socket.on('close', uncount); us.on('error', () => socket.destroy()); socket.on('error', () => us.destroy());
        us.pipe(socket); socket.pipe(us);
      });
      up.on('response', res => {
        const replay = /instance=([^;\s]+)/.exec(res.headers['fly-replay'] || '');
        const to = replay && machines.find(x => x.id === replay[1]);
        res.resume(); uncount();
        if (to && hops < 2) { stats.replays++; return go(to, hops + 1); }
        socket.end('HTTP/1.1 ' + (replay ? 502 : res.statusCode) + ' x\r\nContent-Length: 0\r\n\r\n');
      });
      up.on('error', () => { uncount(); socket.destroy(); });
      if (head && head.length) up.write(head);
      up.end();
    };
    go(pick(), 0);
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  return { url: 'ws://127.0.0.1:' + port + '/ws', port, stats, close: () => new Promise(r => { server.close(() => r()); for (const so of conns) so.destroy(); }) };
}
