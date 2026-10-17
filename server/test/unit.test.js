// Unit tests: stage queries, layout canonical form and hash, the binary codec, ratings, names, coverage, storage,
// schedules, matchmaking windows, and remote-player sampling.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, existsSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { canonicalLayout, layoutHash, hashString, layoutFromStage, codec, FLAGS, RemoteTrack, ClockSync, RMNet, PROTOCOL_VERSION as SDK_PROTO } from '../client/rmnet.js';
import { Level, inR, rampH } from '../src/geometry.js';
import { validateLayout, fromCanonical } from '../src/layout.js';
import { glicko2, rateMatch } from '../src/rating.js';
import { sanitizeName, isProfane, sanitizeLook } from '../src/names.js';
import { Coverage } from '../src/coverage.js';
import { JsonFileStore, MemoryStore } from '../src/store.js';
import { TokenBucket } from '../src/ratelimit.js';
import { weatherSchedule, rainMulAt, zoneSchedule, zoneSizeAt } from '../src/schedule.js';
import { Matchmaker, windowFor, arrangeSides } from '../src/lobby.js';
import { CODE_ALPHABET, roomCode } from '../src/util.js';
import { G, KO_R } from '../src/constants.js';
import { genLayout, flatLayout } from './helpers/layouts.js';

test('stage queries mirror the game', () => {
  const L = new Level({ arena: 20, boxes: [[0, 2, 0, 2, 0, 1], [5, 7, 5, 7, 0, 1, 'c'], [-6, -2, -6, -2, 1, 1.3]], ramps: [[2, 6, 0, 2, 'x', 1, 0]], holes: [[-10, -8, 8, 10], [10, 14, 10, 14, 'c']], pots: [[0, 0, 5]], powers: [], spawns: [[0, -10, 0], [0, 10, 3.14]] });
  // round pieces are circles inscribed in their square
  assert.equal(inR(6, 6, L.boxes[1]), true); assert.equal(inR(5.1, 5.1, L.boxes[1]), false); assert.equal(inR(5.1, 5.1, [5, 7, 5, 7, 0, 1]), true);
  assert.equal(rampH(L.ramps[0], 2, 1), 1); assert.equal(rampH(L.ramps[0], 4, 1), 0.5); assert.equal(rampH(L.ramps[0], 9, 1), 0);
  assert.equal(L.floorAt(25, 0), -Infinity, 'outside the arena'); assert.equal(L.floorAt(-9, 9), -Infinity, 'in a square hole');
  assert.equal(L.floorAt(12, 12), -Infinity, 'in a round hole'); assert.equal(L.floorAt(10.2, 10.2), 0, 'in the corner of a round hole: floor');
  assert.equal(L.surfaceUnder(1, 1, 5), 1, 'box top'); assert.equal(L.surfaceUnder(1, 1, 0.5), 0, 'below the top: the floor');
  assert.equal(L.surfaceUnder(3, 1, 5), 0.75, 'on the ramp');
  assert.equal(L.surfaceUnder(-4, -4, 5), 1.3, 'floating pad top'); assert.equal(L.surfaceUnder(-4, -4, 0.9), 0, 'under the pad');
  assert.equal(L.blockedAt(-0.2, 1, 0), true, 'within the body margin of a box'); assert.equal(L.blockedAt(-0.4, 1, 0), false);
  assert.equal(L.blockedAt(1, 1, 0.8), false, 'standing on it (within a step of the top)');
  assert.equal(L.blockedAt(-4, -4, 0), false, 'under a floating pad'); assert.equal(L.blockedAt(-4, -4, 0.5), true, 'head in the pad');
  assert.equal(L.insideSolid(1, 1, 0), true); assert.equal(L.insideSolid(-0.2, 1, 0), false, 'the strict test ignores the margin');
  assert.equal(L.insideSolid(1, 1, 1), false, 'on top is fine');
  assert.equal(L.spawns[0].y, 0);
});

