// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Hero illustration: a Leitner box sorting itself once on load, and one card's
// forgetting curve inked above it. An illustration of the mechanism only: it
// shows no study data and no number other than the box sequence.
import type { CSSProperties } from "react";

const BOX_X = (i: number) => 34 + i * 96;
const SLOT = 9;
const CARD_Y = 186;
const BOXES: [string, string][] = [["box 1", "daily"], ["box 2", "2 days"], ["box 3", "4 days"], ["box 4", "8 days"], ["box 5", "16 days"]];

interface CardSpec {
  key: string;
  box: number;
  slot: number;
  /** Start offset relative to the final place, in user units; absent for cards that stay. */
  from?: [number, number];
  delay?: number;
  missed?: boolean;
}

// Final arrangement (shown as is under reduced motion).
const CARDS: CardSpec[] = [
  { key: "a", box: 0, slot: 0 },
  { key: "e", box: 4, slot: 0 },
  { key: "b", box: 1, slot: 0, from: [-96 + SLOT, -SLOT * 0.7], delay: 0.55 },
  { key: "c", box: 2, slot: 0, from: [-96 + SLOT, -SLOT * 0.7], delay: 1.0 },
  { key: "d", box: 3, slot: 0, from: [-96, 0], delay: 1.45 },
  { key: "g", box: 0, slot: 1, from: [3 * 96, 0], delay: 1.95, missed: true },
];

function Card({ c }: { c: CardSpec }) {
  const x = BOX_X(c.box) + 14 + c.slot * SLOT, y = CARD_Y - c.slot * SLOT * 0.7;
  const style = c.from
    ? ({ "--dx": `${c.from[0]}px`, "--dy": `${c.from[1]}px`, animationDelay: `${c.delay}s` } as CSSProperties)
    : undefined;
  return (
    <g className={c.from ? `card mover${c.missed ? " missed" : ""}` : "card"} style={style}>
      <rect x={x} y={y} width="60" height="56" rx="2" className="card-body" />
      <line x1={x} x2={x + 60} y1={y + 10} y2={y + 10} className="card-red" />
      {[19, 27, 35].map((dy) => <line key={dy} x1={x + 5} x2={x + 55} y1={y + dy} y2={y + dy} className="card-rule" />)}
      {c.missed && (
        <path d={`M${x + 40} ${y + 15}l10 10m0 -10l-10 10`} className="miss-tick" style={{ animationDelay: `${c.delay}s` }} />
      )}
    </g>
  );
}

function sawtooth(): string {
  const top = 34, bottom = 112, x0 = 56, x1 = 500;
  const reviews = [x0, 118, 196, 300];
  const scales = [16, 30, 52, 110];
  const pts: string[] = [`M${x0} ${bottom}`];
  reviews.forEach((rx, i) => {
    const end = i + 1 < reviews.length ? reviews[i + 1] : x1;
    pts.push(`L${rx} ${top}`);
    for (let x = rx + 3; x <= end; x += 3) {
      const R = Math.exp(-(x - rx) / scales[i]);
      pts.push(`L${x} ${(top + (1 - R) * (bottom - top)).toFixed(1)}`);
    }
  });
  return pts.join("");
}

export function LeitnerHero() {
  return (
    <figure className="hero-art">
      <p className="illus-tag">Illustration, not study data</p>
      <svg viewBox="0 0 520 320" role="img"
        aria-label="Illustration, not study data. Above, the recall of one card falls between reviews, jumps back at each review and falls more slowly each time. Below, a Leitner box with five boxes: recalled cards move to the next box, which is reviewed less often; a forgotten card goes back to box 1.">
        <g className="sheet">
          <line x1="44" x2="44" y1="26" y2="120" className="axis" />
          <line x1="44" x2="504" y1="120" y2="120" className="axis" />
          <text x="52" y="22" className="art-label">recall of one card</text>
          <text x="504" y="138" textAnchor="end" className="art-label">time</text>
          {[56, 118, 196, 300].map((x) => <line key={x} x1={x} x2={x} y1="120" y2="128" className="review-tick" />)}
          <text x="62" y="152" className="art-label">reviews</text>
          <path d={sawtooth()} className="ink-curve" />
        </g>
        <g className="box">
          {BOXES.map((_, i) => <rect key={i} x={BOX_X(i)} y="198" width="88" height="50" className="tray-back" />)}
          {CARDS.map((c) => <Card key={c.key} c={c} />)}
          {BOXES.map(([name, every], i) => (
            <g key={name}>
              <rect x={BOX_X(i)} y="226" width="88" height="66" rx="3" className="tray-front" />
              <text x={BOX_X(i) + 44} y="256" textAnchor="middle" className="box-name">{name}</text>
              <text x={BOX_X(i) + 44} y="276" textAnchor="middle" className="box-every">{every}</text>
            </g>
          ))}
        </g>
      </svg>
      <figcaption>
        A Leitner box: a recalled card moves on to a box that is reviewed less often, and a forgotten card goes
        back to box 1. Leitner is one of the five schedules compared below.
      </figcaption>
    </figure>
  );
}
