// Structured logs: one JSON object per line ({ ts, level, msg, ...fields }) on stdout (errors on stderr).
const LEVELS = { debug: 10, info: 20, warn: 30, error: 40, silent: 100 };

export function createLogger({ level = 'info', base = {}, sink = null } = {}) {
  let min = LEVELS[level] ?? LEVELS.info;
  const write = (lv, msg, fields) => {
    if (LEVELS[lv] < min) return;
    const rec = Object.assign({ ts: new Date().toISOString(), level: lv, msg }, base, fields);
    if (sink) { sink(rec); return; }
    let line;
    try { line = JSON.stringify(rec); } catch (e) { line = JSON.stringify({ ts: rec.ts, level: lv, msg, note: 'unserializable fields' }); }
    (LEVELS[lv] >= LEVELS.error ? process.stderr : process.stdout).write(line + '\n');
  };
  const log = {
    debug: (msg, f) => write('debug', msg, f), info: (msg, f) => write('info', msg, f),
    warn: (msg, f) => write('warn', msg, f), error: (msg, f) => write('error', msg, f),
    child: extra => createLogger({ level: Object.keys(LEVELS).find(k => LEVELS[k] === min) || 'info', base: Object.assign({}, base, extra), sink }),
    setLevel: lv => { min = LEVELS[lv] ?? min; },
    enabled: lv => LEVELS[lv] >= min,
  };
  return log;
}
