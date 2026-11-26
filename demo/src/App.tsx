// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
import { useEffect, useState } from "react";
import { LeitnerHero } from "./Hero";
import { Assumptions, CalendarView, ForgettingCurves, Method, Overview, PublishedResults } from "./Published";
import { loadResults, ResultsError, type Results } from "./results";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

const REPO = "https://github.com/mohamedbechirkefi/memory-spaced-repetition";
const MANUSCRIPT = `${REPO}/blob/main/research/paper/manuscript.md`;
const LABS = "https://labs.kefimohamedbechir.workers.dev";

const SECTIONS: [string, string][] = [
  ["overview", "Answer"],
  ["curves", "Curves"],
  ["calendar", "Calendar"],
  ["results", "Results"],
  ["assumptions", "Assumptions"],
  ["method", "Method"],
  ["sandbox", "Playground"],
];

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
      <header className="bar">
        <div className="bar-in">
          <a className="brand" href="#top" aria-label="Memory, back to the top">
            <img src="./brand/memory-lockup.svg" alt="" width="113" height="30" />
          </a>
          <nav aria-label="Sections">
            <ul>
              {SECTIONS.map(([id, label]) => <li key={id}><a href={`#${id}`}>{label}</a></li>)}
            </ul>
          </nav>
        </div>
      </header>
      <div className="hero" id="top">
        <div className="wrap hero-grid">
          <div className="hero-text">
            <h1>Which review schedule maximizes modelled recall under a fixed study budget?</h1>
            <p className="answer">
              Within these simulated forgetting models, no schedule is best in general: the answer depends on the
              forgetting model, the budget, the retention interval and what the scheduler knows about the learner.
            </p>
            <p className="byline">
              A simulation study by Mohamed Bechir Kefi, independent researcher. Preprint draft, not peer-reviewed.
              Simulated learners, not human participants.
            </p>
            <p className="legend-key">
              Every number carries a label: <span className="lbl lbl-measured">Measured result</span> from the
              committed runs, <span className="lbl lbl-sandbox">Sandbox output</span> computed in your browser, or{" "}
              <span className="lbl lbl-assumption">Assumption</span>, an input and not a finding.
            </p>
          </div>
          <LeitnerHero />
        </div>
      </div>
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
        <div className="wrap foot-grid">
          <div>
            <img src="./brand/memory-lockup-light.svg" alt="Memory" width="136" height="36" />
            <p>
              Mohamed Bechir Kefi, independent researcher. Independent research manuscript / preprint draft, not
              peer-reviewed.
            </p>
            <p>
              Runs offline after the first load. No data about visitors is collected, stored or sent anywhere.
            </p>
          </div>
          <div>
            <h2 className="foot-h">Links</h2>
            <ul className="foot-links">
              <li><a href={REPO}>Source repository on GitHub</a></li>
              <li><a href={MANUSCRIPT}>Manuscript (research/paper/manuscript.md)</a></li>
              <li><a href={LABS}>All lab studies</a></li>
            </ul>
          </div>
          <div>
            <h2 className="foot-h">Notes</h2>
            <p>
              Licence: MEMORY Source-Available Non-Commercial Research License, version 1.0 (see LICENSE in the
              repository).
            </p>
            <p>
              An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author.
            </p>
            <p>
              Type: Zilla Slab (Mozilla Foundation) and Alegreya Sans (Huerta Tipográfica), both under the SIL Open
              Font License, self-hosted.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
