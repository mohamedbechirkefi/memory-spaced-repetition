// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Bounded, cancellable sandbox: runs the browser port of the engine
// (engine.ts) for at most MAX_LEARNERS simulated learners. Nothing is sent
// anywhere; the output lives only in this page.
import { makeCrn, meanRecallAt, simulate, validateConfig, type SimConfig } from "./engine";

export const MAX_LEARNERS = 50;

export interface SandboxRequest {
  config: SimConfig;
  arms: string[];
  seed: number;
  learners: number;
}

export interface ArmOutput {
  arm: string;
  /** Mean modelled recall at the test, one value per sandbox learner. */
  R: number[];
  /** Mean over learners of the mean item recall, at each sample time. */
  curve: [number, number][];
  /** Learner 1's review events, for the calendar. */
  events: { session: number; item: number; success: boolean }[];
}

export interface SandboxOutput {
  request: SandboxRequest;
  arms: ArmOutput[];
}

export type WorkerRequest = { type: "run"; req: SandboxRequest } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; out: SandboxOutput }
  | { type: "cancelled" }
  | { type: "error"; message: string };

let cancelled = false;

export function sampleTimes(c: SimConfig): number[] {
  const end = c.window_days - 1, tTest = end + c.retention_interval_days;
  const t: number[] = [];
  for (let x = 0; x <= end; x += 0.5) t.push(x);
  const steps = 40;
  for (let j = 1; j <= steps; j++) t.push(end + ((tTest - end) * j) / steps);
  return t;
}

export async function runSandbox(req: SandboxRequest, onProgress?: (f: number) => void): Promise<SandboxOutput | null> {
  validateConfig(req.config);
  const learners = Math.max(1, Math.min(MAX_LEARNERS, Math.floor(req.learners)));
  if (!Number.isInteger(req.seed) || req.seed < 0) throw new Error("seed must be a non-negative integer");
  const times = sampleTimes(req.config);
  const out: ArmOutput[] = req.arms.map((arm) => ({ arm, R: [], curve: times.map((t) => [t, 0] as [number, number]), events: [] }));
  for (let l = 0; l < learners; l++) {
    const crn = makeCrn(req.config, req.seed, l);
    out.forEach((o) => {
      const tr = simulate(req.config, o.arm, crn);
      o.R.push(tr.test_recall_prob.reduce((s, v) => s + v, 0) / tr.test_recall_prob.length);
      times.forEach((t, j) => (o.curve[j][1] += meanRecallAt(req.config, tr, t) / learners));
      if (l === 0) o.events = tr.event_session.map((s, k) => ({ session: s, item: tr.event_item[k], success: tr.event_success[k] }));
    });
    await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
    if (cancelled) return null;
    onProgress?.((l + 1) / learners);
  }
  return { request: { ...req, learners }, arms: out };
}

if (typeof self !== "undefined" && typeof (self as unknown as { postMessage?: unknown }).postMessage === "function" && typeof window === "undefined") {
  onmessage = async (ev: MessageEvent<WorkerRequest>) => {
    const m = ev.data;
    if (m.type === "cancel") {
      cancelled = true;
      return;
    }
    cancelled = false;
    try {
      const res = await runSandbox(m.req, (fraction) => postMessage({ type: "progress", fraction } satisfies WorkerReply));
      postMessage((res === null ? { type: "cancelled" } : { type: "done", out: res }) satisfies WorkerReply);
    } catch (e) {
      postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
    }
  };
}