test('layout canonical form, hash and validation', () => {
  const L = genLayout(12345, 26.4);
  const c = canonicalLayout(L);
  assert.ok(c.startsWith('RM1[2640,'), 'numbers become integer hundredths');
  assert.equal(layoutHash(L), hashString(c)); assert.match(layoutHash(L), /^[0-9a-f]{16}$/);
  assert.equal(layoutHash(L), layoutHash(JSON.parse(JSON.stringify(L))), 'stable through JSON');
  assert.equal(layoutHash(genLayout(12345, 26.4)), layoutHash(L), 'same seed, same stage');
  assert.notEqual(layoutHash(genLayout(12346, 26.4)), layoutHash(L), 'another seed, another stage');
  // tiny float noise does not change it; a real change does
  const noisy = JSON.parse(JSON.stringify(L)); noisy.boxes[0][0] += 1e-9; noisy.spawns[0][2] += 1e-7;
  assert.equal(layoutHash(noisy), layoutHash(L));
  const moved = JSON.parse(JSON.stringify(L)); moved.boxes[0][0] += 0.1; assert.notEqual(layoutHash(moved), layoutHash(L));
  // -0 and 0 agree, extra fields (a box's kind) do not count, shapes only when round
  const z = { arena: 20, boxes: [[-0, 1, 0, 1, 0, 1, 0, 'rpad']], ramps: [], holes: [[1, 2, 1, 2, 0]], pots: [[0, 0, 0]], powers: [[1, 0, 1, undefined]], spawns: [[0, -0.001, 0]] };
  assert.equal(canonicalLayout(z), 'RM1[2000,[[0,100,0,100,0,100]],[],[[100,200,100,200]],[[0,0,0]],[[100,0,100]],[[0,0,0]],[]]');
  // known values, so a copy of the hash in the game can be checked against this one
  assert.equal(layoutHash(z), hashString(canonicalLayout(z))); assert.equal(layoutHash(z), 'ab6e1fc1d8b436cf');
  assert.equal(hashString(''), 'e3b1a47cab3e7c0b');
  const ex = { arena: 26.4, boxes: [[-2, 2, -1, 1, 0, 1.5], [5, 7, 5, 7, 0, 2, 'c']], ramps: [[-6, -4, 0, 3, 'z', 0, 1.5]], holes: [[8, 10, -10, -8], [-12, -9, 6, 9, 'c']], pots: [[0, 1.5, 0]], powers: [[4, 0, -4, 'roller'], [-4, 0, 4]], spawns: [[0, -20, 0], [0, 20, Math.PI]], puddles: [[10, 0, 10]] };
  assert.equal(canonicalLayout(ex), 'RM1[2640,[[-200,200,-100,100,0,150],[500,700,500,700,0,200,"c"]],[[-600,-400,0,300,"z",0,150]],[[800,1000,-1000,-800],[-1200,-900,600,900,"c"]],[[0,150,0]],[[400,0,-400,"roller"],[-400,0,400]],[[0,-2000,0],[0,2000,314]],[[1000,0,1000]]]');
  assert.equal(layoutHash(ex), '746f9aef3f617241');
  // puddles (the boiling-water spots) are optional; when sent they are part of the stage
  const wp = layoutFromStage({ arena: 20, boxes: [], ramps: [], holes: [], pots: [[0, 0, 0]], powers: [], spawns: [[0, -5, 0], [0, 5, 3.14]], puddles: [[3, 0.05, 3, 'extra']] });
  assert.deepEqual(wp.puddles, [[3, 0.05, 3]]); assert.ok(canonicalLayout(wp).endsWith(',[[300,5,300]]]'));
  assert.notEqual(layoutHash(wp), layoutHash({ ...wp, puddles: [] })); assert.equal(layoutHash({ ...wp, puddles: [] }), layoutHash({ ...wp, puddles: undefined }));
  const vp = validateLayout(wp, { arena: 20, players: 2 }); assert.ok(vp.ok, vp.error); assert.deepEqual(vp.layout.puddles, [[3, 0.05, 3]]);
  assert.match(validateLayout({ ...wp, puddles: new Array(49).fill([0, 0, 0]) }, { arena: 20 }).error, /too many puddles/);
  assert.equal(hashString('RM1'), hashString('RM1')); assert.notEqual(hashString('RM1'), hashString('RM2'));
  // the server's validation
  const v = validateLayout(L, { arena: 26.4, players: 2 }); assert.ok(v.ok, v.error); assert.equal(v.hash, layoutHash(L));
  assert.equal(canonicalLayout(fromCanonical(v.canonical)), v.canonical, 'round trip');
  const bad = [
    [{ ...L, arena: 33 }, 'arena does not match'], [{ ...L, boxes: [[0, 1, 0, 1, 0, NaN]] }, 'height'], [{ ...L, boxes: [[0, 1, 0, 1, 0, Infinity]] }, 'height'],
    [{ ...L, ramps: [[0, 1, 0, 1, 'y', 0, 1]] }, 'axis'], [{ ...L, boxes: [[2, 1, 0, 1, 0, 1]] }, 'no size'], [{ ...L, spawns: [] }, 'spawns'],
    [{ ...L, boxes: new Array(500).fill([0, 1, 0, 1, 0, 1]) }, 'too many'], [{ ...L, pots: 'x' }, 'array'], [null, 'object'], [{ ...L, powers: [[0, 0, 0, '<script>']] }, 'kind'],
    [{ ...L, boxes: [[0, 1, 0, 1e9, 0, 1]] }, 'range'],
  ];
  for (const [lay, why] of bad) { const r = validateLayout(lay, { arena: 26.4, players: 2 }); assert.equal(r.ok, false, why); assert.match(r.error, new RegExp(why.split(' ')[0])); }
  // the game's own stage arrays convert to the layout format
  const st = layoutFromStage({ arena: 26.4, boxes: [[0, 1, 0, 1, 0, 1, 'c', 'rpad'], [2, 3, 2, 3, 0, 1]], ramps: [[0, 1, 0, 1, 'x', 0, 1]], holes: [[0, 1, 0, 1], [4, 6, 4, 6, 0, 0, 'c']], pots: [[1, 0, 1]], powers: [[0, 0, 0, 'roller'], [1, 0, 1, undefined]], spawns: [{ x: 0, z: -20, yaw: 0 }, { x: 0, z: 20, yaw: 3.14 }] });
  assert.deepEqual(st.boxes, [[0, 1, 0, 1, 0, 1, 'c'], [2, 3, 2, 3, 0, 1]]); assert.deepEqual(st.holes, [[0, 1, 0, 1], [4, 6, 4, 6, 'c']]);
  assert.deepEqual(st.powers, [[0, 0, 0, 'roller'], [1, 0, 1]]); assert.deepEqual(st.spawns, [[0, -20, 0], [0, 20, 3.14]]);
});

