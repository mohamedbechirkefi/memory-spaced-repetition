// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Hand-written SVG charts. Colour carries arm identity only; every line also
// has its own dash pattern and a direct label, and every chart has a table.
import { useEffect, useState, type ReactNode } from "react";

const NARROW = "(max-width: 600px)";
/** Narrow screens get a narrower drawing so that chart text stays readable. */
export function useNarrow(): boolean {
  const [n, setN] = useState(() => typeof matchMedia !== "undefined" && matchMedia(NARROW).matches);
  useEffect(() => {
    const m = matchMedia(NARROW);
    const f = () => setN(m.matches);
    m.addEventListener("change", f);
    return () => m.removeEventListener("change", f);
  }, []);
  return n;
}

export const ARM_ORDER = ["greedy", "expanding", "uniform", "leitner", "massed", "greedy-power", "greedy-exp"];
const DASH: Record<string, string> = {
  greedy: "", expanding: "7 4", uniform: "2 3", leitner: "10 3 2 3", massed: "4 2",
  "greedy-power": "", "greedy-exp": "6 2 2 2",
};
export const armVar = (arm: string) => `var(--arm-${arm})`;
export const armDash = (arm: string) => DASH[arm] ?? "";

export function Legend({ arms }: { arms: string[] }) {
  return (
    <ul className="legend" aria-label="Legend">
      {arms.map((a) => (
        <li key={a}>
          <svg width="28" height="10" aria-hidden="true">
            <line x1="1" y1="5" x2="27" y2="5" stroke={armVar(a)} strokeWidth="2.5" strokeDasharray={armDash(a)} />
          </svg>
          {a}
        </li>
      ))}
    </ul>
  );
}

interface Series {
  arm: string;
  points: [number, number][];
}

/** Spread direct labels so they never overlap (minimum gap in px). */
function spreadLabels(ys: { key: string; y: number }[], gap: number, lo: number, hi: number) {
  const s = [...ys].sort((a, b) => a.y - b.y);
  for (let i = 1; i < s.length; i++) if (s[i].y - s[i - 1].y < gap) s[i].y = s[i - 1].y + gap;
  const over = s.length ? s[s.length - 1].y - hi : 0;
  if (over > 0) s.forEach((x) => (x.y -= over));
  for (let i = s.length - 2; i >= 0; i--) if (s[i + 1].y - s[i].y < gap) s[i].y = s[i + 1].y - gap;
  s.forEach((x) => (x.y = Math.max(lo, x.y)));
  return Object.fromEntries(s.map((x) => [x.key, x.y]));
}

export interface LineChartProps {
  title: string;
  desc: string;
  series: Series[];
  /** Maps a data x to [0, 1] of the plot width. */
  xPos: (x: number) => number;
  xTicks: { x: number; label: string }[];
  xLabel: string;
  xLabelNarrow?: string;
  yDomain: [number, number];
  yTicks: number[];
  yLabel: string;
  markers?: boolean;
  bands?: ReactNode;
  pointTitle?: (arm: string, x: number, y: number) => string;
  vline?: { x: number; label: string };
}

