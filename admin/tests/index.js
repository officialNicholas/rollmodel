// `node --test admin/tests/` on Node 22 runs a folder as a module, which means this file: it loads every
// *.test.mjs beside it. (Node 20 finds the *.test.mjs files itself and never runs this.)
import { readdirSync } from 'node:fs';

const here = new URL('./', import.meta.url);
for (const f of readdirSync(here).filter((f) => f.endsWith('.test.mjs')).sort()) await import(new URL(f, here));
