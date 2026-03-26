#!/usr/bin/env python3
"""Merge per-task JSON catalogs under tasks/*/test_cases.json into one file.

Writes output/consolidated_test_cases.json (multi-task bundle). Run from repo root:

  python3 scripts/consolidate_json_catalog.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        print("No tasks/ directory found.", file=sys.stderr)
        return 1

    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    merged: dict = {
        "consolidated_format": "multi_task_test_cases_json_v1",
        "tasks": [],
    }

    for path in sorted(tasks_dir.glob("*/test_cases.json")):
        try:
            catalog = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {path}: {e}", file=sys.stderr)
            return 1
        merged["tasks"].append(
            {
                "task_folder": path.parent.name,
                "source_relative": str(path.relative_to(root)),
                "catalog": catalog,
            }
        )

    out_path = out_dir / "consolidated_test_cases.json"
    out_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(merged['tasks'])} task catalog(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
