import { useEffect, useMemo, useRef, useState } from "react";
import data from "../lib/pathway-data.json";
import {
  courseStates, doneIds, loadProgress, parseProgressFile, PROGRESS_EVENT,
  saveProgress, toYaml, type Course, type Progress,
} from "../lib/progress";

const TRACK_LABEL: Record<string, string> = {
  core: "Core", ai: "AI", systems: "Systems", security: "Security",
  elective: "Elective",
};

const CSS = `
.ocs { --line: rgba(128,128,128,.25); --card: rgba(128,128,128,.06);
  --done: #16a34a; --avail: #d97706; --accent: #3b82f6; }
.ocs * { box-sizing: border-box; }
.ocs .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px; margin: 16px 0; }
.ocs .tile { border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px;
  background: var(--card); }
.ocs .tile b { display: block; font-size: 26px; line-height: 1.2; }
.ocs .tile span { font-size: 12.5px; opacity: .75; }
.ocs .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 10px; margin: 10px 0 18px; }
.ocs .card { border: 1px solid var(--avail); border-radius: 10px; padding: 10px 12px;
  background: var(--card); text-decoration: none; color: inherit; display: block; }
.ocs .card b { font-size: 14px; }
.ocs .card small { display: block; opacity: .75; margin-top: 2px; }
.ocs details { border: 1px solid var(--line); border-radius: 10px;
  padding: 6px 12px; margin: 8px 0; }
.ocs summary { cursor: pointer; font-weight: 600; padding: 6px 0; }
.ocs .row { display: flex; align-items: center; gap: 10px; padding: 6px 4px;
  border-top: 1px solid var(--line); font-size: 14.5px; }
.ocs .row a { color: inherit; }
.ocs .row .grow { flex: 1; min-width: 0; }
.ocs .chip { font-size: 11px; border: 1px solid var(--line); border-radius: 99px;
  padding: 1px 8px; opacity: .8; white-space: nowrap; }
.ocs .state { font-size: 11.5px; white-space: nowrap; }
.ocs .state.done { color: var(--done); } .ocs .state.available { color: var(--avail); }
.ocs .state.locked { opacity: .55; }
.ocs .meter { display: grid; grid-template-columns: 46px 1fr 70px; gap: 10px;
  align-items: center; padding: 4px 0; font-size: 13px; }
.ocs .meter .bar { height: 8px; border-radius: 4px; background: var(--line);
  overflow: hidden; }
.ocs .meter .bar i { display: block; height: 100%; border-radius: 4px;
  background: var(--accent); }
.ocs .io { display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
  margin: 14px 0; }
.ocs .io button, .ocs .io label.btn { border: 1px solid var(--line); background: var(--card);
  color: inherit; border-radius: 8px; padding: 6px 12px; font-size: 13.5px;
  cursor: pointer; }
.ocs .io input[type=text] { border: 1px solid var(--line); background: transparent;
  color: inherit; border-radius: 8px; padding: 6px 10px; font-size: 13.5px; width: 150px; }
.ocs .note { font-size: 12.5px; opacity: .7; }
`;