test('binary codec round trips and refuses garbage', () => {
  const s = { x: 12.345, y: 0.5, z: -20.25, yaw: -1.2, spd: 6.5, vy: -3.25, flags: FLAGS.AIR | FLAGS.CHARGE, paint: 0.5, aim: 0.75 };
  const d = codec.decodeState(codec.encodeState(s, 65535, 123456.789, 7));
  assert.equal(d.seq, 65535); assert.equal(d.corrAck, 7); assert.equal(d.t, 123456.789);
  assert.ok(Math.abs(d.x - 12.345) < 1e-5); assert.ok(Math.abs(Math.cos(d.yaw) - Math.cos(-1.2)) < 1e-4 && Math.abs(Math.sin(d.yaw) - Math.sin(-1.2)) < 1e-4);
  assert.equal(d.spd, 6.5); assert.equal(d.vy, -3.25); assert.equal(d.flags, FLAGS.AIR | FLAGS.CHARGE); assert.ok(Math.abs(d.paint - 0.5) < 0.003);
  assert.equal(codec.encodeState(s, 1, 1, 0).byteLength, codec.STATE_BYTES);
  const nan = new Uint8Array(codec.encodeState(s, 1, 1, 0)); new DataView(nan.buffer).setFloat32(12, NaN, true); assert.equal(codec.decodeState(nan), null);
  const inf = new Uint8Array(codec.encodeState(s, 1, 1, 0)); new DataView(inf.buffer).setFloat64(4, Infinity, true); assert.equal(codec.decodeState(inf), null);
  assert.equal(codec.decodeState(new Uint8Array(10)), null); assert.equal(codec.decodeState(new Uint8Array(34)), null, 'wrong type byte');
  const snap = codec.encodeSnapshot(7, 5000, 42, [{ slot: 0, age: 12, x: 1.234, y: 0, z: -2, yaw: 3, spd: 5.5, vy: 0, flags: FLAGS.ROLL, paint: 1, aim: 0 }, { slot: 3, age: 70000, x: -300, y: 9, z: 400, yaw: 0, spd: 0, vy: 1, flags: 0, paint: 0, aim: 1 }]);
  assert.equal(snap.byteLength, codec.SNAP_HEAD + 2 * codec.SNAP_ENTRY);
  const ds = codec.decodeSnapshot(snap);
  assert.equal(ds.seq, 7); assert.equal(ds.ack, 42); assert.equal(ds.players[0].x, 1.23); assert.equal(ds.players[0].t, 5000 - 12); assert.equal(ds.players[1].age, 65535, 'age saturates');
  assert.equal(ds.players[1].x, -300); assert.equal(ds.players[1].z, 327.67, 'positions saturate at the int16 range');
  codec.setSnapshotAck(snap, 9); assert.equal(codec.decodeSnapshot(snap).ack, 9);
  assert.equal(codec.decodeSnapshot(snap.slice(0, 20)), null);
  assert.equal(codec.decodePong(codec.encodePong(1.5, 2.5)).s, 2.5);
  assert.equal(codec.decodePing(codec.encodePing(77)), 77); assert.equal(codec.decodePing(new Uint8Array(3)), null);
  assert.equal(SDK_PROTO, 1);
});

