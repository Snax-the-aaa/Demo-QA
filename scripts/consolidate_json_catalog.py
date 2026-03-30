#!/usr/bin/env python3
"""Merge tasks/*/test_cases.json into repo-root test_cases.json.

Run from repo root: python3 scripts/consolidate_json_catalog.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        print("No tasks/ directory.", file=sys.stderr)
        return 1

    sources: list[str] = []
    all_cases: list[dict] = []
    deprecated: list[dict] = []
    prereq: list[str] = []
    no_auth_blocks: list[str] = []
    jira_meta: list[dict] = []

    for task_json in sorted(tasks_dir.glob("*/test_cases.json")):
        rel = str(task_json.relative_to(root)).replace("\\", "/")
        data = _load(task_json)
        sources.append(rel)

        jira_meta.append(
            {
                "source_file": rel,
                "jira_key": data.get("jira_key"),
                "title": data.get("title"),
                "task_folder": data.get("task_folder")
                or task_json.parent.name,
            }
        )

        for p in data.get("prerequisites") or []:
            if isinstance(p, str):
                prereq.append(p)

        na = data.get("no_authentication_scope")
        if isinstance(na, str) and na.strip():
            no_auth_blocks.append(na.strip())

        folder = data.get("task_folder") or task_json.parent.name
        for tc in data.get("test_cases") or []:
            if not isinstance(tc, dict):
                continue
            row = dict(tc)
            row.setdefault("source_task_folder", folder)
            row.setdefault("source_file", rel)
            all_cases.append(row)

        for d in data.get("deprecated_test_cases") or []:
            if isinstance(d, dict):
                deprecated.append({**d, "source_file": rel})

    ids = {}
    for i, tc in enumerate(all_cases):
        tid = tc.get("id")
        if not tid:
            print(f"Case missing id at index {i}", file=sys.stderr)
            return 1
        if tid in ids:
            print(f"Duplicate test case id: {tid}", file=sys.stderr)
            return 1
        ids[tid] = True

    no_auth_merged = (
        no_auth_blocks[0]
        if len(no_auth_blocks) == 1
        else (
            "\n\n---\n\n".join(_dedupe_preserve_order(no_auth_blocks))
            if no_auth_blocks
            else None
        )
    )
    prereq_global = _dedupe_preserve_order(prereq)
    if no_auth_merged:
        prereq_global = [no_auth_merged] + [p for p in prereq_global if p != no_auth_merged]

    consolidated = {
        "catalog_format": "test_cases_json_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "consolidated_from": sources,
        "task_sources": jira_meta,
        "no_authentication_scope": no_auth_merged,
        "prerequisites_global": prereq_global,
        "deprecated_test_cases": deprecated,
        "test_cases": all_cases,
    }

    out_path = root / "test_cases.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {out_path} ({len(all_cases)} cases, {len(deprecated)} deprecated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
