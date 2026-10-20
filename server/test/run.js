#!/usr/bin/env node
// `npm test`: runs every test file one after another (several measure timing, so they never share the machine with
// each other), then prints the key numbers they recorded. `npm run test:quick` runs a smaller load test.
import { spawn } from 'node:child_process';
import { readFileSync, existsSync, rmSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url)), root = path.resolve(here, '..');
const quick = process.argv.includes('--quick');
const files = ['unit', 'movement', 'matchmaking', 'consensus', 'lifecycle', 'sync', 'lagcomp', 'cheats', 'session', 'rooms', 'party', 'items', 'robustness', 'load'].map(f => path.join('test', f + '.test.js'));
const dir = mkdtempSync(path.join(tmpdir(), 'rmtest-')), metricsFile = path.join(dir, 'metrics.jsonl');
const env = Object.assign({}, process.env, { RM_METRICS_FILE: metricsFile }, quick ? { RM_LOAD_ROOMS: process.env.RM_LOAD_ROOMS || '20', RM_LOAD_SECONDS: process.env.RM_LOAD_SECONDS || '5' } : {});
const t0 = Date.now();
const child = spawn(process.execPath, ['--test', '--test-concurrency=1', '--test-reporter=spec', ...files], { cwd: root, env, stdio: 'inherit' });

const SECTIONS = [
  ['sync', 'Lag and sync (simulated networks)'], ['lagcomp', 'Lag-compensated pounds (150 ms round trip)'], ['load', 'Load'],
  ['move', 'Movement referee (offline)'], ['cheat', 'Cheats'], ['lifecycle', 'Matchmaking'], ['session', 'Sessions'],
];
function summary() {
  if (!existsSync(metricsFile)) return;
  const rows = readFileSync(metricsFile, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l));
  const by = new Map(); for (const r of rows) by.set(r.key, r); // the last value of a key wins
  const line = '-'.repeat(100);
  console.log('\n' + line + '\nKEY NUMBERS' + (quick ? ' (quick run: smaller load test)' : '') + '\n' + line);
  for (const [prefix, title] of SECTIONS) {
    const sec = [...by.values()].filter(r => r.key.split('.')[0] === prefix); if (!sec.length) continue;
    console.log('\n' + title);
    for (const r of sec) console.log('  ' + (String(r.value) + ' ' + r.unit).padEnd(14) + r.note);
  }
  console.log('\n' + line + '\nall tests: ' + ((Date.now() - t0) / 1000).toFixed(0) + ' s\n' + line);
}
child.on('exit', code => { try { summary(); } finally { rmSync(dir, { recursive: true, force: true }); } process.exit(code === null ? 1 : code); });