test('Glicko-2 matches the reference example and rates multiplayer finishes', () => {
  // Glickman's worked example
  const r = glicko2({ r: 1500, rd: 200, vol: 0.06 }, [{ r: 1400, rd: 30, s: 1 }, { r: 1550, rd: 100, s: 0 }, { r: 1700, rd: 300, s: 0 }]);
  assert.ok(Math.abs(r.r - 1464.06) < 0.05, 'rating ' + r.r); assert.ok(Math.abs(r.rd - 151.52) < 0.05, 'rd ' + r.rd); assert.ok(Math.abs(r.vol - 0.05999) < 0.0001, 'vol ' + r.vol);
  const base = { r: 1500, rd: 350, vol: 0.06, games: 0 };
  const duel = rateMatch([{ id: 'a', rating: base, side: 0, place: 1 }, { id: 'b', rating: base, side: 1, place: 2 }]);
  assert.ok(duel.get('a').r > 1500 && duel.get('b').r < 1500 && Math.abs(duel.get('a').r - 1500 - (1500 - duel.get('b').r)) < 1e-6);
  assert.ok(duel.get('a').rd < 350); assert.equal(duel.get('a').games, 1);
  const tie = rateMatch([{ id: 'a', rating: base, side: 0, place: 1 }, { id: 'b', rating: base, side: 1, place: 1 }]);
  assert.ok(Math.abs(tie.get('a').r - 1500) < 1e-6);
  // 2v2: teammates are not rated against each other
  const duo = rateMatch([{ id: 'a', rating: base, side: 0, place: 1 }, { id: 'b', rating: base, side: 1, place: 2 }, { id: 'c', rating: base, side: 1, place: 2 }, { id: 'd', rating: base, side: 0, place: 1 }]);
  assert.equal(duo.get('a').r, duo.get('d').r); assert.ok(duo.get('a').r > 1500 && duo.get('b').r < 1500);
  // four-way: places order the gains
  const ffa = rateMatch(['a', 'b', 'c', 'd'].map((id, i) => ({ id, rating: base, side: i, place: i + 1 })));
  assert.ok(ffa.get('a').r > ffa.get('b').r && ffa.get('b').r > ffa.get('c').r && ffa.get('c').r > ffa.get('d').r);
});

