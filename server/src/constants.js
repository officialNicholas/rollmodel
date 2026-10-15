// Game constants, copied from the game's own tuning (game/index.html). Units: metres and seconds.
export const G = Object.freeze({
  SPEED: 5.4, // cfg.speed in versus
  MOVE_K: 1.06,
  TURF_OWN: 1.18, // on your own colour
  RAIN_MUL: 2.0, // speedMul at the height of the rain
  SLOPE_MAX: 1.4, // rolling down a ramp
  GIANT_SPD: 1.75, GIANT_CAP: 1.9,
  ROLL_T: 0.5, ROLL_DASH: 0.32, ROLL_CD: 1.5, ROLL_COST: 0.03, DASH_T: 0.35,
  GRAV: 15, FALL_K: 1.45, JUMP_V: 5.6,
  PR: 0.34, STEP: 0.32, TW: 0.8,
  SLAM_CD: 6, SLAM_FIRST: 4, SLAM_COST: 0.25, POUND_MIN: 0.249, SLAM_R: 3, MISSILE_R: 4, MISSILE_SPD: 2.6, GIANT_SLAM: 1.5,
  POUND_T: 0.569, // a pound from the ground: 0.353 s up, 0.14 s hang, 0.076 s down
  SPLAT_R: 1.35, SPLAT_COST: 0.06,
  DRAIN: 1 / 21, STILL_DRAIN: 0.02, OWN_REFILL: 0.09, REGEN: 0.55, INK_RUSH: 3.2,
  RESPAWN_T: 3.5, FLAT_T: 1.5, SPAWN_SAFE: 4, SPAWN_GRACE: 1,
  MATCH_T: 90, SD_T: 180, SD_HEARTS: 2, SD_OUT_T: 2.4,
  ZONE_AT: [60, 120], ZONE_SZ: [26.4, 20], ZONE_WARN: 15, ZONE_BURN: 0.32,
  POT_REACH: 0.5 + 0.34 * 0.95, POT_POP_Y: 0.55,
  FLING_MIN: 0.08,
  WHIRL_V: 5.4 * 1.06 * 2.5, WHIRL_T: 1.3 + 1.1 + 0.4,
  ROCKET_ALT: 22, ROCKET_SPD: 12.5,
});
export const KO_R = G.SLAM_R + G.PR; // 3.34
export const launchSpd = c => G.SPEED * (0.9 + 1.7 * c) * 0.8; // fling, horizontal (max 11.2)
export const launchV = c => G.JUMP_V * (0.55 + 0.8 * c) * 0.935; // fling, vertical (max 7.07)

export const MODE_INFO = Object.freeze({
  duel: { players: 2, arena: 26.4, sides: [0, 1], showdown: false },
  trio: { players: 3, arena: 33, sides: [0, 1, 2], showdown: false },
  ffa: { players: 4, arena: 33, sides: [0, 1, 2, 3], showdown: true },
  duo: { players: 4, arena: 33, sides: [0, 1, 1, 0], showdown: true }, // the game's 2v2 sides: you and the third rival
});
export const MODES = Object.keys(MODE_INFO);

// Server rules. Every value can be overridden per server (createGameServer({ rules })), which the tests use to run
// short matches. Times are in seconds unless the name ends in Ms.
export const DEFAULT_RULES = Object.freeze({
  matchT: G.MATCH_T, sdT: G.SD_T, hearts: G.SD_HEARTS,
  countdown: 3, startLead: 0.25, // the countdown starts this long after the start message is sent
  respawnT: G.RESPAWN_T, flatT: G.FLAT_T, sdOutT: G.SD_OUT_T,
  slamFirst: G.SLAM_FIRST, slamCd: G.SLAM_CD,
  layoutTimeout: 15, reconnectWindow: 20, afkWarn: 5, afkForfeit: 15, idleForfeit: 40,
  rematchWindow: 15, endLinger: 0,
  weather: true, items: true, zone: true,
  itemFirst: [6, 9], itemEvery: [9, 13], // seconds: when the first pick-up appears, and the gap between them
  // The spec says a player hidden in a pot is safe from a pound. The current single-player game knocks them out instead
  // ("Nailed!"); set this to false to match the game.
  potShields: true,
  lagCompMaxMs: 200, // the attacker's view time is at most this far before the moment of the event
  dodgeWaitMs: 150, // a pound waits up to this long for the target's own dodge to arrive before it is decided
  maxRewindMs: 450, // absolute cap on how far back any rewind can reach
  snapshotHz: 30, coverageHz: 4,
  strikesToKick: 6, strikeDecay: 20, // one strike forgiven every strikeDecay seconds of clean play
  potDownT: 4.6, potInk: 1.0, potRefill: 0.04, // (a drained or burst pot is gone this long, about as long as the game's own: 1 s sinking, 3.6 s down)
  koPct: 2, // versus: each knock-out adds this many points to the coverage score, as in the game
  overtime: 10, // versus: a tie at the buzzer plays on this many seconds, once (0: a tie is a draw)
});

export const LIMITS = Object.freeze({
  maxPayload: 64 * 1024, // ws closes the connection above this (layouts are the largest messages)
  maxJson: 2048, // any JSON message other than a layout
  maxLayoutJson: 60 * 1024,
  layout: { boxes: 400, ramps: 200, holes: 120, pots: 32, powers: 48, spawns: 8, puddles: 48 },
  nameMin: 1, nameMax: 16, lookMax: 512,
  helloTimeoutMs: 5000,
});
