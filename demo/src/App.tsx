// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
import { useEffect, useState } from "react";
import { Assumptions, CalendarView, ForgettingCurves, Method, Overview, PublishedResults } from "./Published";
import { loadResults, ResultsError, type Results } from "./results";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="wrap">
          <p className="kicker">MEMORY · a simulation study of review schedules</p>
          <h1>Which review schedule maximizes modelled recall under a fixed study budget?</h1>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#curves">Forgetting curves</a>
            <a href="#calendar">Calendar</a>
            <a href="#results">Results</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Playground</a>
          </nav>
          <p className="legend-key">
            Labels: <span className="lbl lbl-measured">Measured result</span> from the committed runs;{" "}
            <span className="lbl lbl-sandbox">Sandbox output</span> computed in your browser;{" "}
            <span className="lbl lbl-assumption">Assumption</span> an input, not a finding.
          </p>
        </div>
      </header>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown and the playground is disabled.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && (
          <>
            <Overview r={state.results} />
            <ForgettingCurves r={state.results} />
            <CalendarView r={state.results} />
            <PublishedResults r={state.results} />
            <Assumptions r={state.results} />
            <Method r={state.results} />
            <Sandbox scenarios={state.results.sandbox_scenarios} />
          </>
        )}
      </main>
      <footer className="site">
        <div className="wrap">
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere.
            Independent research manuscript / preprint draft, not peer-reviewed: research/paper/manuscript.md.
          </p>
        </div>
      </footer>
    </>
  );
}