test('display names are cleaned and filtered', () => {
  assert.equal(sanitizeName('  Blobby   McBlob ').name, 'Blobby McBlob');
  assert.equal(sanitizeName('A'.repeat(40)).name.length, 16);
  assert.equal(sanitizeName('x' + String.fromCharCode(0x202e) + 'y' + String.fromCharCode(0x200b) + 'z' + String.fromCharCode(7)).name, 'xyz', 'direction overrides, zero-width and control characters go');
  assert.equal(sanitizeName('<script>alert(1)</script>').name, 'scriptalert1scri', 'symbols go, then it is cut to 16');
  assert.equal(sanitizeName('Zoë 2').name, 'Zoë 2', 'accents and numbers stay');
  for (const bad of ['fuck', 'Sh1t head', 'n1gg3r', 'big d.i.c.k', 'cock', 'FaGgOt']) { const r = sanitizeName(bad); assert.equal(r.reason, 'profanity', bad); assert.match(r.name, /^Player\d{4}$/); }
  for (const ok of ['Dickens', 'Peacock', 'Grape', 'Scunthorpe', 'Assassin', 'Cockatoo', 'Therapist', 'Swanky', 'Nazim', 'Shiitake']) assert.equal(isProfane(ok), false, ok);
  assert.match(sanitizeName('').name, /^Player\d{4}$/); assert.match(sanitizeName(42).name, /^Player\d{4}$/); assert.match(sanitizeName('   ').name, /^Player\d{4}$/);
  assert.deepEqual(sanitizeLook({ hat: 'cap', eyes: 3 }), { hat: 'cap', eyes: 3 }); assert.equal(sanitizeLook({ big: 'x'.repeat(1000) }), null); assert.equal(sanitizeLook(5), null);
});

test('coverage counts every walkable surface and paints discs', () => {
  const L = new Level(flatLayout(26.4)), cov = new Coverage(L, [0, 1]);
  assert.ok(cov.total > 40000, 'about 0.25 m cells');
  assert.equal(cov.colors()[0], 0);
  const n = cov.stamp(0, 0, -15, G.SLAM_R * 0.98, 0); // a pound
  assert.ok(Math.abs(n * 0.0625 - Math.PI * (G.SLAM_R * 0.98) ** 2) < 1.5, 'area of the splat ' + n * 0.0625);
  assert.equal(cov.stamp(0, 0, -15, G.SLAM_R * 0.98, 0), 0, 'painting your own colour again changes nothing');
  const over = cov.stamp(0, 0, -15, 1, 1); assert.ok(over > 0); assert.equal(cov.colorAt(0, 0, -15), 1, 'the other colour takes it over');
  cov.stampPath(-10, 0, -20, 10, 0, -20, G.TW / 2, 1);
  assert.ok(Math.abs(cov.count[1] * 0.0625 - (over * 0.0625 + 20 * G.TW)) < 3, 'a 20 m trail is about 20 x 0.8 m');
  assert.equal(cov.stamp(10, 1.2, -10, 1, 0) > 0, true, 'box tops are paintable'); assert.equal(cov.colorAt(10, 1.2, -10), 0);
  assert.equal(cov.stamp(-12, 0, 0, 1, 0), 0, 'nothing to paint in a hole');
  const side = cov.bySide(); assert.ok(side[0] > 0 && side[1] > 0 && side[0] + side[1] <= 100);
  assert.equal(cov.stamp(0, 5, 0, 1, 0), 0, 'paint only lands near the surface it is on');
});

