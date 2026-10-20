import { nowMs } from './util.js';

// token bucket: `rate` tokens per second, holding at most `burst`
export class TokenBucket {
  constructor(rate, burst) { this.rate = rate; this.burst = burst; this.tokens = burst; this.t = nowMs(); }
  take(n = 1, t = nowMs()) {
    this.tokens = Math.min(this.burst, this.tokens + Math.max(0, t - this.t) / 1000 * this.rate); this.t = t;
    if (this.tokens >= n) { this.tokens -= n; return true; }
    return false;
  }
}

// per-connection limits; a connection that keeps pushing past them is a flood and gets kicked
export function connectionLimits() {
  return {
    state: new TokenBucket(40, 60), // binary states (the SDK sends 30 a second)
    ping: new TokenBucket(12, 24),
    json: new TokenBucket(20, 40), // control messages
    act: new TokenBucket(15, 25), // in-match actions
    join: new TokenBucket(0.1, 6), // wrong room codes: 6, then one more every 10 s
    react: new TokenBucket(1, 4), // party reactions: 4 in a row, then one a second
    poke: new TokenBucket(0.5, 12), // invites and pokes to other players: 12, then one every 2 s
    dropped: 0, droppedSince: nowMs(),
  };
}
// count a dropped message; true when the connection should be kicked for flooding
export function noteDrop(lim, t = nowMs()) {
  if (t - lim.droppedSince > 5000) { lim.dropped = 0; lim.droppedSince = t; }
  lim.dropped++;
  return lim.dropped > 150;
}
