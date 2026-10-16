// The boss model, step 1: read the owner's FBX with three's own FBXLoader (r186, the version the game runs) in Node, and write out what
// the rig builder needs: the mesh in the file's world space (positions, normals and uvs as raw float32, one corner per triangle corner)
// and the embedded base colour texture. Node has no image decoder, so the loader's texture fetch is swapped for one that keeps the
// blob url, and the bytes are read back from that blob.
// usage: THREE_DIR=<node_modules/three> node fbx_extract.mjs <in.fbx> <out dir>
import fs from 'node:fs';
import path from 'node:path';
import { resolveObjectURL } from 'node:buffer';
const DIR = process.env.THREE_DIR || '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/node_modules/three';
const THREE = await import(DIR + '/build/three.module.js');
const { FBXLoader } = await import(DIR + '/examples/jsm/loaders/FBXLoader.js');
const [src, out] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
THREE.TextureLoader.prototype.load = function (url) { const t = new THREE.Texture(); t.userData.url = url; return t; };
const buf = fs.readFileSync(src);
const root = new FBXLoader().parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength), '');
root.updateMatrixWorld(true);
const meshes = []; root.traverse(o => { if (o.isMesh) meshes.push(o); });
if (meshes.length !== 1) throw new Error('expected one mesh, got ' + meshes.length);
const o = meshes[0], g = o.geometry.clone().applyMatrix4(o.matrixWorld), mat = Array.isArray(o.material) ? o.material[0] : o.material;
const f32 = a => Buffer.from(new Float32Array(a).buffer);
fs.writeFileSync(path.join(out, 'pos.f32'), f32(g.attributes.position.array));
fs.writeFileSync(path.join(out, 'nrm.f32'), f32(g.attributes.normal.array));
fs.writeFileSync(path.join(out, 'uv.f32'), f32(g.attributes.uv.array));
const info = { name: o.name, corners: g.attributes.position.count, indexed: !!g.index, material: mat.name };
if (g.index) fs.writeFileSync(path.join(out, 'idx.u32'), Buffer.from(new Uint32Array(g.index.array).buffer));
if (mat.map && mat.map.userData.url) { const b = resolveObjectURL(mat.map.userData.url); fs.writeFileSync(path.join(out, 'base.png'), Buffer.from(await b.arrayBuffer())); info.base = { type: b.type, bytes: b.size }; }
fs.writeFileSync(path.join(out, 'info.json'), JSON.stringify(info, null, 1));
console.log(JSON.stringify(info));