test('the JSON file store keeps players by a hash of their token', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'rmstore-')), file = path.join(dir, 'store.json');
  const s = new JsonFileStore(file, { delayMs: 10 }); await s.init();
  const { player, token } = await s.create({ name: 'Blob' });
  await s.update(player.id, { ratings: Object.assign({}, player.ratings, { duel: { r: 1600, rd: 200, vol: 0.06, games: 3 } }) });
  await s.flag(player.id, 'test', { a: 1 }); await s.recordMatch({ matchId: 'm1' }); await s.flush();
  const raw = (existsSync(file) ? readFileSync(file, 'utf8') : '') + readFileSync(file + '.log', 'utf8'); assert.ok(!raw.includes(token), 'the token itself is never written');
  const s2 = new JsonFileStore(file); await s2.init();
  const again = await s2.getByToken(token); assert.equal(again.id, player.id); assert.equal(again.ratings.duel.r, 1600); assert.equal(again.flags.length, 1);
  assert.equal(await s2.getByToken('nope-nope-nope-nope-nope'), null); assert.equal(await s2.getByToken(5), null);
  const m = new MemoryStore(); const c = await m.create({ name: 'x' }); const got = await m.get(c.player.id); got.name = 'changed'; assert.equal((await m.get(c.player.id)).name, 'x', 'callers get copies');
});

test('token buckets, schedules, matchmaking windows, room codes', () => {
  const b = new TokenBucket(10, 5); let ok = 0; for (let i = 0; i < 20; i++) if (b.take(1, 1000)) ok++; assert.equal(ok, 5); assert.equal(b.take(1, 1100), true, 'refills over time');
  const w = weatherSchedule(42, 90); assert.deepEqual(w, weatherSchedule(42, 90), 'deterministic from the seed'); assert.ok(w.length > 0 && w[0].at >= 22);
  const rain = w.find(p => p.ph === 'rain'); if (rain) { assert.equal(rainMulAt(w, rain.at + 1), 2); assert.equal(rainMulAt(w, rain.at + rain.dur + 1), 2, 'tail'); }
  assert.equal(rainMulAt(w, 1), 1);
  const z = zoneSchedule(); assert.equal(zoneSizeAt(z, 59), Infinity); assert.equal(zoneSizeAt(z, 61), 26.4); assert.equal(zoneSizeAt(z, 121), 20);
  assert.equal(windowFor(0), 100); assert.equal(windowFor(10), 300); assert.equal(windowFor(30), 600); assert.equal(windowFor(60), Infinity);
  const mk = (r, at) => ({ player: { ratings: { duel: { r, rd: 50 }, duo: { r, rd: 50 } } } });
  const mm = new Matchmaker(); const a = mk(1500), c = mk(1550), far = mk(2400);
  mm.add(a, 'duel', 0); mm.add(far, 'duel', 0); assert.equal(mm.form(1000).length, 0, 'too far apart at first');
  mm.add(c, 'duel', 0); const g = mm.form(1000); assert.equal(g.length, 1); assert.deepEqual(g[0].tickets.map(t => t.sess).sort((x, y) => x === a ? -1 : 1), [a, c]);
  assert.equal(mm.form(70000).length, 0, 'one left'); const d = mk(1500); mm.add(d, 'duel', 70000); assert.equal(mm.form(120000).length, 1, 'after a long wait anyone will do');
  const four = [1400, 1700, 1500, 1600].map(r => ({ r, at: 0 })); const s = arrangeSides('duo', four); // sides [0,1,1,0]
  assert.equal(s[0].r + s[3].r, s[1].r + s[2].r, 'balanced teams');
  for (let i = 0; i < 200; i++) { const code = roomCode(); assert.match(code, /^[A-Z0-9]{5}$/); for (const ch of code) assert.ok(CODE_ALPHABET.includes(ch)); }
  for (const amb of ['0', 'O', '1', 'I', 'L']) assert.ok(!CODE_ALPHABET.includes(amb), 'no look-alike ' + amb);
});

