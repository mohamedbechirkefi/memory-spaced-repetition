// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Visitor playground: runs the browser port of the engine in a Web Worker.
// Its output is labelled as sandbox output and never mixed with the
// published results. Nothing typed or produced here leaves the page.
import { useEffect, useRef, useState } from "react";
import { ARM_ORDER, ItemCalendar, Legend, LineChart } from "./charts";
import type { Distribution, Model, SimConfig } from "./engine";
import { Label } from "./Published";
import type { Scenario } from "./results";
import type { SandboxOutput, WorkerReply, WorkerRequest } from "./sandbox.worker";

const DEFAULT_SEED = 1;
const DEFAULT_LEARNERS = 20;

interface Settings {
  scenario: string;
  model: Model;
  k: number;
  ri: number;
  dist: Distribution;
  learners: number;
  seed: number;
}

function fromScenario(s: Scenario): Settings {
  return {
    scenario: s.id,
    model: s.config.true_model as Model,
    k: Number(s.config.reviews_per_item),
    ri: Number(s.config.retention_interval_days),
    dist: s.config.item_distribution as Distribution,
    learners: DEFAULT_LEARNERS,
    seed: DEFAULT_SEED,
  };
}

const f3 = (x: number) => x.toFixed(3);

export function Sandbox({ scenarios }: { scenarios: Scenario[] }) {
  const worker = useRef<Worker | null>(null);
  const [st, setSt] = useState<Settings>(() => fromScenario(scenarios[0]));
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [msg, setMsg] = useState("");
  const [out, setOut] = useState<SandboxOutput | null>(null);
  const [calArm, setCalArm] = useState("greedy");

  const scenario = scenarios.find((s) => s.id === st.scenario) ?? scenarios[0];
  const config: SimConfig = {
    ...(scenario.config as unknown as SimConfig),
    true_model: st.model,
    reviews_per_item: st.k,
    retention_interval_days: st.ri,
    item_distribution: st.dist,
  };

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") { setProgress(m.fraction); return; }
      setRunning(false);
      if (m.type === "done") {
        setOut(m.out);
        const rq = m.out.request;
        const best = [...m.out.arms].sort((a, b) => mean(b.R) - mean(a.R))[0];
        setMsg(`Sandbox output (seed ${rq.seed}, ${rq.learners} sandbox learners, ${rq.config.true_model} forgetting, k = ${rq.config.reviews_per_item}, RI ${rq.config.retention_interval_days} days): highest mean R ${f3(mean(best.R))} for ${best.arm}; uniform ${f3(mean(m.out.arms.find((a) => a.arm === "uniform")!.R))}.`);
        if (!m.out.arms.some((a) => a.arm === calArmRef.current)) setCalArm(m.out.arms[m.out.arms.length - 1].arm);
      }
      if (m.type === "error") setMsg(`The sandbox run stopped with an error: ${m.message}`);
      if (m.type === "cancelled") setMsg("Sandbox run cancelled. No output.");
    };
    worker.current = w;
    return () => w.terminate();
  }, []);
  const calArmRef = useRef(calArm);
  calArmRef.current = calArm;

  const run = () => {
    setRunning(true);
    setProgress(0);
    setMsg("");
    setOut(null);
    worker.current?.postMessage({ type: "run", req: { config, arms: scenario.arms, seed: st.seed, learners: st.learners } } satisfies WorkerRequest);
  };
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    if (running) cancel();
    setSt(fromScenario(scenarios[0]));
    setOut(null);
    setMsg("Settings reset to the EXP-001 setting, seed 1. No output.");
  };
  const pickScenario = (id: string) => {
    const s = scenarios.find((x) => x.id === id);
    if (s) setSt({ ...fromScenario(s), learners: st.learners, seed: st.seed });
  };
  const download = () => {
    if (!out) return;
    const blob = new Blob([JSON.stringify({ label: "MEMORY sandbox output (browser engine port, not a research result)", ...out }, null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `memory-sandbox-seed-${out.request.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Playground <Label kind="sandbox" /></h2>
      <p className="note">
        The playground runs a port of the research engine in your browser. The port reproduces the Python engine
        exactly when both are given the same random numbers (checked by an automated test), but it draws its own
        random numbers, so sandbox seed 1000 is not research seed 1000. Its numbers are not research results and are
        not comparable to the published numbers above. Nothing you choose here is stored or sent anywhere.
      </p>
      <div className="controls" role="group" aria-label="Playground settings">
        <label>Scenario{" "}
          <select id="sb-scenario" value={st.scenario} onChange={(e) => pickScenario(e.target.value)} disabled={running}>
            {scenarios.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
          </select>
        </label>
        <label>Forgetting model{" "}
          <select id="sb-model" value={st.model} onChange={(e) => setSt({ ...st, model: e.target.value as Model })} disabled={running}>
            <option value="exponential">exponential</option>
            <option value="power">power law</option>
          </select>
        </label>
        <label>Reviews per item, k{" "}
          <select id="sb-k" value={st.k} onChange={(e) => setSt({ ...st, k: Number(e.target.value) })} disabled={running}>
            {[1, 2, 4, 8].map((x) => <option key={x} value={x}>{x}</option>)}
          </select>
        </label>
        <label>Retention interval{" "}
          <select id="sb-ri" value={st.ri} onChange={(e) => setSt({ ...st, ri: Number(e.target.value) })} disabled={running}>
            {[1, 7, 30, 90, 281].map((x) => <option key={x} value={x}>{x} days</option>)}
          </select>
        </label>
        <label>Items{" "}
          <select id="sb-items" value={st.dist} onChange={(e) => setSt({ ...st, dist: e.target.value as Distribution })} disabled={running}>
            <option value="homogeneous">homogeneous</option>
            <option value="lognormal">lognormal</option>
            <option value="bimodal">bimodal</option>
          </select>
        </label>
        <label>Learners{" "}
          <input id="sb-learners" type="number" min={1} max={50} value={st.learners} disabled={running}
            onChange={(e) => setSt({ ...st, learners: Math.max(1, Math.min(50, Math.floor(Number(e.target.value)) || 1)) })} />
        </label>
        <label>Seed{" "}
          <input id="sb-seed" type="number" min={0} max={1_000_000} value={st.seed} disabled={running}
            onChange={(e) => setSt({ ...st, seed: Math.max(0, Math.min(1_000_000, Math.floor(Number(e.target.value)) || 0)) })} />
        </label>
      </div>
      <p className="meta">
        Arms: {scenario.arms.join(", ")}. Fixed: N {config.n_items} items, window {config.window_days} days, h0 {config.h0_days} days,
        σ {config.lognormal_sigma}, α {config.alpha}, β {config.beta}, ω {config.omega_per_day} per day.
      </p>
      <div className="controls">
        <button type="button" onClick={run} disabled={running}>Run</button>
        <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
        <button type="button" onClick={reset}>Reset</button>
        <button type="button" onClick={download} disabled={!out}>Download sandbox output (JSON)</button>
        {running && <progress max={1} value={progress} aria-label="Sandbox progress" />}
      </div>
      <p aria-live="polite" className="sandbox-out">{msg}</p>
      {out && <SandboxResults out={out} calArm={calArm} setCalArm={setCalArm} />}
    </section>
  );
}

function mean(x: number[]) {
  return x.reduce((s, v) => s + v, 0) / x.length;
}

function SandboxResults({ out, calArm, setCalArm }: { out: SandboxOutput; calArm: string; setCalArm: (a: string) => void }) {
  const c = out.request.config;
  const end = c.window_days - 1, tTest = end + c.retention_interval_days;
  const split = 0.45;
  const xPos = (t: number) => (t <= end ? (t / end) * split : split + ((t - end) / (tTest - end)) * (1 - split));
  const arms = [...out.arms].sort((a, b) => ARM_ORDER.indexOf(a.arm) - ARM_ORDER.indexOf(b.arm));
  const base = out.arms.find((a) => a.arm === "uniform")!;
  const minY = Math.min(...arms.flatMap((a) => a.curve.map((p) => p[1])));
  const lo = Math.max(0, Math.floor(minY * 10) / 10);
  const yTicks: number[] = [];
  for (let t = lo; t <= 1.0001; t += 0.1) yTicks.push(Number(t.toFixed(1)));
  const cal = out.arms.find((a) => a.arm === calArm) ?? arms[0];
  return (
    <div className="sandbox-results">
      <h3>Sandbox forgetting curves <Label kind="sandbox" /></h3>
      <figure>
        <LineChart
          title="Sandbox: mean recall over time"
          desc={`Mean recall over items and ${out.request.learners} sandbox learners, from day 0 through the study window to the test on day ${tTest}. ${arms.map((a) => `${a}: ${f3(a.curve[a.curve.length - 1][1])} at the test`).join("; ")}.`}
          series={arms.map((a) => ({ arm: a.arm, points: a.curve }))}
          xPos={xPos}
          xTicks={[{ x: 0, label: "day 0" }, { x: Math.round(end / 2), label: `${Math.round(end / 2)}` }, { x: end, label: `${end}` }, { x: tTest, label: `test, day ${tTest}` }]}
          xLabel="days (study window on the left, retention period on the right, different scales)"
          xLabelNarrow="days (two scales: window, then retention)"
          yDomain={[lo, 1]}
          yTicks={yTicks}
          yLabel="mean recall probability"
          vline={{ x: end, label: "last session" }}
        />
        <Legend arms={arms.map((a) => a.arm)} />
        <figcaption>The saw-tooth inside the study window is recall jumping back to 1 after each review. Sandbox output, not a research result.</figcaption>
      </figure>
      <div className="table-scroll" role="region" aria-label="Sandbox summary" tabIndex={0} id="sb-table">
        <table>
          <caption>Sandbox output: mean R at the test over {out.request.learners} sandbox learners (seed {out.request.seed})</caption>
          <thead>
            <tr><th scope="col">arm</th><th scope="col">mean R</th><th scope="col">minus uniform, mean</th><th scope="col">minus uniform, lowest to highest learner</th></tr>
          </thead>
          <tbody>
            {arms.map((a) => {
              const d = a.R.map((v, i) => v - base.R[i]);
              return (
                <tr key={a.arm}>
                  <th scope="row">{a.arm}</th>
                  <td>{f3(mean(a.R))}</td>
                  <td>{a.arm === "uniform" ? "baseline" : f3(mean(d))}</td>
                  <td>{a.arm === "uniform" ? "" : `${f3(Math.min(...d))} to ${f3(Math.max(...d))}`}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="note">The range is the spread across sandbox learners, not a confidence interval.</p>
      <h3>Sandbox review calendar <Label kind="sandbox" /></h3>
      <div className="controls">
        <label>Schedule{" "}
          <select id="sb-calarm" value={cal.arm} onChange={(e) => setCalArm(e.target.value)}>
            {arms.map((a) => <option key={a.arm} value={a.arm}>{a.arm}</option>)}
          </select>
        </label>
      </div>
      <figure>
        <ItemCalendar days={end} items={c.n_items} events={cal.events} arm={cal.arm} />
        <figcaption>
          Sandbox learner 1, one row per item, one column per study day. Filled square: the item was recalled at that
          review. Outlined square: it was forgotten.
        </figcaption>
      </figure>
    </div>
  );
}
