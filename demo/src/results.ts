// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  /** Frozen decision-rule label, where the manuscript prints one. */
  rule: string | null;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  /** confirmatory | descriptive | exploratory | not run */
  kind: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
  /** design | calibrated | assumption */
  kind: string;
}

// ---- MEMORY extensions (top-level keys added by scripts/export_demo_data.py)

export const ARMS5 = ["greedy", "expanding", "uniform", "leitner", "massed"] as const;
export type Arm5 = (typeof ARMS5)[number];

export interface SweepCell {
  cell_id: string;
  true_model: "exponential" | "power";
  reviews_per_item: number;
  retention_interval_days: number;
  item_distribution: "homogeneous" | "lognormal" | "bimodal";
  means: Record<Arm5, number>;
  means_display: Record<Arm5, string>;
  greedy_minus_uniform: { estimate: number; ci_low: number; ci_high: number; display: string; interval_display: string };
  rank_order: string[];
}

export interface CalendarArm {
  peak_daily_load: number;
  sessions_used: number;
  mean_R: number;
  mean_R_display: string;
  ci_low: number;
  ci_high: number;
  mean_R_interval_display: string;
}

export interface Calendar {
  days: number[];
  budget: number;
  n_items: number;
  loads: Record<string, number[]>;
  measured: Record<string, CalendarArm>;
  note: string;
}

export interface Scenario {
  id: string;
  label: string;
  config: Record<string, number | string>;
  arms: string[];
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  sweep: SweepCell[];
  calendar: Calendar;
  sandbox_scenarios: Scenario[];
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    rule: o.rule === null || o.rule === undefined ? null : str(o, "rule", where),
  };
  if (e.display === null) throw new ResultsError(`${where}.display: expected the manuscript's text`);
  if (e.ci_low !== null && e.interval_display === null) {
    throw new ResultsError(`${where}.interval_display: an interval must carry its printed text`);
  }
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      kind: oneOf(e, "kind", w, ["confirmatory", "descriptive", "exploratory", "not run"]),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
        kind: oneOf(a, "kind", `assumptions[${i}]`, ["design", "calibrated", "assumption"]),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    sweep: sweep(arr(o, "sweep", "results")),
    calendar: calendar(obj(o.calendar, "calendar")),
    sandbox_scenarios: arr(o, "sandbox_scenarios", "results").map((v, i) => scenario(v, `sandbox_scenarios[${i}]`)),
  };
}

function oneOf(o: Obj, k: string, where: string, allowed: string[]): string {
  const v = str(o, k, where);
  if (!allowed.includes(v)) throw new ResultsError(`${where}.${k}: unexpected value "${v}"`);
  return v;
}

function int(o: Obj, k: string, where: string, min = 0): number {
  const v = num(o, k, where) as number;
  if (!Number.isInteger(v) || v < min) throw new ResultsError(`${where}.${k}: expected an integer >= ${min}`);
  return v;
}

function prob(o: Obj, k: string, where: string): number {
  const v = num(o, k, where) as number;
  if (v < 0 || v > 1) throw new ResultsError(`${where}.${k}: expected a probability`);
  return v;
}