test('remote sampling interpolates, extrapolates briefly, then holds', () => {
  const tr = new RemoteTrack();
  for (let i = 0; i <= 10; i++) tr.push({ slot: 1, t: 1000 + i * 33, x: i * 0.2, y: 0, z: 0, yaw: Math.PI / 2, spd: 6, vy: 0, flags: 0, paint: 1, aim: 0 });
  assert.equal(tr.push({ t: 1000 }), false, 'old states are ignored');
  const mid = tr.sample(1000 + 5 * 33 + 16.5); assert.ok(Math.abs(mid.x - 1.1) < 1e-9); assert.equal(mid.extrapolated, false);
  const ex = tr.sample(1330 + 100); assert.ok(ex.extrapolated); assert.ok(Math.abs(ex.x - (2 + 0.2 / 33 * 100)) < 1e-6, 'carries on at the last speed');
  const held = tr.sample(1330 + 1000, 250); assert.ok(held.held); assert.ok(Math.abs(held.x - (2 + 0.2 / 33 * 250)) < 1e-6, 'stops after 250 ms');
  assert.equal(tr.sample(0).x, 0, 'before the first state: the first state');
  tr.push({ slot: 1, t: 1400, x: 30, y: 0, z: 0, yaw: 0, spd: 0, vy: 0, flags: 0, paint: 1, aim: 0 });
  assert.equal(tr.sample(1365).x, 2, 'never slides across a teleport (a respawn)');
  // a player who sends nothing new (dropped, knocked out) keeps its last state, but the server's flags still get through
  assert.equal(tr.push({ slot: 1, t: 1400, x: 30, y: 0, z: 0, yaw: 0, spd: 0, vy: 0, flags: FLAGS.AWAY | FLAGS.KO, paint: 0.5, aim: 0 }), false, 'not a new position');
  const away = tr.sample(1500); assert.equal(away.flags, FLAGS.AWAY | FLAGS.KO); assert.equal(away.x, 30); assert.equal(away.paint, 0.5);
  // yaw takes the short way round
  const t2 = new RemoteTrack(); t2.push({ t: 0, x: 0, y: 0, z: 0, yaw: 3.1, spd: 0, vy: 0, flags: 0 }); t2.push({ t: 10, x: 0, y: 0, z: 0, yaw: -3.1, spd: 0, vy: 0, flags: 0 });
  assert.ok(Math.abs(Math.abs(t2.sample(5).yaw) - Math.PI) < 0.01);
  // clock: the lowest round trip wins
  const c = new ClockSync(); c.add(0, 1100, 100); c.add(200, 1260, 220); assert.equal(c.offset, 1260 + 10 - 220);
  assert.equal(KO_R, 3.34);
});

test('drawing a remote player: a leap back after a stall glides instead of popping; real moves and teleports pass through', () => {
  let now = 0; const net = new RMNet({ url: 'ws://x', now: () => now, autoReconnect: false });
  const at = (x, flags = 0) => { const o = { x, y: 0, z: 0, flags }; net._smoothed(1, o); return o.x; };
  // steady running at 5.4 m/s, 60 frames a second: drawn exactly where sampled
  let x = 0; for (let i = 0; i < 30; i++) { now += 16.7; x += 5.4 * 0.0167; assert.ok(Math.abs(at(x) - x) < 1e-9); }
  // a stall's late states pull the sample 1.2 m back in one frame: the drawn position barely moves, then eases back
  now += 16.7; const before = x; x -= 1.2; const d0 = at(x);
  assert.ok(Math.abs(d0 - before) < 0.35, 'no pop (' + (d0 - before).toFixed(2) + ' m)');
  let last = d0; for (let i = 0; i < 30; i++) { now += 16.7; const d = at(x); assert.ok(Math.abs(d - last) < 0.35, 'each frame a small step'); last = d; }
  assert.ok(Math.abs(last - x) < 0.02, 'back on the sample within half a second (' + (last - x).toFixed(3) + ')');
  // a respawn, more than 5 m away: straight there
  now += 16.7; x += 9; assert.equal(at(x), x);
  // knocked out: never smoothed
  now += 16.7; x -= 2; assert.equal(at(x, FLAGS.KO), x);
});