export function LineChart(p: LineChartProps) {
  const narrow = useNarrow();
  const W = narrow ? 360 : 680, H = narrow ? 300 : 330, m = { l: 44, r: narrow ? 84 : 112, t: 14, b: 50 };
  const pw = W - m.l - m.r, ph = H - m.t - m.b;
  const X = (x: number) => m.l + p.xPos(x) * pw;
  const Y = (y: number) => m.t + (1 - (y - p.yDomain[0]) / (p.yDomain[1] - p.yDomain[0])) * ph;
  const ends = spreadLabels(
    p.series.map((s) => ({ key: s.arm, y: Y(s.points[s.points.length - 1][1]) })), 14, m.t + 4, m.t + ph,
  );
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label={`${p.title}. ${p.desc}`}>
      <title>{p.title}</title>
      <desc>{p.desc}</desc>
      {p.yTicks.map((t) => (
        <g key={t}>
          <line x1={m.l} x2={m.l + pw} y1={Y(t)} y2={Y(t)} className="grid" />
          <text x={m.l - 8} y={Y(t) + 4} textAnchor="end" className="tick">{t.toFixed(t === 0 || t === 1 ? 0 : 1)}</text>
        </g>
      ))}
      {p.xTicks.map((t) => (
        <text key={t.label} x={X(t.x)} y={m.t + ph + 18} textAnchor="middle" className="tick">{t.label}</text>
      ))}
      {p.vline && (
        <g>
          <line x1={X(p.vline.x)} x2={X(p.vline.x)} y1={m.t} y2={m.t + ph} className="vline" />
          <text x={X(p.vline.x) + 5} y={m.t + 12} className="tick">{p.vline.label}</text>
        </g>
      )}
      <line x1={m.l} x2={m.l + pw} y1={m.t + ph} y2={m.t + ph} className="axis" />
      <text x={m.l + pw / 2} y={H - 8} textAnchor="middle" className="axis-label">{narrow && p.xLabelNarrow ? p.xLabelNarrow : p.xLabel}</text>
      <text x={14} y={m.t + ph / 2} textAnchor="middle" transform={`rotate(-90 14 ${m.t + ph / 2})`} className="axis-label">{p.yLabel}</text>
      {p.bands}
      <g className="ink">
      {p.series.map((s) => (
        <g key={s.arm}>
          <polyline
            fill="none" stroke={armVar(s.arm)} strokeWidth="2.25" strokeDasharray={armDash(s.arm)}
            strokeLinejoin="round" strokeLinecap="round"
            points={s.points.map(([x, y]) => `${X(x).toFixed(1)},${Y(y).toFixed(1)}`).join(" ")}
          />
          {p.markers && s.points.map(([x, y]) => (
            <circle key={x} cx={X(x)} cy={Y(y)} r="4.5" stroke={armVar(s.arm)} className="marker">
              {p.pointTitle && <title>{p.pointTitle(s.arm, x, y)}</title>}
            </circle>
          ))}
          <text x={m.l + pw + 13} y={ends[s.arm] + 4} className="direct-label">{s.arm}</text>
        </g>
      ))}
      </g>
    </svg>
  );
}

/** Interval plot: one estimate with a 95% interval per category, with a zero line and the ±0.02 band. */
export function IntervalChart(props: {
  title: string;
  desc: string;
  rows: { label: string; est: number; lo: number; hi: number; tip: string }[];
  domain: [number, number];
}) {
  const narrow = useNarrow();
  const W = narrow ? 360 : 680, rowH = 34, m = { l: 92, r: 14, t: 12, b: 40 };
  const H = m.t + m.b + rowH * props.rows.length;
  const pw = W - m.l - m.r;
  const X = (x: number) => m.l + ((x - props.domain[0]) / (props.domain[1] - props.domain[0])) * pw;
  const ticks: number[] = [];
  const span = props.domain[1] - props.domain[0];
  const step = span > (narrow ? 0.08 : 0.12) ? (span > 0.16 && narrow ? 0.08 : 0.04) : 0.02;
  for (let t = Math.ceil(props.domain[0] / step) * step; t <= props.domain[1] + 1e-9; t += step) ticks.push(Number(t.toFixed(2)));
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label={`${props.title}. ${props.desc}`}>
      <title>{props.title}</title>
      <desc>{props.desc}</desc>
      <rect x={X(-0.02)} width={X(0.02) - X(-0.02)} y={m.t} height={rowH * props.rows.length} className="band" />
      {ticks.map((t) => (
        <g key={t}>
          <line x1={X(t)} x2={X(t)} y1={m.t} y2={m.t + rowH * props.rows.length} className={t === 0 ? "zero" : "grid"} />
          <text x={X(t)} y={H - 22} textAnchor="middle" className="tick">{t.toFixed(2)}</text>
        </g>
      ))}
      <text x={m.l + pw / 2} y={H - 4} textAnchor="middle" className="axis-label">{narrow ? "difference in R (band ±0.02)" : "difference in mean recall R (grey band: ±0.02)"}</text>
      <g className="ink">
      {props.rows.map((r, i) => {
        const y = m.t + rowH * i + rowH / 2;
        return (
          <g key={r.label}>
            <title>{r.tip}</title>
            <text x={m.l - 10} y={y + 4} textAnchor="end" className="tick">{r.label}</text>
            <line x1={X(r.lo)} x2={X(r.hi)} y1={y} y2={y} className="ci" />
            <line x1={X(r.lo)} x2={X(r.lo)} y1={y - 6} y2={y + 6} className="ci" />
            <line x1={X(r.hi)} x2={X(r.hi)} y1={y - 6} y2={y + 6} className="ci" />
            <circle cx={X(r.est)} cy={y} r="5" className="est" />
          </g>
        );
      })}
      </g>
    </svg>
  );
}

