import { useEffect, useMemo, useRef, useState } from "react";
import data from "../lib/pathway-data.json";
import {
  courseStates, currentStreak, loadProgress, logActivity, MASTERY_LABELS,
  mergeMastery, parseProgressFile, PROGRESS_EVENT, saveProgress, todayISO,
  toYaml, type Course, type Progress,
} from "../lib/progress";

const TRACK_LABEL: Record<string, string> = {
  core: "Core", ai: "AI", systems: "Systems", security: "Security",
  elective: "Elective",
};

const MASTERY_DOTS = ["○", "◔", "◑", "●"];

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
.ocs .focus { border: 1px solid var(--accent); border-radius: 12px; padding: 14px 16px;
  background: var(--card); margin: 10px 0 18px; }
.ocs .focus h3 { margin: 0 0 4px; font-size: 17px; }
.ocs .focus .links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.ocs .focus .links a { border: 1px solid var(--line); border-radius: 8px;
  padding: 4px 10px; font-size: 13px; text-decoration: none; color: inherit;
  background: rgba(128,128,128,.04); }
.ocs .focus .links a.primary { border-color: var(--accent); font-weight: 600; }
.ocs .focus .others { margin-top: 8px; font-size: 13px; opacity: .8; }
.ocs .heatwrap { display: flex; align-items: flex-end; gap: 14px; margin: 10px 0 4px;
  flex-wrap: wrap; }
.ocs .heat { display: grid; grid-template-rows: repeat(7, 11px);
  grid-auto-flow: column; gap: 3px; }
.ocs .heat i { width: 11px; height: 11px; border-radius: 2.5px;
  background: var(--card); border: 1px solid var(--line); }
.ocs .heat i.on { background: var(--done); border-color: var(--done); }
.ocs .heatstats b { font-size: 22px; }
.ocs .heatstats span { font-size: 12.5px; opacity: .75; display: block; }
.ocs details { border: 1px solid var(--line); border-radius: 10px;
  padding: 6px 12px; margin: 8px 0; }
.ocs summary { cursor: pointer; font-weight: 600; padding: 6px 0; }
.ocs .row { display: flex; align-items: center; gap: 10px; padding: 6px 4px;
  border-top: 1px solid var(--line); font-size: 14.5px; }
.ocs .row a { color: inherit; }
.ocs .row .grow { flex: 1; min-width: 0; }
.ocs .chip { font-size: 11px; border: 1px solid var(--line); border-radius: 99px;
  padding: 1px 8px; opacity: .8; white-space: nowrap; }
.ocs .chip.ready { color: var(--done); border-color: var(--done); opacity: 1; }
.ocs .state { font-size: 11.5px; white-space: nowrap; }
.ocs .state.done { color: var(--done); } .ocs .state.available { color: var(--avail); }
.ocs .state.locked { opacity: .55; }
.ocs .units { border-top: 1px solid var(--line); padding: 4px 4px 8px 30px; }
.ocs .urow { display: flex; align-items: center; gap: 10px; padding: 3px 0;
  font-size: 13.5px; }
.ocs .urow .udot { border: none; background: none; color: inherit; cursor: pointer;
  font-size: 15px; width: 26px; text-align: center; padding: 0; }
.ocs .urow .udot.l2, .ocs .urow .udot.l3 { color: var(--done); }
.ocs .urow .ulabel { opacity: .85; }
.ocs .urow .ulevel { font-size: 11px; opacity: .6; }
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

const DAY = 24 * 60 * 60 * 1000;

function lastDays(n: number): string[] {
  const out: string[] = [];
  const d = new Date();
  for (let i = n - 1; i >= 0; i--) {
    out.push(new Date(d.getTime() - i * DAY).toISOString().slice(0, 10));
  }
  return out;
}

function fmtMonthYear(d: Date): string {
  return d.toLocaleDateString(undefined, { month: "short", year: "numeric" });
}

