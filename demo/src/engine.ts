// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Browser port of the research engine (src/memory_research/: models.py,
// schedules.py, simulate.py). Given the same common random numbers, it
// reproduces the Python traces; engine.test.ts checks this against
// src/fixtures/engine_fixture.json. Only the random-number generator differs
// (makeCrn below uses mulberry32 and Box-Muller, not NumPy's PCG64), so a
// sandbox seed is not the research seed of the same number.

export type Model = "exponential" | "power";
export type Distribution = "homogeneous" | "lognormal" | "bimodal";

export interface SimConfig {
  n_items: number;
  window_days: number;
  retention_interval_days: number;
  reviews_per_item: number;
  h0_days: number;
  alpha: number;
  beta: number;
  omega_per_day: number;
  true_model: Model;
  item_distribution: Distribution;
  lognormal_sigma: number;
  bimodal_factor: number;
}

export interface Crn {
  half_lives_days: number[];
  review_uniforms: number[][]; // [item][j-th review]
  test_uniforms: number[];
}

export interface Trace {
  arm: string;
  event_session: number[];
  event_item: number[];
  event_success: boolean[];
  final_rate: number[];
  last_review_day: number[];
  test_recall_prob: number[];
  /** Rate in effect after each review, per item: [day, rate] pairs, starting with [0, initial rate]. */
  history: [number, number][][];
}

export const ARMS = ["uniform", "expanding", "massed", "leitner", "greedy", "greedy-exp", "greedy-power"] as const;
export const LN2 = Math.log(2);
const LEITNER_INTERVALS = [1, 2, 4, 8, 16];

export class EngineError extends Error {}

export function validateConfig(c: SimConfig): void {
  const ints = [c.n_items, c.window_days, c.retention_interval_days, c.reviews_per_item];
  if (!ints.every((x) => Number.isInteger(x))) throw new EngineError("integer fields must be integers");
  if (c.n_items < 1 || c.n_items > 200) throw new EngineError("n_items must be 1 to 200 in the sandbox");
  if (c.window_days < 2 || c.window_days > 120) throw new EngineError("window_days must be 2 to 120 in the sandbox");
  if (c.retention_interval_days < 0) throw new EngineError("retention_interval_days must be >= 0");
  if (c.reviews_per_item < 1 || c.reviews_per_item > c.window_days - 1) throw new EngineError("reviews_per_item must be 1 to D-1");
  for (const x of [c.h0_days, c.omega_per_day, c.lognormal_sigma, c.bimodal_factor]) {
    if (!(Number.isFinite(x) && x > 0)) throw new EngineError("positive parameters must be finite and > 0");
  }
  if (!(c.alpha > 0 && c.alpha < 1)) throw new EngineError("alpha must satisfy 0 < alpha < 1");
  if (!(Number.isFinite(c.beta) && c.beta >= 0)) throw new EngineError("beta must be >= 0");
  if (c.true_model !== "exponential" && c.true_model !== "power") throw new EngineError("unknown model");
  if (!["homogeneous", "lognormal", "bimodal"].includes(c.item_distribution)) throw new EngineError("unknown item distribution");
}

export function recall(model: Model, rate: number, delta: number, omega: number): number {
  return model === "exponential" ? Math.exp(-rate * delta) : Math.exp(-rate * Math.log1p(omega * delta));
}

export function initialRate(model: Model, h: number, omega: number): number {
  return model === "exponential" ? LN2 / h : LN2 / Math.log1p(omega * h);
}

function updateRate(rate: number, success: boolean, alpha: number, beta: number): number {
  return success ? (1.0 - alpha) * rate : (1.0 + beta) * rate;
}

const ceilDiv = (a: number, b: number) => -Math.floor(-a / b);

// ------------------------------------------------------------ fixed plans

export function uniformPlan(c: SimConfig): number[][] {
  const n = c.n_items, k = c.reviews_per_item, sMax = c.window_days - 1;
  const plan: number[][] = [];
  for (let i = 0; i < n; i++) {
    const row: number[] = [];
    for (let j = 0; j < k; j++) row.push(ceilDiv(sMax * (i + 1 + j * n), k * n));
    plan.push(row);
  }
  return plan;
}

