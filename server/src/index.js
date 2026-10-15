#!/usr/bin/env node
// Start the server from the command line: `npm start` (settings come from environment variables, see config.js).
import { configFromEnv } from './config.js';
import { GameServer } from './server.js';
import { createLogger } from './log.js';

const cfg = configFromEnv();
const log = createLogger({ level: cfg.logLevel, base: { svc: 'rollmodel' } });
const srv = new GameServer(Object.assign({ log }, cfg));

let stopping = false;
async function stop(signal) {
  if (stopping) return; stopping = true;
  log.info('signal', { signal });
  try { await srv.close(); process.exit(0); } catch (e) { log.error('shutdown failed', { err: e.stack || e.message }); process.exit(1); }
}
process.on('SIGTERM', () => stop('SIGTERM'));
process.on('SIGINT', () => stop('SIGINT'));
process.on('unhandledRejection', e => log.error('unhandled rejection', { err: e && (e.stack || e.message || String(e)) }));

srv.listen(cfg.port, cfg.host).then(() => {
  // the port line lets scripts (and the load test) find a server started with PORT=0
  if (process.env.PRINT_PORT) process.stdout.write('PORT=' + srv.port + '\n');
}).catch(e => { log.error('could not start', { err: e.stack || e.message }); process.exit(1); });