export default function Dashboard() {
  const [progress, setProgress] = useState<Progress>({
    learner: "", completed: [], inProgress: [], activity: [], started: "",
    mastery: {},
  });
  const [unitsOpen, setUnitsOpen] = useState<Record<string, boolean>>({});
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
  const states = useMemo(
    () => courseStates(courses, progress.completed),
    [courses, progress.completed],
  );
  const doneSet = new Set(progress.completed);
  const studySet = new Set(progress.inProgress);
  const activitySet = new Set(progress.activity);

  const creditsDone = courses.filter((c) => doneSet.has(c.id))
    .reduce((n, c) => n + c.credits, 0);
  const coreDone = courses.filter((c) => doneSet.has(c.id) && c.track === "core")
    .reduce((n, c) => n + c.credits, 0);
  const coreTotal = courses.filter((c) => c.track === "core")
    .reduce((n, c) => n + c.credits, 0);
  const available = courses
    .filter((c) => states.get(c.id) === "available")
    .sort((a, b) => a.semester - b.semester || a.id.localeCompare(b.id));

  // Today widget: first studying course, else first available.
  const studying = courses.filter((c) => studySet.has(c.id));
  const focus: Course | undefined = studying[0] ?? available[0];

  // Pace projection from first study day.
  const pace = useMemo(() => {
    if (!progress.started || creditsDone === 0) return null;
    const elapsedDays = Math.max(
      7, (Date.now() - new Date(progress.started + "T00:00:00").getTime()) / DAY,
    );
    const perWeek = creditsDone / (elapsedDays / 7);
    const remaining = (data.targetCredits as number) - creditsDone;
    const eta = new Date(Date.now() + (remaining / perWeek) * 7 * DAY);
    return { perWeek, eta };
  }, [progress.started, creditsDone]);

  const streak = useMemo(() => currentStreak(progress.activity), [progress.activity]);
  const heatDays = useMemo(() => lastDays(19 * 7), []);

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
  const stamp = () => logActivity(progress);
  const toggleDone = (id: string) => {
    const completed = doneSet.has(id)
      ? progress.completed.filter((x) => x !== id)
      : [...progress.completed, id];
    const s = stamp();
    update({
      completed,
      inProgress: progress.inProgress.filter((x) => x !== id || !completed.includes(id)),
      activity: s.activity,
      started: s.started,
    });
  };
  const toggleStudy = (id: string) => {
    const s = stamp();
    update({
      inProgress: studySet.has(id)
        ? progress.inProgress.filter((x) => x !== id)
        : [...progress.inProgress, id],
      activity: s.activity,
      started: s.started,
    });
  };
  const logToday = () => update(logActivity(progress));

  const levelOf = (cid: string, i: number) =>
    progress.mastery[`${cid}/${i + 1}`] ?? 0;
  const cycleMastery = (cid: string, i: number) => {
    const k = `${cid}/${i + 1}`;
    const s = stamp();
    update({
      mastery: { ...progress.mastery, [k]: (levelOf(cid, i) + 1) % 4 },
      activity: s.activity,
      started: s.started,
    });
  };
  const unitsReady = (c: Course) =>
    (c.units ?? []).length > 0 &&
    (c.units ?? []).every((_, i) => levelOf(c.id, i) >= 2) &&
    !doneSet.has(c.id);

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
      [...new Set([...a, ...(b ?? []).filter((x) => ids.has(x) || /^\d{4}-\d{2}-\d{2}$/.test(x))])];
    update({
      learner: parsed.learner || progress.learner,
      completed: merge(progress.completed, parsed.completed),
      inProgress: merge(progress.inProgress, parsed.inProgress),
      activity: merge(progress.activity, parsed.activity).sort(),
      started: [progress.started, parsed.started ?? ""].filter(Boolean).sort()[0] ?? "",
      mastery: mergeMastery(parsed.mastery ?? {}, progress.mastery),
    });
  };

  return (
    <div className="ocs">
      <style>{CSS}</style>

      <h2>Today</h2>
      {focus ? (
        <div className="focus">
          <h3>
            {studySet.has(focus.id) ? "Continue" : "Start"}: {focus.id} — {focus.title}
          </h3>
          <span className="chip">
            {TRACK_LABEL[focus.track]} · {focus.credits} cr · sem {focus.semester}
          </span>{" "}
          <span className="chip">
            {(focus.concepts ?? 0) > 0
              ? `${focus.concepts} concept doc${(focus.concepts ?? 0) > 1 ? "s" : ""}`
              : "concept docs pending"}
          </span>
          <div className="links">
            <a className="primary" href={`/courses/${focus.id}/`}>Open course page</a>
            {(focus.lecture ?? []).map((l) => (
              <a key={l.url} href={l.url} target="_blank" rel="noreferrer">
                ▶ {l.title}
              </a>
            ))}
          </div>
          {studying.length > 1 && (
            <div className="others">
              Also studying: {studying.slice(1).map((c) => c.id).join(", ")}
            </div>
          )}
        </div>
      ) : (
        <p className="note">Nothing available yet — check the pathway map.</p>
      )}

      <h2>Study streak</h2>
      <div className="heatwrap">
        <div className="heat">
          {heatDays.map((d) => (
            <i key={d} className={activitySet.has(d) ? "on" : ""} title={d} />
          ))}
        </div>
        <div className="heatstats">
          <b>{streak}</b><span>day streak</span>
        </div>
        <div className="heatstats">
          <b>{progress.activity.length}</b><span>study days total</span>
        </div>
        <button className="chip" style={{ cursor: "pointer", background: "none", color: "inherit" }}
          onClick={logToday} disabled={activitySet.has(todayISO())}>
          {activitySet.has(todayISO()) ? "✓ logged today" : "+ Log study today"}
        </button>
      </div>
      <p className="note">
        One click per study day keeps the streak honest. The last 19 weeks are shown.
      </p>

      <div className="tiles">
        <div className="tile"><b>{creditsDone}<small style={{ fontSize: 15 }}> / {data.targetCredits}</small></b><span>credits earned</span></div>
        <div className="tile"><b>{coreDone}<small style={{ fontSize: 15 }}> / {coreTotal}</small></b><span>core credits</span></div>
        <div className="tile"><b>{progress.completed.length}<small style={{ fontSize: 15 }}> / {courses.length}</small></b><span>courses completed</span></div>
        <div className="tile">
          <b>{courses.reduce((n, c) => n + (c.concepts ?? 0), 0)}
            <small style={{ fontSize: 15 }}> / {courses.reduce((n, c) => n + (c.units ?? []).length, 0)}</small></b>
          <span>concept docs authored</span>
        </div>
        <div className="tile">
          {pace
            ? <><b>{pace.perWeek.toFixed(1)}<small style={{ fontSize: 15 }}> cr/wk</small></b><span>pace → degree ETA {fmtMonthYear(pace.eta)}</span></>
            : <><b>—</b><span>complete a course to get a pace reading</span></>}
        </div>
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
              const units = c.units ?? [];
              return (
                <div key={c.id}>
                  <div className="row">
                    <input
                      type="checkbox"
                      checked={doneSet.has(c.id)}
                      onChange={() => toggleDone(c.id)}
                      aria-label={`Mark ${c.id} complete`}
                    />
                    <span className="grow">
                      <a href={`/courses/${c.id}/`}>{c.id}</a> — {c.title}
                    </span>
                    {unitsReady(c) && <span className="chip ready">units ready — mark complete?</span>}
                    <span className="chip">{TRACK_LABEL[c.track]} · {c.credits} cr</span>
                    <span className={`state ${st}`}>
                      {st === "done" ? "✓ done" : st === "available" ? "◔ available" : "🔒 locked"}
                    </span>
                    {units.length > 0 && (
                      <button
                        className="chip"
                        style={{ cursor: "pointer", background: "none", color: "inherit" }}
                        onClick={() =>
                          setUnitsOpen({ ...unitsOpen, [c.id]: !unitsOpen[c.id] })}
                      >
                        {unitsOpen[c.id] ? "▾ units" : `▸ ${c.concepts ?? 0}/${units.length} docs`}
                      </button>
                    )}
                    <button
                      className="chip"
                      style={{ cursor: "pointer", background: "none", color: "inherit" }}
                      onClick={() => toggleStudy(c.id)}
                      title="Toggle studying"
                    >
                      {studySet.has(c.id) ? "★ studying" : "☆ study"}
                    </button>
                  </div>
                  {unitsOpen[c.id] && units.length > 0 && (
                    <div className="units">
                      {units.map((u, i) => {
                        const lvl = levelOf(c.id, i);
                        return (
                          <div className="urow" key={i}>
                            <button
                              className={`udot l${lvl}`}
                              onClick={() => cycleMastery(c.id, i)}
                              title={`${MASTERY_LABELS[lvl]} — click to advance`}
                            >
                              {MASTERY_DOTS[lvl]}
                            </button>
                            <span className="ulabel">{i + 1}. {u}</span>
                            <span className="ulevel">{MASTERY_LABELS[lvl]}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </details>
        );
      })}
      <p className="note">
        Unit dots cycle ○ unfamiliar → ◔ familiar → ◑ proficient → ● mastered.
        A course is ready to complete when every unit is ◑ or better; /teach
        sets levels via progress.yaml after quizzes.
      </p>

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
              update({ completed: [], inProgress: [], activity: [], started: "", mastery: {} });
          }}
        >
          Reset
        </button>
        <span className="note">
          Import merges (progress only grows). Keep the export in your private
          learner-state repo.
        </span>
      </div>
    </div>
  );
}
