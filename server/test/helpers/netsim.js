// A network simulator for tests. It wraps a real WebSocket (Node 22's global one) and delays every message in each
// direction by a configurable latency with jitter, occasional delay spikes, and an optional bandwidth cap.
// WebSocket runs over TCP, so nothing is ever lost or reordered: a lost packet shows up as a spike that holds back
// that message and everything behind it until it is retransmitted (head-of-line blocking). That is what this models.
//
// link: { latency (one-way ms), jitter (± ms, uniform), spikeEvery (mean ms between spikes, 0 for none),
//         spikeMs ([min, max] extra ms), bandwidth (bytes per second, 0 for no cap) }
import { performance } from 'node:perf_hooks';
import { rng } from '../../src/util.js';

export class Link {
  constructor(cfg = {}, seed = 1) {
    this.c = Object.assign({ latency: 0, jitter: 0, spikeEvery: 0, spikeMs: [150, 300], bandwidth: 0 }, cfg);
    this.R = rng(seed); this.lastAt = 0; this.freeAt = 0; this.nextSpike = this._nextSpike(performance.now());
    this.sent = 0; this.bytes = 0; this.spikes = 0; this.delays = [];
  }
  _nextSpike(now) { const e = this.c.spikeEvery; return e ? now - Math.log(1 - this.R()) * e : Infinity; }
  // when a message of `size` bytes handed to the link now comes out the other end
  arrival(size, now = performance.now()) {
    const c = this.c;
    const start = Math.max(now, this.freeAt);
    this.freeAt = start + (c.bandwidth ? size / c.bandwidth * 1000 : 0);
    let at = this.freeAt + c.latency + (this.R() * 2 - 1) * c.jitter;
    if (now >= this.nextSpike) { at += c.spikeMs[0] + this.R() * (c.spikeMs[1] - c.spikeMs[0]); this.spikes++; this.nextSpike = this._nextSpike(now); }
    at = Math.max(at, this.lastAt, now); // in order, never early
    this.lastAt = at; this.sent++; this.bytes += size;
    if (this.delays.length < 50000) this.delays.push(at - now);
    return at;
  }
  // in order, like TCP: one queue per direction (a timer per message could swap two sent within a millisecond, since
  // timers round their delays)
  deliver(size, fn) {
    const now = performance.now(), at = this.arrival(size, now);
    (this.q || (this.q = [])).push({ at, fn }); if (this.q.length === 1) this._pump();
  }
  _pump() {
    const q = this.q; if (!q.length) return;
    const wait = q[0].at - performance.now();
    if (wait > 0) { setTimeout(() => this._pump(), wait); return; }
    q.shift().fn(); // (one message a task, as a browser hands them over)
    if (q.length) setImmediate(() => this._pump());
  }
}

let seedSeq = 1;
// returns a WebSocket class to hand to RMNet({ WebSocket }). up: client to server, down: server to client.
export function netSim({ up = {}, down = {}, RealWebSocket = globalThis.WebSocket } = {}) {
  return class NetSimWebSocket {
    constructor(url) {
      this.url = url; this.readyState = 0; this.binaryType = 'arraybuffer';
      this.onopen = null; this.onmessage = null; this.onclose = null; this.onerror = null;
      this.up = new Link(up, seedSeq++ * 7919); this.down = new Link(down, seedSeq++ * 104729);
      NetSimWebSocket.last = this;
      const ws = this._ws = new RealWebSocket(url); ws.binaryType = 'arraybuffer';
      ws.onopen = () => this.down.deliver(0, () => { if (this.readyState === 0) { this.readyState = 1; this.onopen && this.onopen({ type: 'open' }); } });
      ws.onmessage = ev => { if (this.silent) return; const d = ev.data, n = typeof d === 'string' ? d.length : d.byteLength; this.down.deliver(n, () => { if (this.readyState === 1 || this.readyState === 2) this.onmessage && this.onmessage({ data: d }); }); };
      ws.onclose = ev => { const e = { code: ev.code, reason: ev.reason }; this.down.deliver(0, () => { this.readyState = 3; this.onclose && this.onclose(e); }); };
      ws.onerror = ev => { this.onerror && this.onerror(ev); };
    }
    get bufferedAmount() { return this._ws.bufferedAmount; }
    send(data) {
      if (this.readyState !== 1) throw new Error('not open');
      if (this.silent) return;
      const n = typeof data === 'string' ? data.length : data.byteLength;
      this.up.deliver(n, () => { if (this._ws.readyState === 1) this._ws.send(data); });
    }
    close(code, reason) { if (this.readyState >= 2) return; this.readyState = 2; this.up.deliver(0, () => { try { this._ws.close(code, reason); } catch (e) { /* closing */ } }); }
    // test helper: drop the connection at once, as if the phone lost its signal
    kill() { try { this._ws.close(); } catch (e) { /* gone */ } }
    // test helper: the link goes dead both ways without closing (a tunnel, Wi-Fi handing over to 4G)
    blackhole() { this.silent = true; }
  };
}

// the usual profiles
export const PROFILES = {
  lan: { up: { latency: 1 }, down: { latency: 1 } },
  rtt60: { up: { latency: 30, jitter: 5 }, down: { latency: 30, jitter: 5 } },
  rtt120: { up: { latency: 60, jitter: 15 }, down: { latency: 60, jitter: 15 } }, // 120 ms round trip, +/- 30 ms
  rtt150: { up: { latency: 75, jitter: 10 }, down: { latency: 75, jitter: 10 } },
  mobile: { up: { latency: 60, jitter: 20, spikeEvery: 4000, spikeMs: [120, 250] }, down: { latency: 60, jitter: 20, spikeEvery: 4000, spikeMs: [120, 250] } },
};
