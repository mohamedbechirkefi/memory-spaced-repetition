// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
// Small UI pieces of the MEMORY brand: a segmented control with a sliding
// thumb, and a figure that inks its chart in once when scrolled into view.
import { useEffect, useRef, useState, type ReactNode } from "react";

export function Segmented<T extends string | number>(props: {
  id: string;
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}) {
  const i = Math.max(0, props.options.findIndex((o) => o.value === props.value));
  const n = props.options.length;
  return (
    <div className="seg-field">
      <span className="seg-label" id={`${props.id}-label`}>{props.label}</span>
      <div className="seg" role="group" aria-labelledby={`${props.id}-label`} id={props.id}
        style={{ gridTemplateColumns: `repeat(${n}, 1fr)` }}>
        <span className="seg-thumb" aria-hidden="true"
          style={{ width: `calc((100% - 8px) / ${n})`, transform: `translateX(${i * 100}%)` }} />
        {props.options.map((o) => (
          <button key={String(o.value)} type="button" aria-pressed={o.value === props.value}
            onClick={() => props.onChange(o.value)}>{o.label}</button>
        ))}
      </div>
    </div>
  );
}

/** A figure whose chart inks in once, the first time it enters the viewport. */
export function InkFigure({ children, className }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLElement>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") { setSeen(true); return; }
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { setSeen(true); io.disconnect(); }
    }, { threshold: 0.25 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <figure ref={ref} className={`ink-fig${seen ? " seen" : ""}${className ? " " + className : ""}`}>{children}</figure>;
}
