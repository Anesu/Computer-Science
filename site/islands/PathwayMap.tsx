import { useEffect, useRef, useState } from "react";
import data from "../lib/pathway-data.json";
import {
  courseStates, loadProgress, PROGRESS_EVENT, type Course,
} from "../lib/progress";

const LEGEND = [
  { cls: "pw-done", label: "✓ Completed", color: "#16a34a" },
  { cls: "pw-avail", label: "◔ Available", color: "#d97706" },
  { cls: "pw-locked", label: "🔒 Locked", color: "#94a3b8" },
];

export default function PathwayMap() {
  const host = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    fetch("/pathway.svg")
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(`${r.status}`))))
      .then(setSvg)
      .catch((e) => setErr(String(e)));
  }, []);

  useEffect(() => {
    if (!svg || !host.current) return;
    const apply = () => {
      const states = courseStates(
        data.courses as Course[], loadProgress().completed,
      );
      for (const g of host.current!.querySelectorAll<SVGGElement>(".pw-course")) {
        const id = g.dataset.course!;
        g.classList.remove("pw-done", "pw-avail", "pw-locked");
        const st = states.get(id);
        if (st === "done") g.classList.add("pw-done");
        else if (st === "available") g.classList.add("pw-avail");
        else g.classList.add("pw-locked");
      }
    };
    apply();
    window.addEventListener(PROGRESS_EVENT, apply);
    window.addEventListener("storage", apply);
    return () => {
      window.removeEventListener(PROGRESS_EVENT, apply);
      window.removeEventListener("storage", apply);
    };
  }, [svg]);

  return (
    <div>
      <div style={{
        display: "flex", gap: 16, flexWrap: "wrap", margin: "10px 0",
        fontSize: 13.5,
      }}>
        {LEGEND.map((l) => (
          <span key={l.cls} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <i style={{
              width: 14, height: 14, borderRadius: 4, display: "inline-block",
              border: `3px solid ${l.color}`,
              opacity: l.cls === "pw-locked" ? 0.4 : 1,
            }} />
            {l.label}
          </span>
        ))}
      </div>
      {err && (
        <p style={{ opacity: 0.7 }}>
          Could not load the map (/pathway.svg): {err}
        </p>
      )}
      <div
        ref={host}
        style={{ maxHeight: "80vh", overflow: "auto", border: "1px solid rgba(128,128,128,.25)", borderRadius: 10 }}
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </div>
  );
}
