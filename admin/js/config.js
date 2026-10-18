// The only two values the dashboard holds. Both are public by design and already ship inside the game:
// every admin power is a database function that checks who is calling.
export const SUPABASE_URL = 'https://nbemerxgukwwtrfgirfl.supabase.co';
export const PUBLISHABLE_KEY = 'sb_publishable_9fux5IpOiTei0HvScvqI1g_iAwSCHPc';

// Test hooks (shorter idle timers). Always null here: only the dev mock (dev/mock.mjs) serves a config with them.
export const DEV = null;
