// Match events that follow the clock: the weather and the Showdown's closing canvas. Both are decided by the server
// from the match seed when the match starts and sent to every client in the start message, so everyone switches at
// exactly the same server time and the referee knows when the rain makes people faster.
import { rng } from './util.js';
import { G } from './constants.js';

const SUN_WARN = 4, SUN_TIME = 7, SUN_CHANCE = 0.45, DUSK_TIME = 5, RAIN_TIME = 6.5, RAIN_TAIL = 1.5;

// [{ ph, at, dur }] in seconds after the start. Mirrors the game's updateWeather (clear, then sometimes a heat wave
// that ends in rain, sometimes rain, often more clear).
export function weatherSchedule(seed, durS) {
  const R = rng((seed ^ 0x5eed1234) >>> 0), out = [];
  let t = 22 + R() * 8, suns = 0;
  const push = (ph, dur) => { out.push({ ph, at: +t.toFixed(3), dur: +dur.toFixed(3) }); t += dur; };
  while (t < durS) {
    const roll = R();
    if (!suns && durS - t > SUN_WARN + SUN_TIME + 6 && roll < SUN_CHANCE) { push('warn', SUN_WARN); push('sun', SUN_TIME); push('dusk', DUSK_TIME); push('rain', RAIN_TIME); push('clear', 16 + R() * 8); suns++; }
    else if (roll < SUN_CHANCE + 0.32) { push('rain', RAIN_TIME); push('clear', 16 + R() * 8); }
    else push('clear', 14 + R() * 8);
  }
  return out.filter(p => p.at < durS);
}
// the speed multiplier the referee allows at time tS (seconds after the start): the rain, plus a tail while it fades
export function rainMulAt(sched, tS) {
  for (const p of sched) if (p.ph === 'rain' && tS >= p.at - 0.25 && tS <= p.at + p.dur + RAIN_TAIL) return G.RAIN_MUL;
  return 1;
}

// Showdown: the safe square closes at 60 s and 120 s, with a warning 15 s before each
export function zoneSchedule() {
  const out = [];
  G.ZONE_AT.forEach((at, i) => { out.push({ at: at - G.ZONE_WARN, warn: true, size: G.ZONE_SZ[i] }); out.push({ at, warn: false, size: G.ZONE_SZ[i] }); });
  return out;
}
// the half size of the safe square at tS (Infinity before the first close)
export function zoneSizeAt(sched, tS) { let s = Infinity; for (const z of sched) if (!z.warn && tS >= z.at) s = z.size; return s; }
