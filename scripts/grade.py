#!/usr/bin/env python3
"""Run the exercise checks for one course unit (check50-style, zero deps).

Checks live in assess/<COURSE>/<NN>-<slug>/test_unit.py as plain test_*
functions with asserts; the learner fills in exercises.py in the same
folder. No pytest required — the runner is stdlib-only and the test files
stay pytest-compatible if you want the bigger tool later.

Usage:  python3 scripts/grade.py CS1101 01
Exit:   0 when every check passes, 1 otherwise, 2 on usage/setup error.
"""

import importlib.util
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    course, unit = sys.argv[1].upper(), sys.argv[2].zfill(2)
    base = ROOT / "assess" / course
    matches = sorted(base.glob(f"{unit}-*")) if base.exists() else []
    if not matches:
        print(f"no assessment for {course} unit {unit} (looked in {base})")
        return 2
    udir = matches[0]
    if not (udir / "test_unit.py").exists():
        print(f"{udir}: test_unit.py missing")
        return 2
    if not (udir / "exercises.py").exists():
        print(f"{udir}: exercises.py missing — create it and fill the stubs")
        return 2

    sys.path.insert(0, str(udir))
    try:
        tests = load_module("test_unit", udir / "test_unit.py")
    except Exception:
        print(f"could not load {udir / 'test_unit.py'}:")
        traceback.print_exc()
        return 2

    fns = sorted(
        (getattr(tests, n) for n in dir(tests) if n.startswith("test_")),
        key=lambda f: f.__name__,
    )
    fns = [f for f in fns if callable(f)]
    if not fns:
        print(f"{udir}: no test_* functions found")
        return 2

    print(f"{course} unit {unit} — {len(fns)} checks\n")
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"[ok]   {fn.__name__}")
            passed += 1
        except NotImplementedError:
            print(f"[FAIL] {fn.__name__}: not implemented yet")
        except AssertionError as e:
            print(f"[FAIL] {fn.__name__}: {e or 'assertion failed'}")
        except Exception as e:
            print(f"[FAIL] {fn.__name__}: {type(e).__name__}: {e}")

    print(f"\n{passed}/{len(fns)} checks passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    sys.exit(main())
