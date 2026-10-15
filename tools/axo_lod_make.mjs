// The distant-level index for the axolotl pack's bodies: meshoptimizer's simplifier over the same vertices (positions, normals and the
// canonical place / UV as attributes so the face and seams hold), written as base64 Uint16 per mesh with the counts it was made for.
import { MeshoptSimplifier as M } from 'meshoptimizer';
import fs from 'fs';
const [,, packPath, ratioS, errS, outPath] = process.argv; const ratio = +ratioS || 0.35, err = +errS || 0.02;
const b64 = fs.readFileSync(packPath, 'utf8').trim(), buf = Buffer.from(b64, 'base64'), ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
const dv = new DataView(ab); if (String.fromCharCode(...new Uint8Array(ab, 0, 4)) !== 'RMA1') throw new Error('not a pack');
const hl = dv.getUint32(4, true), head = JSON.parse(new TextDecoder().decode(new Uint8Array(ab, 8, hl))), base = 8 + hl;
await M.ready; const out = {};
for (const [name, m] of Object.entries(head.meshes)) {
  const meta = m.meta, mb = ab.slice(base + m.off, base + m.off + m.len), n = meta.n, ni = meta.ni;
  if (meta.fmt !== 'axo7') { console.log(name, 'skip fmt', meta.fmt); continue; }
  const o = meta.off7, pos = new Float32Array(mb, o.position, n * 3), idx16 = new Uint16Array(mb, o.index, ni), nrm = new Int8Array(mb, o.normal, n * 4);
  const cpos = new Int16Array(mb, o.cpos, n * 4), uv = o.uv !== undefined ? new Uint16Array(mb, o.uv, n * 2) : null;
  // attributes: normal (3), canonical place (3), uv (2)
  const A = 8, attr = new Float32Array(n * A);
  for (let i = 0; i < n; i++) { attr[i * A] = nrm[i * 4] / 127; attr[i * A + 1] = nrm[i * 4 + 1] / 127; attr[i * A + 2] = nrm[i * 4 + 2] / 127;
    attr[i * A + 3] = cpos[i * 4] / 32767; attr[i * A + 4] = cpos[i * 4 + 1] / 32767; attr[i * A + 5] = cpos[i * 4 + 2] / 32767;
    if (uv) { attr[i * A + 6] = uv[i * 2] / 65535; attr[i * A + 7] = uv[i * 2 + 1] / 65535; } }
  const idx = new Uint32Array(idx16), target = Math.floor(ni * ratio / 3) * 3;
  const [res, e] = M.simplifyWithAttributes(idx, pos, 3, attr, A, [0.5, 0.5, 0.5, 1, 1, 1, 2, 2], null, target, err, []);
  const used = new Set(res); console.log(name, 'verts', n, 'tris', ni / 3, '->', res.length / 3, 'used verts', used.size, 'error', e.toFixed(4));
  out[name] = { n, ni, li: res.length, b64: Buffer.from(new Uint16Array(res).buffer).toString('base64') };
}
fs.writeFileSync(outPath, JSON.stringify(out)); console.log('wrote', outPath, fs.statSync(outPath).size);