export default function Dashboard() {
  const [progress, setProgress] = useState<Progress>(
    { learner: "", completed: [], inProgress: [], records: {},
      reviewDue: 0, reviewCounted: "" },
  );
  const fileRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const sync = () => setProgress(loadProgress());
    sync();
    window.addEventListener(PROGRESS_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(PROGRESS_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const courses = data.courses as Course[];
  const done = useMemo(() => doneIds(progress), [progress]);
  const states = useMemo(
    () => courseStates(courses, done),
    [courses, done],
  );
  const doneSet = new Set(done);
  const passedSet = new Set(Object.keys(progress.records));
  const studySet = new Set(progress.inProgress);

  const creditsDone = courses.filter((c) => doneSet.has(c.id))
    .reduce((n, c) => n + c.credits, 0);
  const coreDone = courses.filter((c) => doneSet.has(c.id) && c.track === "core")
    .reduce((n, c) => n + c.credits, 0);
  const coreTotal = courses.filter((c) => c.track === "core")
    .reduce((n, c) => n + c.credits, 0);
  const available = courses
    .filter((c) => states.get(c.id) === "available")
    .sort((a, b) => a.semester - b.semester || a.id.localeCompare(b.id));

  const bySem = new Map<number, Course[]>();
  for (const c of courses) {
    if (!bySem.has(c.semester)) bySem.set(c.semester, []);
    bySem.get(c.semester)!.push(c);
  }

  const kaRows = Object.entries(data.kaNames as Record<string, string>)
    .map(([ka, name]) => {
      const cover = courses.filter((c) => c.track === "core" && c.kas.includes(ka));
      const done = cover.filter((c) => doneSet.has(c.id)).length;
      return { ka, name, done, total: cover.length };
    });

  const update = (p: Partial<Progress>) => {
    const next = { ...progress, ...p };
    saveProgress(next);
    setProgress(next);
  };
  const toggleDone = (id: string) => {
    if (passedSet.has(id)) return; // evidence-gated — only an import changes it
    const completed = doneSet.has(id)
      ? progress.completed.filter((x) => x !== id)
      : [...progress.completed, id];
    update({ completed, inProgress: progress.inProgress.filter((x) => x !== id || !completed.includes(id)) });
  };
  const toggleStudy = (id: string) => {
    update({
      inProgress: studySet.has(id)
        ? progress.inProgress.filter((x) => x !== id)
        : [...progress.inProgress, id],
    });
  };

  const doExport = () => {
    const blob = new Blob([toYaml(progress)], { type: "text/yaml" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "progress.yaml";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  const doImport = async (file: File) => {
    const parsed = parseProgressFile(await file.text());
    if (!parsed) {
      alert("Could not parse that file as progress.yaml or JSON.");
      return;
    }
    const ids = new Set(courses.map((c) => c.id));
    const merge = (a: string[], b?: string[]) =>
      [...new Set([...a, ...(b ?? []).filter((x) => ids.has(x))])];
    const records = { ...progress.records };
    for (const [id, r] of Object.entries(parsed.records ?? {})) {
      if (ids.has(id)) records[id] = r;
    }
    update({
      learner: parsed.learner || progress.learner,
      completed: merge(progress.completed, parsed.completed)
        .filter((x) => !records[x]),
      inProgress: merge(progress.inProgress, parsed.inProgress),
      records,
      ...(parsed.isV2
        ? { reviewDue: parsed.reviewDue ?? 0,
            reviewCounted: parsed.reviewCounted ?? "" }
        : {}),
    });
  };

  return (
    <div className="ocs">
      <style>{CSS}</style>

      <div className="tiles">
        <div className="tile"><b>{creditsDone}<small style={{ fontSize: 15 }}> / {data.targetCredits}</small></b><span>credits earned</span></div>
        <div className="tile"><b>{coreDone}<small style={{ fontSize: 15 }}> / {coreTotal}</small></b><span>core credits</span></div>
        <div className="tile"><b>{passedSet.size}<small style={{ fontSize: 15 }}> / {done.length}</small></b><span>passed with evidence / done</span></div>
        <div className="tile"><b>{available.length}</b><span>available now</span></div>
        <div className="tile"><b>{progress.reviewDue}</b><span>reviews due{progress.reviewCounted ? ` (as of ${progress.reviewCounted})` : " — import your record"}</span></div>
      </div>

      <h2>Available next</h2>
      {available.length === 0 && (
        <p className="note">
          Nothing unlocked — either you are just starting (semester-1 courses
          have no prerequisites and appear here) or everything is done.
        </p>
      )}
      <div className="cards">
        {available.map((c) => (
          <a key={c.id} className="card" href={`/courses/${c.id}/`}>
            <b>{c.id}</b> <span className="chip">{TRACK_LABEL[c.track]}</span>
            <small>{c.title} · {c.credits} cr · sem {c.semester}</small>
          </a>
        ))}
      </div>

      <h2>Courses</h2>
      {[...bySem.keys()].sort((a, b) => a - b).map((s) => {
        const list = bySem.get(s)!
          .sort((a, b) => (a.track !== "core" ? 1 : 0) - (b.track !== "core" ? 1 : 0)
            || a.id.localeCompare(b.id));
        const done = list.filter((c) => doneSet.has(c.id)).length;
        return (
          <details key={s} open={done < list.length && list.some((c) => states.get(c.id) !== "locked")}>
            <summary>Semester {s} — {done}/{list.length} complete</summary>
            {list.map((c) => {
              const st = states.get(c.id)!;
              const passed = passedSet.has(c.id);
              return (
                <div className="row" key={c.id}>
                  <input
                    type="checkbox"
                    checked={doneSet.has(c.id)}
                    disabled={passed}
                    onChange={() => toggleDone(c.id)}
                    aria-label={`Mark ${c.id} complete`}
                    title={passed
                      ? `Passed ${progress.records[c.id].passedOn ?? ""} — ${progress.records[c.id].examinerReport}`
                      : "Self-reported — attach evidence by importing your record"}
                  />
                  <span className="grow">
                    <a href={`/courses/${c.id}/`}>{c.id}</a> — {c.title}
                  </span>
                  <span className="chip">{TRACK_LABEL[c.track]} · {c.credits} cr</span>
                  <span className={`state ${st}`}>
                    {st === "done"
                      ? (passed ? "✓ passed" : "☑ self-reported")
                      : st === "available" ? "◔ available" : "🔒 locked"}
                  </span>
                  <button
                    className="chip"
                    style={{ cursor: "pointer", background: "none", color: "inherit" }}
                    onClick={() => toggleStudy(c.id)}
                    title="Toggle studying"
                  >
                    {studySet.has(c.id) ? "★ studying" : "☆ study"}
                  </button>
                </div>
              );
            })}
          </details>
        );
      })}

      <h2>Knowledge-area coverage (core)</h2>
      {kaRows.map((r) => (
        <div className="meter" key={r.ka} title={r.name}>
          <b>{r.ka}</b>
          <span className="bar"><i style={{ width: `${r.total ? (r.done / r.total) * 100 : 0}%` }} /></span>
          <span>{r.done}/{r.total} courses</span>
        </div>
      ))}

      <h2>Sync</h2>
      <div className="io">
        <input
          type="text"
          placeholder="learner name"
          value={progress.learner}
          onChange={(e) => update({ learner: e.target.value })}
        />
        <button onClick={doExport}>Export progress.yaml</button>
        <label className="btn">
          Import
          <input
            ref={fileRef}
            type="file"
            accept=".yaml,.yml,.json,.txt"
            style={{ display: "none" }}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) doImport(f);
              e.target.value = "";
            }}
          />
        </label>
        <button
          onClick={() => {
            if (confirm("Clear all progress in this browser?"))
              update({ completed: [], inProgress: [], records: {},
                reviewDue: 0, reviewCounted: "" });
          }}
        >
          Reset
        </button>
        <span className="note">
          Import merges (progress only grows); a v2 record attaches examiner
          evidence — "passed" is only rendered with an examiner report. The
          private learner-state repo stays authoritative: the review queue and
          misconception log live there, not here.
        </span>
      </div>
    </div>
  );
}
