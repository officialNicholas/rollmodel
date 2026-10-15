// Glicko-2 ratings (Glickman, "Example of the Glicko-2 system", 2013). One rating per mode.
// A match is one rating period. In modes with more than two sides every pair of players on different sides counts as a
// game: 1 for the better finish, 0.5 for a tie, 0 for the worse one.
const SCALE = 173.7178, TAU = 0.5, EPS = 1e-6;
export const DEFAULT_RATING = Object.freeze({ r: 1500, rd: 350, vol: 0.06, games: 0 });
const RD_MIN = 30, RD_MAX = 350;

const g = phi => 1 / Math.sqrt(1 + 3 * phi * phi / (Math.PI * Math.PI));
const E = (mu, muj, phij) => 1 / (1 + Math.exp(-g(phij) * (mu - muj)));

// player: { r, rd, vol }, results: [{ r, rd, s }] -> new { r, rd, vol }
export function glicko2(player, results, tau = TAU) {
  const mu = (player.r - 1500) / SCALE, phi = player.rd / SCALE, sigma = player.vol;
  if (!results.length) { const p = Math.min(Math.sqrt(phi * phi + sigma * sigma), RD_MAX / SCALE); return { r: player.r, rd: p * SCALE, vol: sigma }; }
  let vInv = 0, dSum = 0;
  for (const o of results) {
    const muj = (o.r - 1500) / SCALE, phij = o.rd / SCALE, gj = g(phij), e = E(mu, muj, phij);
    vInv += gj * gj * e * (1 - e); dSum += gj * (o.s - e);
  }
  const v = 1 / vInv, delta = v * dSum;
  // new volatility (Illinois algorithm)
  const a = Math.log(sigma * sigma), d2 = delta * delta, p2 = phi * phi;
  const f = x => { const ex = Math.exp(x); return ex * (d2 - p2 - v - ex) / (2 * (p2 + v + ex) ** 2) - (x - a) / (tau * tau); };
  let A = a, B;
  if (d2 > p2 + v) B = Math.log(d2 - p2 - v);
  else { let k = 1; while (f(a - k * tau) < 0) k++; B = a - k * tau; }
  let fA = f(A), fB = f(B), guard = 0;
  while (Math.abs(B - A) > EPS && guard++ < 100) {
    const C = A + (A - B) * fA / (fB - fA), fC = f(C);
    if (fC * fB <= 0) { A = B; fA = fB; } else fA /= 2;
    B = C; fB = fC;
  }
  const sigma2 = Math.exp(A / 2), phiStar = Math.sqrt(p2 + sigma2 * sigma2);
  const phi2 = 1 / Math.sqrt(1 / (phiStar * phiStar) + 1 / v), mu2 = mu + phi2 * phi2 * dSum;
  return { r: mu2 * SCALE + 1500, rd: Math.min(RD_MAX, Math.max(RD_MIN, phi2 * SCALE)), vol: sigma2 };
}

// players: [{ id, rating: {r, rd, vol}, side, place }] (place 1 is best; equal places tie).
// Returns Map id -> new rating. Leavers should be given the worst place before calling this.
export function rateMatch(players) {
  const out = new Map();
  for (const p of players) {
    const res = [];
    for (const o of players) {
      if (o === p || o.side === p.side) continue;
      res.push({ r: o.rating.r, rd: o.rating.rd, s: p.place < o.place ? 1 : p.place === o.place ? 0.5 : 0 });
    }
    const n = glicko2(p.rating, res);
    out.set(p.id, { r: n.r, rd: n.rd, vol: n.vol, games: (p.rating.games || 0) + 1 });
  }
  return out;
}
