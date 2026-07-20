#!/usr/bin/env python3
"""Churn defense: check every registry URL is alive (planning/07, S9).

Classifies each source URL:
  ok        2xx/3xx
  blocked   401/403/429 — bot-blocking is not rot (Stat 110 & co. block curl)
  ROT       404/410/5xx or connection failure — the link is dead

Also warns when an entry's status_date is older than 183 days (license
re-verification due, matching validate_pathway.py's STALE_AFTER).

CI: run weekly via .github/workflows/link-check.yml — exits 1 on any ROT.
Usage:  python3 scripts/check_links.py [--offline-ok]
"""

import sys
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "resources" / "registry.yaml"
STALE_AFTER = timedelta(days=183)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def probe(url: str, hops: int = 0) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, "ok"
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location")
        if e.code in (301, 302, 303, 307, 308) and loc:
            # urllib won't follow 308; chase redirects manually. A live
            # redirect chain is not rot — only dead ends are.
            if hops < 4:
                try:
                    return probe(urllib.parse.urljoin(url, loc), hops + 1)
                except Exception:
                    return e.code, "rot"
            return e.code, "ok"
        return e.code, ("blocked" if e.code in (401, 403, 429) else "rot")
    except Exception:
        return None, "rot"


def main() -> int:
    entries = yaml.safe_load(open(REGISTRY, encoding="utf-8")) or []
    jobs = [(e["id"], e["url"]) for e in entries if e.get("url")]
    results: dict[str, tuple[int | None, str]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(probe, url): rid for rid, url in jobs}
        for f in as_completed(futs):
            results[futs[f]] = f.result()

    rot, blocked = [], 0
    for rid, url in jobs:
        code, cls = results[rid]
        if cls == "blocked":
            blocked += 1
        elif cls == "rot":
            rot.append((rid, code, url))

    today = date.today()
    stale = [e["id"] for e in entries
             if e.get("status_date") and (today - e["status_date"]) > STALE_AFTER]

    print(f"checked {len(jobs)} urls: "
          f"{len(jobs) - len(rot) - blocked} ok, {blocked} bot-blocked, {len(rot)} ROT")
    for rid, code, url in rot:
        print(f"ROT: {rid} [{code}] {url}")
    if stale:
        print(f"re-verification due ({len(stale)}): " + ", ".join(sorted(stale)))
    return 1 if rot else 0


if __name__ == "__main__":
    sys.exit(main())
