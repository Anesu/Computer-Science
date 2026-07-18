// Shared progress model for the Dashboard and PathwayMap islands.
// State lives in localStorage; export/import round-trips progress.yaml
// (see planning/05-frontend-plan.md — progress never enters this repo).

export type Progress = {
  learner: string;
  completed: string[];
  inProgress: string[];
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
};

const KEY = "openCS.progress.v1";
export const PROGRESS_EVENT = "opencs-progress";

export function loadProgress(): Progress {
  if (typeof localStorage === "undefined")
    return { learner: "", completed: [], inProgress: [] };
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return {
      learner: typeof raw.learner === "string" ? raw.learner : "",
      completed: Array.isArray(raw.completed) ? raw.completed : [],
      inProgress: Array.isArray(raw.inProgress) ? raw.inProgress : [],
    };
  } catch {
    return { learner: "", completed: [], inProgress: [] };
  }
}

export function saveProgress(p: Progress): void {
  localStorage.setItem(KEY, JSON.stringify(p));
  window.dispatchEvent(new Event(PROGRESS_EVENT));
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

export function toYaml(p: Progress): string {
  const list = (xs: string[]) => (xs.length ? `[${xs.join(", ")}]` : "[]");
  return [
    `learner: ${p.learner || "anonymous"}`,
    `updated: ${new Date().toISOString().slice(0, 10)}`,
    `completed_courses: ${list([...p.completed].sort())}`,
    `in_progress: ${list([...p.inProgress].sort())}`,
    "completed_concepts: []",
    "quiz_scores: {}",
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
  return {
    learner,
    completed,
    inProgress: grab("in_progress") ?? [],
  };
}
