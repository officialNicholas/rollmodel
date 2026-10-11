// The axolotl's look (v7): one procedural layered skin on both meshes, the old slime's face, the paint coat, the soft-body jelly layer.
//  - The skin is drawn from per-vertex data (see extras7.py) and the canonical position of each vertex on the standing body (the crawl mesh
//    is mapped onto it through the skeleton), so both meshes carry the same pattern at the same detail: a team-coloured base with slow
//    tone drift and dorsal mottling, a pale cream belly gradient (throat and chin included), blue-grey speckle spots in two sizes, fine skin
//    relief and pores, wrinkle bands at the knuckles, wrists, elbows, knees, ankles and neck, cavity occlusion, a translucent tail fin with a
//    darker blue-grey core band and a lit edge, feathery saturated gill frills that glow when backlit, and a satin sheen on the belly.
//  - The face is the game's slime face: the same face sheets (drawn by the game's own makeFaceSheets, below), the same shader-drawn
//    pupils, iris colours, catchlights and eye styles (round, squid, dot, zombie), the same expressions, blinks and glances, projected onto
//    the front of the head about the head centre exactly as the slime projects it, on a head that is the same shape in both states.
import * as THREE from 'three';
import { dqsShader } from './axo.js';

// ---------------- the face projection (shared by both meshes: angles about each mesh's face-sphere centre, in rest space) ----------------
// pitch: the face centre's height above the head centre's horizon (rad); half: the angle a face cell's half width spans (rad); the game's
// slime uses pitch 0, half 0.86 on its round head. The axolotl head is a wider dome, so its face sits a little higher and a little tighter.
export const FACE = { pitch: 0.12, half: 0.9, squeeze: 1.0 };
export const EYE_COLS = { brown: { name: 'Brown', lin: [0.16, 0.06, 0.035], css: '#8A5636' }, blue: { name: 'Blue', lin: [0.03, 0.1, 0.32], css: '#3B7BE0' }, green: { name: 'Green', lin: [0.04, 0.18, 0.05], css: '#46A853' },
  violet: { name: 'Violet', lin: [0.14, 0.045, 0.28], css: '#8E52DA' }, gold: { name: 'Gold', lin: [0.34, 0.17, 0.016], css: '#D8A41F' } };
export const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', zombie: 'Zombie' };
export const EYE_STYLE_K = { round: 0, edgy: 1, dot: 2, zombie: 3 };
// each expression is an eye cell and a mouth cell (yawn and dizzy borrow parts of the others), as in the game
export const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11] };
const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 } };
const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 };
export function pupilOf(name) { const F = PUPILS[name] || FACE_LIDS[name]; if (!F) return { pu: 1, py: 0 }; const L = F.L || F; return { pu: L.pu || 1, py: (L.py || 0) * FACE_EYE.ry }; }