export function expandingSessions(k: number, sMax: number): number[] {
  if (!(k >= 1 && k <= sMax)) throw new EngineError("need 1 <= k <= D-1");
  const denom = 2 ** k - 1;
  const out: number[] = [];
  let prev = 0;
  for (let j = 0; j < k; j++) {
    const num = sMax * (2 ** (j + 1) - 1);
    const target = Math.floor((2 * num + denom) / (2 * denom));
    const s = Math.max(target, prev + 1);
    out.push(s);
    prev = s;
  }
  if (out[out.length - 1] !== sMax) throw new EngineError("expanding schedule does not end at D-1");
  return out;
}

export function planFor(arm: string, c: SimConfig): number[][] | null {
  const sMax = c.window_days - 1, k = c.reviews_per_item;
  if (arm === "uniform") return uniformPlan(c);
  if (arm === "expanding") {
    const s = expandingSessions(k, sMax);
    return Array.from({ length: c.n_items }, () => [...s]);
  }
  if (arm === "massed") {
    const s = Array.from({ length: k }, (_, j) => sMax - k + 1 + j);
    return Array.from({ length: c.n_items }, () => [...s]);
  }
  return null;
}

export function dailyCapacity(c: SimConfig): number[] {
  const b = c.reviews_per_item * c.n_items, sMax = c.window_days - 1;
  const cap: number[] = [];
  for (let s = 1; s <= sMax; s++) cap.push(Math.floor((s * b) / sMax) - Math.floor(((s - 1) * b) / sMax));
  if (Math.max(...cap) > c.n_items) throw new EngineError("daily capacity exceeds N");
  return cap;
}

// ------------------------------------------------------------ schedulers

interface Scheduler {
  select(session: number): number[];
  observe(session: number, items: number[], success: boolean[]): void;
}

/** Sort item indices by a lexicographic key (all keys ascending), as numpy.lexsort with the key order reversed. */
function lexOrder(n: number, key: (i: number) => number[]): number[] {
  const idx = Array.from({ length: n }, (_, i) => i);
  const keys = idx.map(key);
  idx.sort((a, b) => {
    const ka = keys[a], kb = keys[b];
    for (let t = 0; t < ka.length; t++) if (ka[t] !== kb[t]) return ka[t] < kb[t] ? -1 : 1;
    return 0;
  });
  return idx;
}

function fixedScheduler(plan: number[][], sMax: number): Scheduler {
  const bySession: number[][] = Array.from({ length: sMax + 1 }, () => []);
  plan.forEach((sessions, i) => sessions.forEach((s) => {
    if (s < 1 || s > sMax) throw new EngineError("session outside the window");
    bySession[s].push(i);
  }));
  return { select: (s) => bySession[s], observe: () => {} };
}

function leitnerScheduler(c: SimConfig): Scheduler {
  const cap = dailyCapacity(c), n = c.n_items;
  const box = new Array<number>(n).fill(1), due = new Array<number>(n).fill(1), reviewed = new Array<boolean>(n).fill(false);
  return {
    select(s) {
      return lexOrder(n, (i) => [reviewed[i] ? 1 : 0, due[i] > s ? 1 : 0, due[i], box[i], i]).slice(0, cap[s - 1]);
    },
    observe(s, items, success) {
      items.forEach((i, t) => {
        const nb = success[t] ? Math.min(box[i] + 1, LEITNER_INTERVALS.length) : 1;
        box[i] = nb;
        due[i] = s + LEITNER_INTERVALS[nb - 1];
        reviewed[i] = true;
      });
    },
  };
}

function greedyScheduler(model: Model, c: SimConfig, halfLives: number[]): Scheduler {
  const cap = dailyCapacity(c), n = c.n_items, omega = c.omega_per_day;
  const rate = halfLives.map((h) => initialRate(model, h, omega));
  const last = new Array<number>(n).fill(0), reviewed = new Array<boolean>(n).fill(false);
  return {
    select(s) {
      const m = rate.map((r, i) => recall(model, r, s - last[i], omega));
      return lexOrder(n, (i) => [reviewed[i] ? 1 : 0, m[i], i]).slice(0, cap[s - 1]);
    },
    observe(s, items, success) {
      items.forEach((i, t) => {
        rate[i] = updateRate(rate[i], success[t], c.alpha, c.beta);
        last[i] = s;
        reviewed[i] = true;
      });
    },
  };
}

