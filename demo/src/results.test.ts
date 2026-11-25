// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "", display: "1" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects an estimate without its printed text", () => {
    const r = good();
    delete r.experiments[0].estimates[0].display;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an interval without its printed interval text", () => {
    const r = good();
    r.experiments[0].estimates[0].interval_display = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an unknown experiment kind", () => {
    const r = good();
    r.experiments[0].kind = "promising";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("keeps the not-run omega check visible", () => {
    const e = validateResults(good()).experiments.find((x) => x.kind === "not run");
    expect(e?.id).toBe("EXP-002 ω check");
  });
  it("rejects a missing sweep", () => {
    const r = good();
    delete r.sweep;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a sweep mean outside [0, 1]", () => {
    const r = good();
    r.sweep[0].means.greedy = 1.2;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a sweep cell with a missing arm in its rank order", () => {
    const r = good();
    r.sweep[0].rank_order = r.sweep[0].rank_order.slice(1);
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a calendar that does not spend the budget", () => {
    const r = good();
    r.calendar.loads.uniform[0] += 1;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a calendar whose peak disagrees with the measured runs", () => {
    const r = good();
    r.calendar.measured.massed.peak_daily_load = 8;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a scenario without the uniform baseline", () => {
    const r = good();
    r.sandbox_scenarios[0].arms = ["greedy"];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("exports 72 sweep cells and the central cell C044", () => {
    const r = validateResults(good());
    expect(r.sweep.length).toBe(72);
    expect(r.sweep.find((c) => c.cell_id === "C044")?.greedy_minus_uniform.interval_display).toBe("[0.0113, 0.0218]");
  });
});
