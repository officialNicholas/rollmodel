// Server settings from environment variables. Anything not set falls back to a sensible default.
//   PORT (8080)  HOST (0.0.0.0)  DATA_FILE (./data/store.json, or "memory")  LOG_LEVEL (info: debug|info|warn|error|silent)
//   ALLOWED_ORIGINS (comma list; empty allows any; the iOS app's page is rollmodel://localhost)
//   MAX_CONNECTIONS (5000)  MAX_PER_IP (64)  TRUST_PROXY (0; 1 to take the client address from X-Forwarded-For)
//   SNAPSHOT_HZ (30)  SHUTDOWN_GRACE_MS (3000)  RULES (JSON object overriding rules, for test servers)
//   Notifications (v391, src/push.js): APNS_KEY_ID, APNS_TEAM_ID, APNS_KEY_P8, APNS_BUNDLE_ID, APNS_PRODUCTION,
//   SUPABASE_URL, SUPABASE_KEY. Set as Fly secrets, never in a file; with no key, no notifications
import { pushFromEnv } from './push.js';
export function configFromEnv(env = process.env) {
  const int = (k, d, lo, hi) => { const v = parseInt(env[k], 10); return Number.isFinite(v) && v >= lo && v <= hi ? v : d; };
  let rules = {};
  if (env.RULES) { try { const r = JSON.parse(env.RULES); if (r && typeof r === 'object') rules = r; } catch (e) { throw new Error('RULES is not valid JSON'); } }
  if (env.SNAPSHOT_HZ) rules.snapshotHz = int('SNAPSHOT_HZ', 30, 10, 60);
  return {
    port: int('PORT', 8080, 0, 65535),
    host: env.HOST || '0.0.0.0',
    dataFile: env.DATA_FILE || './data/store.json',
    logLevel: env.LOG_LEVEL || 'info',
    allowedOrigins: (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean),
    maxConnections: int('MAX_CONNECTIONS', 5000, 1, 1e6),
    maxPerIp: int('MAX_PER_IP', 64, 1, 1e6),
    trustProxy: env.TRUST_PROXY === '1' || env.TRUST_PROXY === 'true',
    shutdownGraceMs: int('SHUTDOWN_GRACE_MS', 3000, 0, 60000),
    rules,
    push: pushFromEnv(env),
  };
}
