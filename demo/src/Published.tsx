// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Published (measured) results. Every number shown here comes from
// public/data/results.json, whose display strings are the manuscript's text.
import { useState } from "react";
import { CalendarChart, IntervalChart, Legend, LineChart } from "./charts";
import { InkFigure, Segmented } from "./ui";
import { ARMS5, fmtEstimate, fmtInterval, type Estimate, type Experiment, type Results, type SweepCell } from "./results";

const KIND_LABEL: Record<string, string> = {
  confirmatory: "Measured: confirmatory",
  descriptive: "Measured: confirmatory run, descriptive",
  exploratory: "Measured: exploratory",
  "not run": "Not run",
};

export function Label({ kind }: { kind: "measured" | "sandbox" | "assumption" | "notrun"; children?: never }) {
  const text = { measured: "Measured result", sandbox: "Sandbox output", assumption: "Assumption", notrun: "Not run" }[kind];
  return <span className={`lbl lbl-${kind}`}>{text}</span>;
}

function KindChip({ kind }: { kind: string }) {
  return <span className={`lbl ${kind === "not run" ? "lbl-notrun" : "lbl-measured"}`}>{KIND_LABEL[kind] ?? kind}</span>;
}

const RIS = [1, 7, 30, 281];

const VERDICT_LABEL: Record<string, string> = {
  confirmatory: "Verdict under the frozen rule",
  descriptive: "Descriptive reading (no hypothesis test)",
  exploratory: "Exploratory reading (no frozen verdict)",
  "not run": "Status",
};

export function Overview({ r }: { r: Results }) {
  const e1 = r.experiments.find((e) => e.id === "EXP-001")!.estimates[0];
  const e2 = r.experiments.find((e) => e.id === "EXP-002")!.estimates[1];
  const e3 = r.experiments.find((e) => e.id === "EXP-003")!.estimates[0];
  return (
    <section id="overview" aria-labelledby="h-overview">
      <h2 id="h-overview">The three frozen experiments, filed</h2>
      <p className="status-label"><strong>Status.</strong> {r.status_label}</p>
      <p className="prose"><strong>The question, precisely.</strong> {r.question}</p>
      <p className="prose">
        Five schedules spend exactly the same budget of reviews on 50 synthetic items. The memory models are
        published forgetting curves (exponential and power law) with an update after each review. Nothing here is
        a measurement of human learners.
      </p>
      <div className="cards">
        <article className="icard tab-1">
          <p className="icard-tab">EXP-001</p>
          <div className="icard-body">
            <div className="icard-head"><KindChip kind="confirmatory" /></div>
            <p className="big">{fmtEstimate(e1)}</p>
            <p className="ci">95% interval {fmtInterval(e1)}</p>
            <p>Greedy (oracle model) minus uniform, mean modelled recall. Small, and above zero.</p>
          </div>
        </article>
        <article className="icard tab-2">
          <p className="icard-tab">EXP-002</p>
          <div className="icard-body">
            <div className="icard-head"><KindChip kind="confirmatory" /></div>
            <p className="big">{fmtEstimate(e2)}</p>
            <p className="ci">95% interval {fmtInterval(e2)}</p>
            <p>The same scheduler with a wrong model on power-law learners. Classified as equivalent to uniform (fragile).</p>
          </div>
        </article>
        <article className="icard tab-3">
          <p className="icard-tab">EXP-003</p>
          <div className="icard-body">
            <div className="icard-head"><KindChip kind="descriptive" /></div>
            <p className="big">{fmtEstimate(e3)}</p>
            <p className="ci">count, no interval</p>
            <p>Cells of the sweep in which the EXP-001 ranking of schedules changes.</p>
          </div>
        </article>
      </div>
    </section>
  );
}