test('the file store: a change is a short line in the journal, the snapshot is rebuilt now and then, and both load back', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'rmjournal-')), file = path.join(dir, 'store.json');
  const s = new JsonFileStore(file, { delayMs: 5, chunk: 7, compactBytes: 1e9 }); await s.init();
  const made = []; for (let i = 0; i < 60; i++) made.push(await s.create({ name: 'P' + i }));
  await s.flush();
  const log1 = statSync(file + '.log').size;
  // one change: one line more, not everyone again
  await s.update(made[3].player.id, { name: 'Renamed' }); await s.flush();
  const grew = statSync(file + '.log').size - log1; assert.ok(grew > 0 && grew < 1000, 'one player\'s line (' + grew + ' bytes)');
  // enough changes and the journal is folded into a fresh snapshot (written 7 players at a time)
  s.compactBytes = 20000;
  for (let k = 0; k < 4; k++) for (const m of made) await s.update(m.player.id, { stats: { matches: k + 1, wins: 0, kos: 0 } });
  await s.flush(); while (s._compacting) await s._compacting;
  assert.ok(existsSync(file), 'a snapshot was written'); assert.ok((existsSync(file + '.log') ? statSync(file + '.log').size : 0) < 20000, 'and the journal started over');
  await s.recordMatch({ matchId: 'mA' }); await s.update(made[5].player.id, { name: 'Last' }); await s.flush();
  const s2 = new JsonFileStore(file); await s2.init();
  assert.equal(s2.players.size, 60); assert.equal((await s2.get(made[3].player.id)).name, 'Renamed'); assert.equal((await s2.get(made[5].player.id)).name, 'Last');
  assert.equal((await s2.get(made[9].player.id)).stats.matches, 4); assert.equal(s2.matches.filter(m => m.matchId === 'mA').length, 1);
  assert.equal((await s2.getByToken(made[0].token)).id, made[0].player.id);
  // shutting down folds everything into the snapshot
  await s.close(); const snap = JSON.parse(readFileSync(file, 'utf8')); assert.equal(snap.players.length, 60);
  assert.ok(snap.players.some(p => p.name === 'Last'));
});

test('the SDK starts its clock again on another machine (or a restarted one): each counts time from its own start', () => {
  let now = 1000; const net = new RMNet({ url: 'ws://x', now: () => now, autoReconnect: false });
  try {
  for (let i = 0; i < 10; i++) { now += 50; net._clock.add(now - 20, 500000 + now - 10, now); } // (machine m1: its clock 500 s ahead of ours)
  net._onJson({ t: 'welcome', id: 'p', token: 't', name: 'n', shard: 'm1', serverTime: 500000 + now });
  assert.ok(Math.abs(net.serverNow() - (500000 + now)) < 30);
  net._onJson({ t: 'welcome', id: 'p', token: 't', name: 'n', shard: 'm2', serverTime: 20000 + now }); // moved to m2, which started later
  assert.ok(Math.abs(net.serverNow() - (20000 + now)) < 5, "on m2's clock at once (" + (net.serverNow() - (20000 + now)) + ')');
  assert.equal(net._clock.n, 0, 'old samples gone');
  for (let i = 0; i < 6; i++) { now += 50; net._clock.add(now - 20, 20000 + now - 10, now); } // (pings on m2)
  net._onJson({ t: 'welcome', id: 'p', token: 't', name: 'n', shard: 'm2', serverTime: 90000 + now }); // the same machine, restarted
  assert.ok(Math.abs(net.serverNow() - (90000 + now)) < 5);
  } finally { net.close(); }
});