export function makeScheduler(arm: string, c: SimConfig, halfLives: number[]): Scheduler {
  const plan = planFor(arm, c);
  if (plan) return fixedScheduler(plan, c.window_days - 1);
  if (arm === "leitner") return leitnerScheduler(c);
  if (arm === "greedy") return greedyScheduler(c.true_model, c, halfLives);
  if (arm === "greedy-exp") return greedyScheduler("exponential", c, halfLives);
  if (arm === "greedy-power") return greedyScheduler("power", c, halfLives);
  throw new EngineError(`unknown arm ${arm}`);
}

// ------------------------------------------------------------ simulation

export function simulate(c: SimConfig, arm: string, crn: Crn): Trace {
  validateConfig(c);
  const n = c.n_items, sMax = c.window_days - 1, omega = c.omega_per_day;
  if (crn.half_lives_days.length !== n || crn.review_uniforms.length !== n) throw new EngineError("random numbers do not match the configuration");
  const sched = makeScheduler(arm, c, crn.half_lives_days);
  const rate = crn.half_lives_days.map((h) => initialRate(c.true_model, h, omega));
  const last = new Array<number>(n).fill(0), count = new Array<number>(n).fill(0);
  const history: [number, number][][] = rate.map((r) => [[0, r]]);
  const evS: number[] = [], evI: number[] = [], evOk: boolean[] = [];
  for (let s = 1; s <= sMax; s++) {
    const items = [...sched.select(s)].sort((a, b) => a - b);
    if (items.length === 0) continue;
    for (let t = 1; t < items.length; t++) if (items[t] === items[t - 1]) throw new EngineError("item reviewed twice in a session");
    const success = items.map((i) => {
      const m = recall(c.true_model, rate[i], s - last[i], omega);
      return crn.review_uniforms[i][count[i]] < m;
    });
    items.forEach((i, t) => {
      rate[i] = updateRate(rate[i], success[t], c.alpha, c.beta);
      last[i] = s;
      count[i] += 1;
      history[i].push([s, rate[i]]);
      evS.push(s);
      evI.push(i);
      evOk.push(success[t]);
    });
    sched.observe(s, items, success);
  }
  const tTest = c.window_days - 1 + c.retention_interval_days;
  return {
    arm,
    event_session: evS,
    event_item: evI,
    event_success: evOk,
    final_rate: [...rate],
    last_review_day: [...last],
    test_recall_prob: rate.map((r, i) => recall(c.true_model, r, tTest - last[i], omega)),
    history,
  };
}

/** Mean true recall over items at time t (days), from a trace's rate history. */
export function meanRecallAt(c: SimConfig, tr: Trace, t: number): number {
  let sum = 0;
  for (const h of tr.history) {
    let k = 0;
    while (k + 1 < h.length && h[k + 1][0] <= t) k++;
    sum += recall(c.true_model, h[k][1], t - h[k][0], c.omega_per_day);
  }
  return sum / tr.history.length;
}

export function recallAtRi(c: SimConfig, tr: Trace, ri: number): number[] {
  const t = c.window_days - 1 + ri;
  return tr.final_rate.map((r, i) => recall(c.true_model, r, t - tr.last_review_day[i], c.omega_per_day));
}

// ------------------------------------------------------------ sandbox random numbers (not NumPy's)

export function mulberry32(a: number): () => number {
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Common random numbers for one sandbox learner: shared by every arm, as in the research design. */
export function makeCrn(c: SimConfig, seed: number, learner: number): Crn {
  const rng = mulberry32((Math.imul(seed, 0x9e3779b1) ^ Math.imul(learner + 1, 0x85ebca6b)) >>> 0);
  const n = c.n_items, sMax = c.window_days - 1;
  const normal = () => {
    const u1 = 1 - rng(), u2 = rng();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };
  const half: number[] = [];
  for (let i = 0; i < n; i++) {
    if (c.item_distribution === "homogeneous") half.push(c.h0_days);
    else if (c.item_distribution === "lognormal") half.push(Math.exp(Math.log(c.h0_days) + c.lognormal_sigma * normal()));
    else half.push(rng() < 0.5 ? c.h0_days / c.bimodal_factor : c.h0_days * c.bimodal_factor);
  }
  const review = Array.from({ length: n }, () => Array.from({ length: sMax }, () => rng()));
  const test = Array.from({ length: n }, () => rng());
  return { half_lives_days: half, review_uniforms: review, test_uniforms: test };
}
