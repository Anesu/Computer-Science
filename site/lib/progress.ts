// Shared progress model for the Dashboard and PathwayMap islands.
// State lives in localStorage; export/import round-trips the learning
// record (schemas/learning-record.md — the record never enters this repo).
//
// Two record formats are accepted on import:
//   v1 — flat checkbox lists (completed_courses / in_progress)
//   v2 — evidence-linked: courses.<ID>.status with examiner_report paths
// The dashboard is a *viewer* of the record, not its home: the private
// learner-state repo is authoritative, and the review queue / misconception
// log live only there (v2 export carries course state, not the queues).

export type CourseEvidence = {
  status: "passed";
  examinerReport: string;
  passedOn?: string;
  project?: string;
};

export type Progress = {
  learner: string;
  completed: string[];   // self-reported checkboxes (no evidence attached)
  inProgress: string[];
  records: Record<string, CourseEvidence>; // evidence-gated, import-only
  reviewDue: number;     // due review_queue items counted at last import
  reviewCounted: string; // ISO date of that count ("" = never imported)
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
  assessment?: {
    core: number;
    supporting: number;
    aiModes: string[];
    stub: boolean;
  } | null;
};

const KEY = "openCS.progress.v1";
export const PROGRESS_EVENT = "opencs-progress";

const EMPTY: Progress = {
  learner: "", completed: [], inProgress: [], records: {},
  reviewDue: 0, reviewCounted: "",
};

export function loadProgress(): Progress {
  if (typeof localStorage === "undefined") return { ...EMPTY };
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return {
      learner: typeof raw.learner === "string" ? raw.learner : "",
      completed: Array.isArray(raw.completed) ? raw.completed : [],
      inProgress: Array.isArray(raw.inProgress) ? raw.inProgress : [],
      records: raw.records && typeof raw.records === "object" ? raw.records : {},
      reviewDue: typeof raw.reviewDue === "number" ? raw.reviewDue : 0,
      reviewCounted: typeof raw.reviewCounted === "string" ? raw.reviewCounted : "",
    };
  } catch {
    return { ...EMPTY };
  }
}

export function saveProgress(p: Progress): void {
  localStorage.setItem(KEY, JSON.stringify(p));
  window.dispatchEvent(new Event(PROGRESS_EVENT));
}

// Everything that counts as "done" for prerequisite purposes: evidence-gated
// passes plus self-reported checkboxes. The gate is soft by design (the DAG
// is advice, not law) — the *rendering* distinguishes passed from
// self-reported, the frontier does not.
export function doneIds(p: Progress): string[] {
  return [...new Set([...p.completed, ...Object.keys(p.records)])];
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
  const lines = [
    "version: 2",
    `learner: ${p.learner || "anonymous"}`,
    `updated: ${new Date().toISOString().slice(0, 10)}`,
    "# Exported by the dashboard — course state only. The review queue and",
    "# misconception log live in your records repo and are not round-tripped.",
    "courses:",
  ];
  const ids = [...new Set([...doneIds(p), ...p.inProgress])].sort();
  for (const id of ids) {
    const r = p.records[id];
    if (r) {
      lines.push(`  ${id}:`);
      lines.push("    status: passed");
      if (r.passedOn) lines.push(`    passed_on: ${r.passedOn}`);
      lines.push(`    examiner_report: ${r.examinerReport}`);
      if (r.project) lines.push(`    project: ${r.project}`);
    } else if (p.completed.includes(id)) {
      lines.push(`  ${id}:`);
      lines.push("    status: self-reported");
    } else {
      lines.push(`  ${id}:`);
      lines.push("    status: in-progress");
    }
  }
  if (!ids.length) lines.push("  {}");
  lines.push("");
  return lines.join("\n");
}

export type ParsedRecord = Partial<Progress> & { isV2?: boolean };

// v2 records: a small indentation-based reader for the canonical layout
// written by tooling (two-space course keys, four-space fields, inline-map
// review_queue entries). Agents read the record with a real YAML parser;
// only the browser import is this constrained.
function parseRecordV2(text: string): ParsedRecord | null {
  if (!/^version:\s*2\s*$/m.test(text)) return null;
  const learner = text.match(/^learner:\s*(.+)$/m)?.[1]?.trim();
  const records: Record<string, CourseEvidence> = {};
  const completed: string[] = [];
  const inProgress: string[] = [];

  const coursesSec = text.match(/^courses:\s*\n((?:(?: {2,}.*)?\n?)*?)(?=^\S|\s*$(?![\s\S]))/m);
  if (coursesSec) {
    let current: string | null = null;
    let fields: Record<string, string> = {};
    const finish = () => {
      if (!current) return;
      const status = fields["status"];
      if (status === "passed" && fields["examiner_report"]) {
        records[current] = {
          status: "passed",
          examinerReport: fields["examiner_report"],
          passedOn: fields["passed_on"],
          project: fields["project"],
        };
      } else if (status === "passed" || status === "self-reported") {
        completed.push(current); // passed without evidence downgrades
      } else if (status === "in-progress") {
        inProgress.push(current);
      }
      fields = {};
    };
    for (const line of coursesSec[1].split("\n")) {
      const key = line.match(/^ {2}([A-Za-z][\w-]*):\s*$/);
      const field = line.match(/^ {4}([\w]+):\s*(.+?)\s*$/);
      if (key) {
        finish();
        current = key[1];
      } else if (field && current) {
        fields[field[1]] = field[2];
      }
    }
    finish();
  }

  const today = new Date().toISOString().slice(0, 10);
  let reviewDue = 0;
  const queueSec = text.match(/^review_queue:\s*\n((?:\s+-.*\n?)*)/m);
  if (queueSec) {
    for (const m of queueSec[1].matchAll(/due:\s*['"]?(\d{4}-\d{2}-\d{2})/g)) {
      if (m[1] <= today) reviewDue += 1;
    }
  }
  return {
    isV2: true, learner, completed, inProgress, records,
    reviewDue, reviewCounted: today,
  };
}

// Accepts a v2 record, a v1 progress.yaml (inline or block lists), or a
// JSON export of either.
export function parseProgressFile(text: string): ParsedRecord | null {
  try {
    const j = JSON.parse(text);
    if (j && (j.completed || j.completed_courses)) {
      return {
        learner: j.learner,
        completed: j.completed ?? j.completed_courses ?? [],
        inProgress: j.inProgress ?? j.in_progress ?? [],
        records: j.records && typeof j.records === "object" ? j.records : {},
      };
    }
  } catch {
    /* not JSON — try YAML */
  }
  const v2 = parseRecordV2(text);
  if (v2) return v2;
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
