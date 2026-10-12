// the Sludge Sewer and the Fishing Raft (their pieces, materials and markings: sewerDress, raftDress and the rest, below with the stage builder)
THEMES.push(
  { id: 'sewer', label: 'Sludge Sewer', sf: ['steelPlate', 'steelWall'], uv: 0.25, ft: 0xDCE2DA, st: 0xB6BCB6, dt: 0x6A706A, hor: 0x0A160E, fog: [30, 118], sky: [0x010302, 0x030805, 0x07140A], low: 0x050E07, hemi: [0x7AA486, 0x3E8228], sunPos: [8, 30, -5],
    kit: { drum: [1, 2], column: [1, 2], rpit: [1, 2] }, fill: 'drum', pot: 'drum', enclosed: true, slime: true, mirror: true, arch: 'rotunda', noClouds: true,
    base: { hemiI: 0.6, key: 0xE4EEDC, keyI: 0.8 }, env: { top: 0x0A140E, hor: 0x22402A, gnd: 0x3C8C22, sun: 0xE8F2DC, sunK: 0.3 }, lk: { hemi: 0.34, key: 1.22 }, grade: { sat: 1.12, con: 1.1, vig: 0.34, bloom: 0.8, expo: 1.12, tint: [0.98, 1.03, 0.96] }, jglow: 0.8,
    trim: { c: 0xD9A020, m: 0.25, r: 0.45, w: 0.16, h: 0.1 }, foot: { c: 0x1C201C, m: 0.6, r: 0.5 }, edge: 0x7CFF3A, edgeK: 2.4, rimLights: 0.55, cloud: 0x8EA090,
    mkMats: sewerMats, dress: sewerDress, decalDraw: sewerDecal, scatDraw: sewerScatter },
  { id: 'raft', label: 'Fishing Raft', sf: ['deck', 'crate'], uv: 0.3, ft: 0xF2F2F2, st: 0xD8D8D8, dt: 0x8A8A8A, hor: 0xCBE9F2, sky: [0x2A7BD4, 0x76BCEE, 0xD6EEF6], low: 0x2A86BC, hemi: [0xCFE6FA, 0xC4A070], sunPos: [22, 26, 14],
    kit: { drum: [1, 3], column: [1, 2], rpad: [0, 1], rpit: [0, 1] }, fill: 'drum', pot: 'barrel', day: true, sun: 1, sea: true, farIsles: true, arch: 'rotunda', noClouds: true, seaCol: [0x0A4C8C, 0x2AAAC8],
    base: { hemiI: 0.62, key: 0xFFE4BE, keyI: 1.02 }, env: { top: 0x4A86C6, hor: 0xD2EAF2, gnd: 0x2A6A8A, sun: 0xFFE8C0, sunK: 1.1 }, lk: { hemi: 0.34, key: 1.24 }, grade: { sat: 1.2, con: 1.08, vig: 0.12, bloom: 0.45, expo: 1.06, tint: [1.03, 1.0, 0.96] }, jglow: 0.55,
    trim: { c: 0x6A4A30, m: 0, r: 0.7, w: 0.18, h: 0.12 }, foot: { c: 0x4A3424, m: 0, r: 0.85 }, edge: 0xFFFFFF, edgeK: 1.0, cloud: 0xFFFFFF,
    mkMats: raftMats, dress: raftDress, decalDraw: raftDecal, scatDraw: raftScatter }
);
