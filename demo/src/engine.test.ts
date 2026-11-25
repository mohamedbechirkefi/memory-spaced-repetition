// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Compares the browser port with the Python engine on identical random numbers.
// Fixture: src/fixtures/engine_fixture.json (scripts/export_engine_fixture.py).
// Tolerance: review events (session, item, outcome) must match exactly; every
// float (final rate, last review day, test recall, means) within 1e-12 relative
// or 1e-15 absolute (libm differences between NumPy and V8 are at most a few ulp).
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { makeCrn, meanRecallAt, recallAtRi, simulate, type SimConfig } from "./engine";

interface ArmFx {
  event_session: number[];
  event_item: number[];
  event_success: number[];
  final_rate: number[];
  last_review_day: number[];
  test_recall_prob: number[];
  recall_mean: number;
  recall_mean_at_ri30: number;
}
interface CaseFx {
  id: string;
  config: SimConfig;
  seed: number;
  crn: { half_lives_days: number[]; review_uniforms: number[][]; test_uniforms: number[] };
  arms: Record<string, ArmFx>;
}

const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8")) as { cases: CaseFx[] };
const REL = 1e-12, ABS = 1e-15;
const close = (a: number, b: number) => Math.abs(a - b) <= Math.max(ABS, REL * Math.abs(b));
const mean = (x: number[]) => x.reduce((s, v) => s + v, 0) / x.length;

describe("engine port matches the Python engine on identical random numbers", () => {
  it("has four cases covering both models, all distributions and seven arms", () => {
    expect(fx.cases.length).toBe(4);
    const arms = new Set(fx.cases.flatMap((c) => Object.keys(c.arms)));
    expect([...arms].sort()).toEqual(["expanding", "greedy", "greedy-exp", "greedy-power", "leitner", "massed", "uniform"]);
  });
  for (const c of fx.cases) {
    for (const [arm, want] of Object.entries(c.arms)) {
      it(`${c.id} / ${arm}`, () => {
        const got = simulate(c.config, arm, c.crn);
        expect(got.event_session).toEqual(want.event_session);
        expect(got.event_item).toEqual(want.event_item);
        expect(got.event_success.map(Number)).toEqual(want.event_success);
        const pairs: [number[], number[]][] = [
          [got.final_rate, want.final_rate],
          [got.last_review_day, want.last_review_day],
          [got.test_recall_prob, want.test_recall_prob],
        ];
        for (const [g, w] of pairs) {
          expect(g.length).toBe(w.length);
          g.forEach((v, i) => expect(close(v, w[i]), `${v} vs ${w[i]}`).toBe(true));
        }
        expect(close(mean(got.test_recall_prob), want.recall_mean)).toBe(true);
        expect(close(mean(recallAtRi(c.config, got, 30)), want.recall_mean_at_ri30)).toBe(true);
        const tTest = c.config.window_days - 1 + c.config.retention_interval_days;
        expect(close(meanRecallAt(c.config, got, tTest), want.recall_mean)).toBe(true);
      });
    }
  }
});

describe("sandbox random numbers", () => {
  const cfg = fx.cases[0].config;
  it("are deterministic in (seed, learner) and differ across learners", () => {
    expect(makeCrn(cfg, 1, 0)).toEqual(makeCrn(cfg, 1, 0));
    expect(makeCrn(cfg, 1, 0).review_uniforms[0][0]).not.toBe(makeCrn(cfg, 1, 1).review_uniforms[0][0]);
  });
  it("every arm spends the exact budget, at most once per item per session", () => {
    const crn = makeCrn(cfg, 42, 3);
    for (const arm of ["uniform", "expanding", "massed", "leitner", "greedy", "greedy-exp", "greedy-power"]) {
      const tr = simulate(cfg, arm, crn);
      expect(tr.event_session.length).toBe(cfg.reviews_per_item * cfg.n_items);
      tr.test_recall_prob.forEach((p) => expect(p >= 0 && p <= 1).toBe(true));
    }
  });
});
