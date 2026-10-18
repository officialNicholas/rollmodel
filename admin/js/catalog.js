// catalog.json: the game's items, Strokes, modes, canvases, tutorial steps and ad placements, with readable names.
// Every label on the dashboard comes from here; ids the catalog doesn't know are shown as they are.

let C = null;
const maps = {};

export async function loadCatalog() {
  const res = await fetch('catalog.json', { cache: 'no-cache', credentials: 'omit' });
  if (!res.ok) throw new Error("The catalog didn't load (" + res.status + ').');
  C = await res.json();
  for (const k of ['items', 'strokes', 'modes', 'stages', 'tutorial', 'ads']) maps[k] = new Map((C[k] || []).map((x) => [x.id, x]));
  return C;
}

export const catalog = () => C;
const get = (k, id) => (maps[k] && maps[k].get(id)) || null;
const name = (k, id) => (get(k, id) || {}).name || String(id ?? '');

export const item = (id) => get('items', id);
export const itemName = (id) => name('items', id);
export const strokeName = (id) => name('strokes', id);
export const modeName = (id) => name('modes', id);
export const stageName = (id) => (get('stages', id) ? name('stages', id) : cap(id));
export const stepName = (id) => name('tutorial', id);
export const adName = (id) => name('ads', id);
export const tutorialIds = () => (C ? C.tutorial.map((t) => t.id) : []);

const cap = (s) => (s ? String(s).charAt(0).toUpperCase() + String(s).slice(1) : 'Unknown');

// CPU difficulties aren't in the catalog: "easy" -> "Easy"
export const diffName = (d) => cap(d);

// Where dabs come from (adm_economy earn[].src)
const EARN = { match: 'Matches', comm: 'Commissions', board: 'Friends board prize', lesson: 'Lesson bonus', gift: 'Gifts', other: 'Other' };
export const earnName = (src) => EARN[src] || String(src || 'Unknown');

// Item slots in plain words
const SLOTS = { head: 'Head', eye: 'Eyes', eyes: 'Eyes', side: 'Side', neck: 'Neck', lash: 'Lashes', mouth: 'Mouth', arms: 'Arms', back: 'Back' };
export const slotName = (s) => SLOTS[s] || s || '';
