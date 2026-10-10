// load a rigged axolotl (bin + json) into a THREE.SkinnedMesh with its skeleton; bones keep their rest in world-aligned space
import * as THREE from 'three';
export async function loadAxo(name, tex) {
  const meta = await (await fetch('/axo/' + name + '.json')).json(), buf = await (await fetch('/axo/' + name + '.bin')).arrayBuffer();
  const n = meta.n, o = meta.off, g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
  g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
  g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
  g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
  const bones = [], byName = {};
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bn.userData.rest = new THREE.Vector3(...b.pos); bn.userData.end = new THREE.Vector3(...b.end); bones.push(bn); byName[b.name] = bn; }
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i], p = b.parent ? byName[b.parent] : null; if (p) { p.add(bn); bn.position.copy(bn.userData.rest).sub(p.userData.rest); } else bn.position.copy(bn.userData.rest); }
  const root = bones[0]; const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.55, metalness: 0 });
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(root); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false;
  return { mesh, bones, byName, meta };
}