/** Day-by-arm calendar: cell shade = number of reviews that day. */
export function CalendarChart(props: { days: number[]; rows: { arm: string; loads: number[] }[]; max: number; desc: string }) {
  const narrow = useNarrow();
  const cw = narrow ? 10 : 20, rh = 30, m = { l: 80, r: 8, t: 8, b: 36 };
  const W = m.l + m.r + cw * props.days.length, H = m.t + m.b + rh * props.rows.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart plain" role="img" aria-label={`Review calendar. ${props.desc}`}>
      <title>Review calendar</title>
      <desc>{props.desc}</desc>
      <g className="ink">
      {props.rows.map((r, i) => (
        <g key={r.arm}>
          <text x={m.l - 10} y={m.t + rh * i + rh / 2 + 4} textAnchor="end" className="tick">{r.arm}</text>
          {r.loads.map((v, d) => (
            <rect key={d} x={m.l + d * cw + 1} y={m.t + rh * i + 2} width={cw - 2} height={rh - 4} rx="1"
              className={v === 0 ? "cal-empty" : "cal-cell"} style={v ? { fillOpacity: 0.18 + 0.82 * (v / props.max) } : undefined}>
              <title>{`${r.arm}, day ${props.days[d]}: ${v} reviews`}</title>
            </rect>
          ))}
        </g>
      ))}
      </g>
      {props.days.filter((d) => d === 1 || d % 5 === 0 || d === props.days.length).map((d) => (
        <text key={d} x={m.l + (d - 1) * cw + cw / 2} y={H - 18} textAnchor="middle" className="tick">{d}</text>
      ))}
      <text x={m.l + (cw * props.days.length) / 2} y={H - 2} textAnchor="middle" className="axis-label">{narrow ? "study day" : `study day (review sessions 1 to ${props.days.length})`}</text>
    </svg>
  );
}

/** Item-by-day calendar for one learner and one arm: filled = recalled, outlined = forgotten. */
export function ItemCalendar(props: { days: number; items: number; events: { session: number; item: number; success: boolean }[]; arm: string }) {
  const cw = 20, rh = 9, m = { l: 44, r: 8, t: 6, b: 34 };
  const W = m.l + m.r + cw * props.days, H = m.t + m.b + rh * props.items;
  const ok = props.events.filter((e) => e.success).length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart tall" role="img"
      aria-label={`Sandbox calendar for ${props.arm}, sandbox learner 1: ${props.events.length} reviews, ${ok} recalled, ${props.events.length - ok} forgotten.`}>
      <title>{`Sandbox review calendar, ${props.arm}`}</title>
      {Array.from({ length: props.items }, (_, i) => i).filter((i) => i % 10 === 0).map((i) => (
        <text key={i} x={m.l - 6} y={m.t + rh * i + rh - 1} textAnchor="end" className="tick small">{`item ${i + 1}`}</text>
      ))}
      {props.events.map((e, k) => (
        <rect key={k} x={m.l + (e.session - 1) * cw + 3} y={m.t + rh * e.item + 1} width={cw - 6} height={rh - 2} rx="1.5"
          fill={e.success ? armVar(props.arm) : "none"} stroke={armVar(props.arm)} strokeWidth="1.2" />
      ))}
      {Array.from({ length: props.days }, (_, d) => d + 1).filter((d) => d === 1 || d % 5 === 0 || d === props.days).map((d) => (
        <text key={d} x={m.l + (d - 1) * cw + cw / 2} y={H - 18} textAnchor="middle" className="tick">{d}</text>
      ))}
      <text x={m.l + (cw * props.days) / 2} y={H - 2} textAnchor="middle" className="axis-label">study day</text>
    </svg>
  );
}