export function ForgettingCurves({ r }: { r: Results }) {
  const [model, setModel] = useState<SweepCell["true_model"]>("exponential");
  const [k, setK] = useState(4);
  const [dist, setDist] = useState<SweepCell["item_distribution"]>("lognormal");
  const cells = RIS.map((ri) => r.sweep.find((c) => c.true_model === model && c.reviews_per_item === k && c.item_distribution === dist && c.retention_interval_days === ri));
  if (cells.some((c) => !c)) return <p role="alert" className="panel error">The sweep data are incomplete for this selection.</p>;
  const cs = cells as SweepCell[];
  const all = cs.flatMap((c) => ARMS5.map((a) => c.means[a]));
  const lo = Math.max(0, Math.floor(Math.min(...all) * 10) / 10);
  const yTicks: number[] = [];
  for (let t = lo; t <= 1.0001; t += lo <= 0.3 ? 0.2 : 0.1) yTicks.push(Number(t.toFixed(1)));
  const diffs = cs.map((c) => c.greedy_minus_uniform);
  const dlo = Math.min(-0.03, ...diffs.map((d) => d.ci_low)), dhi = Math.max(0.03, ...diffs.map((d) => d.ci_high));
  const central = model === "exponential" && k === 4 && dist === "lognormal";
  return (
    <section id="curves" aria-labelledby="h-curves">
      <h2 id="h-curves">Forgetting curves after the course <Label kind="measured" /></h2>
      <p className="prose">
        Mean modelled recall <em>R</em> at the test, by how long after the last study session the test happens.
        Each point is a confirmatory EXP-003 cell (50 simulated learners; each retention interval uses its own
        independent block of seeds). Choose a forgetting model, a budget and an item distribution.
      </p>
      <div className="controls seg-row" role="group" aria-label="Sweep cell selection">
        <Segmented id="pub-model" label="Forgetting model" value={model} onChange={setModel}
          options={[{ value: "exponential", label: "exponential" }, { value: "power", label: "power law" }]} />
        <Segmented id="pub-k" label="Reviews per item, k" value={k} onChange={setK}
          options={[2, 4, 8].map((x) => ({ value: x, label: String(x) }))} />
        <Segmented id="pub-items" label="Item distribution" value={dist} onChange={setDist}
          options={[{ value: "homogeneous", label: "homogeneous" }, { value: "lognormal", label: "lognormal" }, { value: "bimodal", label: "bimodal" }]} />
      </div>
      <p className="note">
        {central ? "This is the central setting of EXP-001 (the 281-day point is cell C044, an independent-seed replication)." : "Not the central setting."}
        {" "}The horizontal axis is ordinal, not to scale. The vertical axis starts at {lo.toFixed(1)}.
      </p>
      <InkFigure>
        <LineChart
          title="Mean modelled recall by retention interval"
          desc={`${model} forgetting, k = ${k}, ${dist} items. ${ARMS5.map((a) => `${a}: ${cs.map((c) => c.means_display[a]).join(", ")}`).join("; ")} at 1, 7, 30 and 281 days.`}
          series={ARMS5.map((a) => ({ arm: a, points: cs.map((c, i) => [i, c.means[a]] as [number, number]) }))}
          xPos={(i) => i / 3}
          xTicks={RIS.map((ri, i) => ({ x: i, label: `${ri} d` }))}
          xLabel="retention interval: days from the last session to the test"
          xLabelNarrow="days from last session to test"
          yDomain={[lo, 1]}
          yTicks={yTicks}
          yLabel="mean modelled recall R"
          markers
          pointTitle={(a, i) => `${a}, RI ${RIS[i]} days: R ${cs[i].means_display[a as (typeof ARMS5)[number]]} (cell ${cs[i].cell_id})`}
        />
        <Legend arms={[...ARMS5]} />
        <figcaption>
          Arm means have no interval in EXP-003; the uncertainty of the comparison that matters, greedy minus uniform,
          is shown below with its unadjusted 95% bootstrap interval.
        </figcaption>
      </InkFigure>
      <InkFigure>
        <IntervalChart
          title="Greedy minus uniform by retention interval"
          desc={cs.map((c) => `RI ${c.retention_interval_days} days: ${c.greedy_minus_uniform.display} ${c.greedy_minus_uniform.interval_display}`).join("; ")}
          rows={cs.map((c) => ({
            label: `RI ${c.retention_interval_days} d`, est: c.greedy_minus_uniform.estimate, lo: c.greedy_minus_uniform.ci_low, hi: c.greedy_minus_uniform.ci_high,
            tip: `${c.cell_id}: ${c.greedy_minus_uniform.display} ${c.greedy_minus_uniform.interval_display}`,
          }))}
          domain={[dlo - 0.005, dhi + 0.005]}
        />
        <figcaption>Dot: mean paired difference over 50 learners. Bar: unadjusted 95% bootstrap interval. Grey band: ±0.02.</figcaption>
      </InkFigure>
      <div className="table-scroll" role="region" aria-label="Sweep values for the selected cells" tabIndex={0} id="tbl-sweep">
        <table>
          <caption>Values as printed in research/experiments/EXP-003/results_tables.md</caption>
          <thead>
            <tr><th scope="col">RI (days)</th>{ARMS5.map((a) => <th scope="col" key={a}>R {a}</th>)}<th scope="col">greedy minus uniform</th><th scope="col">95% interval</th><th scope="col">cell</th></tr>
          </thead>
          <tbody>
            {cs.map((c) => (
              <tr key={c.cell_id}>
                <th scope="row">{c.retention_interval_days}</th>
                {ARMS5.map((a) => <td key={a}>{c.means_display[a]}</td>)}
                <td>{c.greedy_minus_uniform.display}</td>
                <td className="num">{c.greedy_minus_uniform.interval_display}</td>
                <td>{c.cell_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function CalendarView({ r }: { r: Results }) {
  const cal = r.calendar;
  const arms = ["uniform", "expanding", "massed", "leitner", "greedy"].filter((a) => a in cal.loads);
  const max = Math.max(...arms.flatMap((a) => cal.loads[a]));
  return (
    <section id="calendar" aria-labelledby="h-calendar">
      <h2 id="h-calendar">Calendar comparison of the schedules <Label kind="measured" /></h2>
      <p className="prose">
        How each schedule spends the same {cal.budget} reviews of {cal.n_items} items over the study days, at the
        EXP-001 setting. Darker cells hold more reviews. Expanding and massed concentrate every review on 4 days;
        the others spread reviews over every session.
      </p>
      <InkFigure>
        <CalendarChart
          days={cal.days}
          rows={arms.map((a) => ({ arm: a, loads: cal.loads[a] }))}
          max={max}
          desc={arms.map((a) => `${a}: reviews on ${cal.measured[a].sessions_used} days, at most ${cal.measured[a].peak_daily_load} per day`).join("; ")}
        />
        <figcaption>{cal.note}</figcaption>
      </InkFigure>
      <div className="table-scroll" role="region" aria-label="Calendar summary and measured recall" tabIndex={0} id="tbl-calendar">
        <table>
          <caption>Load from the schedule definition; mean R measured in EXP-001 (50 learners, 95% bootstrap interval)</caption>
          <thead>
            <tr><th scope="col">arm</th><th scope="col">days with reviews</th><th scope="col">peak reviews per day</th><th scope="col">mean R</th><th scope="col">95% interval</th></tr>
          </thead>
          <tbody>
            {arms.map((a) => (
              <tr key={a}>
                <th scope="row">{a}</th>
                <td>{cal.measured[a].sessions_used}</td>
                <td>{cal.measured[a].peak_daily_load}</td>
                <td>{cal.measured[a].mean_R_display}</td>
                <td className="num">{cal.measured[a].mean_R_interval_display}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <details>
        <summary>Reviews per day, as a table</summary>
        <div className="table-scroll" id="tbl-days">
          <table className="compact">
            <thead><tr><th scope="col">day</th>{arms.map((a) => <th scope="col" key={a}>{a}</th>)}</tr></thead>
            <tbody>
              {cal.days.map((d, i) => (
                <tr key={d}><th scope="row">{d}</th>{arms.map((a) => <td key={a}>{cal.loads[a][i]}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}

function EstimatesTable({ e }: { e: Experiment }) {
  if (e.estimates.length === 0) {
    return <p className="empty"><strong>No estimate.</strong> This check was not run, so there is no number to show.</p>;
  }
  const anyRule = e.estimates.some((x) => x.rule !== null);
  return (
    <div className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0} id={`tbl-${e.id.replace(/\W+/g, "-")}`}>
      <table className="est-table">
        <thead>
          <tr>
            <th scope="col">Quantity</th>
            <th scope="col">Estimate</th>
            <th scope="col">95% interval</th>
            {anyRule && <th scope="col">{e.kind === "confirmatory" ? "Frozen rule" : "Same rule, applied post hoc"}</th>}
          </tr>
        </thead>
        <tbody>
          {e.estimates.map((x) => (
            <tr key={x.label}>
              <th scope="row">{x.label}</th>
              <td className="num" data-label="Estimate">{fmtEstimate(x)}</td>
              <td className="num" data-label="95% interval">{x.ci_low === null ? (x.unit === "cells" ? "count, no interval" : "no interval computed") : fmtInterval(x)}</td>
              {anyRule && <td data-label="Rule">{x.rule ?? "not classified"}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function contrastRows(e: Experiment) {
  return e.estimates
    .filter((x): x is Estimate & { ci_low: number; ci_high: number } => x.rule !== null && x.ci_low !== null && x.ci_high !== null)
    .map((x) => ({ label: x.label.split(" minus")[0], est: x.estimate, lo: x.ci_low, hi: x.ci_high, tip: `${x.label}: ${fmtEstimate(x)} ${fmtInterval(x)}` }));
}

export function PublishedResults({ r }: { r: Results }) {
  return (
    <section id="results" aria-labelledby="h-results">
      <h2 id="h-results">Published results <Label kind="measured" /></h2>
      <p className="note">
        From the committed results at revision <code>{r.code_revision.slice(0, 12)}</code>. Every estimate is printed
        exactly as in the manuscript. Null, not-run and exploratory entries are shown with the same weight as the
        positive ones. Nothing the playground produces appears here.
      </p>
      {r.experiments.map((e) => {
        const rows = e.kind === "confirmatory" ? contrastRows(e) : [];
        return (
          <article key={e.id} className={`panel kind-${e.kind.replace(" ", "-")}`} aria-labelledby={`h-${e.id.replace(/\W+/g, "-")}`}>
            <h3 id={`h-${e.id.replace(/\W+/g, "-")}`}>{e.id}: {e.title}</h3>
            <p><KindChip kind={e.kind} /> <span className="badge">{e.status}</span></p>
            <p><strong>{VERDICT_LABEL[e.kind] ?? "Verdict"}:</strong> {e.verdict}</p>
            {rows.length > 0 && (
              <InkFigure>
                <IntervalChart
                  title={`${e.id}: arm minus uniform`}
                  desc={rows.map((x) => x.tip).join("; ")}
                  rows={rows}
                  domain={[Math.min(-0.03, ...rows.map((x) => x.lo)) - 0.005, Math.max(0.03, ...rows.map((x) => x.hi)) + 0.005]}
                />
                <figcaption>Mean paired difference in R (arm minus uniform) with its 95% percentile bootstrap interval over 50 learners; grey band ±0.02.</figcaption>
              </InkFigure>
            )}
            <EstimatesTable e={e} />
            {e.notes.map((n, i) => <p key={i} className="note">{n}</p>)}
            <p className="meta">Report: <code>{e.report_path}</code></p>
            {e.claim_ids.length > 0 && <p className="meta">Claims: {e.claim_ids.join(", ")}</p>}
          </article>
        );
      })}
    </section>
  );
}

export function Assumptions({ r }: { r: Results }) {
  const kinds: [string, string][] = [["assumption", "Planning assumptions (not estimates)"], ["calibrated", "Calibrated to public data"], ["design", "Design choices"]];
  return (
    <section id="assumptions" aria-labelledby="h-assumptions">
      <h2 id="h-assumptions">Assumptions <Label kind="assumption" /></h2>
      <p>The setting every published result depends on. These values are inputs, not findings.</p>
      {kinds.map(([k, title]) => (
        <div key={k}>
          <h3>{title}</h3>
          <dl className="assumptions">
            {r.assumptions.filter((a) => a.kind === k).map((a) => (
              <div key={a.name}>
                <dt>{a.name}</dt>
                <dd>{a.value} <span className="meta">({a.source})</span></dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
    </section>
  );
}

export function Method({ r }: { r: Results }) {
  return (
    <section id="method" aria-labelledby="h-method">
      <h2 id="h-method">Method and limitations</h2>
      <p className="prose">
        Each simulated learner holds 50 items, first studied on day 0. Recall of an item decays as
        exp(−n·Δ) or (1 + ω·Δ)<sup>−n</sup>, where Δ is the time since its last review. A review succeeds with that
        probability; success multiplies n by (1 − α), failure by (1 + β). Every schedule places exactly the same
        number of reviews in the study window. Arms are compared on the same learners (common random numbers), and
        differences use 95% percentile bootstrap intervals over learners. The protocols, configurations and seeds
        were frozen and hashed before any confirmatory run.
      </p>
      <h3>Limitations</h3>
      <ul>{r.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul>
      <details>
        <summary>Source files and hashes</summary>
        <ul className="meta">
          {r.sources.map((s) => <li key={s.path}><code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code></li>)}
        </ul>
      </details>
    </section>
  );
}