function sweep(raw: unknown[]): SweepCell[] {
  const cells = raw.map((v, i) => {
    const w = `sweep[${i}]`;
    const c = obj(v, w);
    const means = obj(c.means, `${w}.means`);
    const md = obj(c.means_display, `${w}.means_display`);
    const g = obj(c.greedy_minus_uniform, `${w}.greedy_minus_uniform`);
    const gl = num(g, "ci_low", w) as number, gh = num(g, "ci_high", w) as number;
    if (gl > gh) throw new ResultsError(`${w}: ci_low exceeds ci_high`);
    const cell: SweepCell = {
      cell_id: str(c, "cell_id", w),
      true_model: oneOf(c, "true_model", w, ["exponential", "power"]) as SweepCell["true_model"],
      reviews_per_item: int(c, "reviews_per_item", w, 1),
      retention_interval_days: int(c, "retention_interval_days", w),
      item_distribution: oneOf(c, "item_distribution", w, ["homogeneous", "lognormal", "bimodal"]) as SweepCell["item_distribution"],
      means: Object.fromEntries(ARMS5.map((a) => [a, prob(means, a, `${w}.means`)])) as Record<Arm5, number>,
      means_display: Object.fromEntries(ARMS5.map((a) => [a, str(md, a, `${w}.means_display`)])) as Record<Arm5, string>,
      greedy_minus_uniform: {
        estimate: num(g, "estimate", w) as number, ci_low: gl, ci_high: gh,
        display: str(g, "display", w), interval_display: str(g, "interval_display", w),
      },
      rank_order: strArr(c, "rank_order", w),
    };
    if (cell.rank_order.length !== ARMS5.length || !ARMS5.every((a) => cell.rank_order.includes(a))) {
      throw new ResultsError(`${w}.rank_order: expected each of the five arms once`);
    }
    return cell;
  });
  if (cells.length === 0) throw new ResultsError("results.sweep: empty");
  const keys = new Set(cells.map((c) => `${c.true_model}|${c.reviews_per_item}|${c.retention_interval_days}|${c.item_distribution}`));
  if (keys.size !== cells.length) throw new ResultsError("results.sweep: duplicate cell");
  return cells;
}

function calendar(c: Obj): Calendar {
  const days = arr(c, "days", "calendar").map((d, i) => {
    if (typeof d !== "number" || !Number.isInteger(d) || d !== i + 1) throw new ResultsError(`calendar.days[${i}]: expected ${i + 1}`);
    return d;
  });
  const budget = int(c, "budget", "calendar", 1);
  const loadsRaw = obj(c.loads, "calendar.loads");
  const loads: Record<string, number[]> = {};
  for (const [arm, v] of Object.entries(loadsRaw)) {
    if (!Array.isArray(v) || v.length !== days.length || !v.every((x) => typeof x === "number" && Number.isInteger(x) && x >= 0)) {
      throw new ResultsError(`calendar.loads.${arm}: expected one non-negative integer per day`);
    }
    if (v.reduce((s: number, x: number) => s + x, 0) !== budget) throw new ResultsError(`calendar.loads.${arm}: does not spend the budget`);
    loads[arm] = v as number[];
  }
  if (Object.keys(loads).length === 0) throw new ResultsError("calendar.loads: empty");
  const mRaw = obj(c.measured, "calendar.measured");
  const measured: Record<string, CalendarArm> = {};
  for (const arm of Object.keys(loads)) {
    const w = `calendar.measured.${arm}`;
    const m = obj(mRaw[arm], w);
    const lo = prob(m, "ci_low", w), hi = prob(m, "ci_high", w);
    if (lo > hi) throw new ResultsError(`${w}: ci_low exceeds ci_high`);
    measured[arm] = {
      peak_daily_load: int(m, "peak_daily_load", w), sessions_used: int(m, "sessions_used", w),
      mean_R: prob(m, "mean_R", w), mean_R_display: str(m, "mean_R_display", w),
      ci_low: lo, ci_high: hi, mean_R_interval_display: str(m, "mean_R_interval_display", w),
    };
    if (Math.max(...loads[arm]) !== measured[arm].peak_daily_load) throw new ResultsError(`${w}: peak load disagrees with the calendar`);
  }
  return { days, budget, n_items: int(c, "n_items", "calendar", 1), loads, measured, note: str(c, "note", "calendar") };
}

function scenario(v: unknown, w: string): Scenario {
  const s = obj(v, w);
  const cfg = obj(s.config, `${w}.config`);
  for (const k of ["n_items", "window_days", "retention_interval_days", "reviews_per_item", "h0_days", "alpha", "beta", "omega_per_day", "lognormal_sigma", "bimodal_factor"]) {
    num(cfg, k, `${w}.config`);
  }
  oneOf(cfg, "true_model", `${w}.config`, ["exponential", "power"]);
  oneOf(cfg, "item_distribution", `${w}.config`, ["homogeneous", "lognormal", "bimodal"]);
  const arms = strArr(s, "arms", w);
  if (arms.length === 0 || !arms.includes("uniform")) throw new ResultsError(`${w}.arms: must include the uniform baseline`);
  return { id: str(s, "id", w), label: str(s, "label", w), config: cfg as Scenario["config"], arms };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
