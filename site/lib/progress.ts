// Shared progress model for the Dashboard and PathwayMap islands.
// State lives in localStorage; export/import round-trips progress.yaml
// (see planning/05-frontend-plan.md — progress never enters this repo).
//
// v2 added study activity (`activity`, `started` — streak + pace).
// v3 adds per-unit mastery: `mastery` maps "<COURSE>/<unit#>" to a level
// 0–3 (MASTERY_LABELS). /teach writes levels into progress.yaml after
// quizzes; the dashboard merges them (max wins). All v1/v2 exports import
// cleanly — new fields just default.

export type MasteryMap = Record<string, number>;

export const MASTERY_LABELS = [
  "unfamiliar", "familiar", "proficient", "mastered",
] as const;

export type Progress = {
  learner: string;
  completed: string[];
  inProgress: string[];
  activity: string[]; // ISO dates, unique
  started: string; // ISO date of first activity, "" until then
  mastery: MasteryMap;
};

export type CourseState = "done" | "available" | "locked";

export type Course = {
  id: string;
  title: string;
  semester: number;
  credits: number;
  track: string;
  kas: string[];
  prereqs: string[];
  lecture?: { title: string; url: string }[];
  units?: string[];
  concepts?: number;
};

const KEY = "openCS.progress.v1";
export const PROGRESS_EVENT = "opencs-progress";

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

const EMPTY: Progress = {
  learner: "", completed: [], inProgress: [], activity: [], started: "",
  mastery: {},
};

export function loadProgress(): Progress {
  if (typeof localStorage === "undefined") return EMPTY;
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return {
      learner: typeof raw.learner === "string" ? raw.learner : "",
      completed: Array.isArray(raw.completed) ? raw.completed : [],
      inProgress: Array.isArray(raw.inProgress) ? raw.inProgress : [],
      activity: Array.isArray(raw.activity) ? raw.activity : [],
      started: typeof raw.started === "string" ? raw.started : "",
      mastery: raw.mastery && typeof raw.mastery === "object" ? raw.mastery : {},
    };
  } catch {
    return EMPTY;
  }
}

export function saveProgress(p: Progress): void {
  localStorage.setItem(KEY, JSON.stringify(p));
  window.dispatchEvent(new Event(PROGRESS_EVENT));
}

// Stamp today as a study day (and set `started` on first use).
// Returns a new Progress; caller decides whether to merge more changes.
export function logActivity(p: Progress): Progress {
  const today = todayISO();
  return {
    ...p,
    activity: p.activity.includes(today) ? p.activity : [...p.activity, today],
    started: p.started || today,
  };
}

// Merge two mastery maps, keeping the higher level per unit.
export function mergeMastery(a: MasteryMap, b: MasteryMap): MasteryMap {
  const out: MasteryMap = { ...a };
  for (const [k, v] of Object.entries(b)) {
    out[k] = Math.max(out[k] ?? 0, v);
  }
  return out;
}

export function courseStates(
  courses: Course[],
  completed: string[],
): Map<string, CourseState> {
  const done = new Set(completed);
  const states = new Map<string, CourseState>();
  for (const c of courses) {
    if (done.has(c.id)) states.set(c.id, "done");
    else if (c.prereqs.every((p) => done.has(p))) states.set(c.id, "available");
    else states.set(c.id, "locked");
  }
  return states;
}

// Current consecutive-day study streak ending today (or yesterday).
export function currentStreak(activity: string[]): number {
  const days = new Set(activity);
  let streak = 0;
  const d = new Date();
  if (!days.has(d.toISOString().slice(0, 10))) d.setDate(d.getDate() - 1);
  while (days.has(d.toISOString().slice(0, 10))) {
    streak += 1;
    d.setDate(d.getDate() - 1);
  }
  return streak;
}

export function toYaml(p: Progress): string {
  const list = (xs: string[]) => (xs.length ? `[${xs.join(", ")}]` : "[]");
  const mastery = Object.keys(p.mastery).length
    ? JSON.stringify(p.mastery, Object.keys(p.mastery).sort())
    : "{}";
  return [
    `learner: ${p.learner || "anonymous"}`,
    `updated: ${todayISO()}`,
    `started: ${p.started || ""}`,
    `completed_courses: ${list([...p.completed].sort())}`,
    `in_progress: ${list([...p.inProgress].sort())}`,
    `activity: ${list([...p.activity].sort())}`,
    `mastery: ${mastery}`,
    "",
  ].join("\n");
}

// Accepts progress.yaml (inline or block lists) or a JSON export.
export function parseProgressFile(text: string): Partial<Progress> | null {
  try {
    const j = JSON.parse(text);
    if (j && (j.completed || j.completed_courses)) {
      return {
        learner: j.learner,
        completed: j.completed ?? j.completed_courses ?? [],
        inProgress: j.inProgress ?? j.in_progress ?? [],
        activity: j.activity ?? [],
        started: j.started ?? "",
        mastery: j.mastery && typeof j.mastery === "object" ? j.mastery : {},
      };
    }
  } catch {
    /* not JSON — try YAML subset */
  }
  const grab = (key: string): string[] | null => {
    const inline = text.match(new RegExp(`^${key}:\\s*\\[([^\\]]*)\\]`, "m"));
    if (inline)
      return inline[1].split(",").map((s) => s.trim()).filter(Boolean);
    const block = text.match(
      new RegExp(`^${key}:\\s*\\n((?:\\s+-\\s+.+\\n?)+)`, "m"),
    );
    if (block)
      return block[1].split("\n").map((l) => l.replace(/^\s+-\s+/, "").trim())
        .filter(Boolean);
    if (new RegExp(`^${key}:`, "m").test(text)) return [];
    return null;
  };
  const completed = grab("completed_courses");
  if (completed === null) return null;
  const learner = text.match(/^learner:\s*(.+)$/m)?.[1]?.trim();
  const started = text.match(/^started:\s*(\S+)/m)?.[1]?.trim() ?? "";
  let mastery: MasteryMap = {};
  const mline = text.match(/^mastery:\s*(\{.*\})\s*$/m);
  if (mline) {
    try {
      mastery = JSON.parse(mline[1]);
    } catch {
      /* malformed mastery — ignore */
    }
  }
  return {
    learner,
    started,
    completed,
    inProgress: grab("in_progress") ?? [],
    activity: grab("activity") ?? [],
    mastery,
  };
}
