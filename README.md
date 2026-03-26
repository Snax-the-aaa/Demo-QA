# Chat app — test cases repository (Excel)

This tree is the **dedicated test-case catalog** for the **chat-app** product: **per-task** manual workbooks under `tasks/`, optionally merged into **one global** workbook by the consolidation script. In the monorepo it lives under `example/test-cases-repo/` as a copy-paste layout.

**Product scope:** chat-app UAT / regression rows live under `tasks/<task_id>_<slug>/`, separate from application source repos.

## Task folder and workbook naming

- **Folder:** `tasks/<task_id>_<slug>/` — e.g. `KAN-10_user-profile-management` (Jira-style id + short slug, **underscore** between id and slug).
- **Workbook (preferred):** `tasks/<task_id>_<slug>/<task_id>_<slug>.xlsx` (same name as the folder + `.xlsx`).
- **Fallback:** `test_cases.xlsx` inside the folder is still accepted.

**QA / platform subtasks** should only add or change files **inside that task folder** (the workbook and optional human `metadata.json`). Do not rely on consolidation running in the same step.

## What to commit (typical MR)

Include **only** your task folder: the `.xlsx` and optional `metadata.json` (platform fields only). Do **not** commit `output/` or `consolidation_state.json` unless your team chooses to track them (this example **gitignores** them).

## What to commit (typical MR)

For a **single task**, commits and merge requests should usually include **only** that task’s folder: `tasks/<slug>/test_cases.xlsx` and optional `tasks/<slug>/metadata.json` **human/platform fields** (not consolidation side effects).

**Do not rely on** `output/`, `consolidation_state.json`, or other tasks’ `metadata.json` changing as part of normal authoring—those come from **manually** running `scripts/consolidate_test_cases.py` when you want a consolidated workbook. This repo’s `.gitignore` excludes `output/` and `consolidation_state.json` so local consolidation runs do not dirty unrelated paths. The script **by default** only updates `metadata.json` **inside task folders that received new rows in that run** (use `--refresh-all-task-metadata` if you need every merged folder refreshed).

**Baseline** (`baseline/*.xlsx`) should change only when the team intentionally updates the column template—opening it in Excel can rewrite the file; avoid committing accidental baseline diffs.

## Layout

| Path | Purpose |
|------|--------|
<<<<<<< HEAD
| `scripts/consolidate_test_cases.py` | Consolidation script (copy of platform `scripts/consolidate_test_cases.py`; run from **this** repo root). |
| `scripts/requirements.txt` | `openpyxl` for the script. |
| `consolidation_metadata.json` | Optional baseline pointer: `baseline_template_relative` (path under repo root) and optional `baseline_sheet`. If missing or `baseline_template_relative` is empty, the script uses **row 1 of the first task workbook** as the column layout (no separate baseline file). `--baseline` overrides this file. |
| `baseline/AutoSec-Test-Cases-Baseline.xlsx` | Template for **header row** when referenced from `consolidation_metadata.json` (or `--baseline`). |
| `tasks/<slug>/test_cases.xlsx` | Test cases for one task. |
| `tasks/<slug>/metadata.json` | Optional **platform** fields (`platform_task_title`, `flow_steps_tail`, …). The **consolidation** subsection is **written by the script** when you run consolidation (default: only for task folders merged with **new** rows that run). |
| `consolidation_state.json` | **Authoritative** list of task slugs in the rolling consolidated file + path to that workbook (incremental runs). **Gitignored** here—local artifact; commit only if your team shares state via git (`git add -f`). |
| `output/` | Rolling consolidated workbook (e.g. `latest_consolidated.xlsx`). **Gitignored** (see `.gitignore`). |
=======
| `scripts/consolidate_test_cases.py` | Merge script (canonical: `scripts/consolidate_test_cases.py` at monorepo root). |
| `scripts/requirements.txt` | `openpyxl`. |
| `consolidation_metadata.json` | Optional: `baseline_template_relative`, `baseline_sheet`. If `baseline_template_relative` is empty, column layout comes from the **first** task workbook. |
| `baseline/*.xlsx` | Optional template for header row when referenced from `consolidation_metadata.json`. |
| `tasks/<task_id>_<slug>/*.xlsx` | Per-task cases (see naming above). |
| `tasks/<task_id>_<slug>/metadata.json` | Optional **human/platform** fields only. The merge script **does not** write here. |
| `consolidation_state.json` | **Only** written by the merge script: `baseline_file_relative` (= latest output path), `processed_task_folders` (folders to **skip** next run), timestamps. **Gitignored** here. |
| `output/latest_consolidated.xlsx` | **Global** workbook: sheet `Consolidated`, **first column `Task ID`** (task folder name), then test columns, then `_…` meta columns. **Gitignored** here. |
>>>>>>> 86de912 (Update code)

## How consolidation works

1. **No `consolidation_state.json`** (or empty `processed_task_folders`) → merge **all** task folders from scratch into `output/…`.
2. **With state** → load the previous global file (`baseline_file_relative` / `last_output_relative`), keep existing rows, **append only** task folders **not** listed in `processed_task_folders`.
3. After a successful write, state is updated: `baseline_file_relative` and `last_output_relative` point at the new global file; `processed_task_folders` lists every folder merged into that file (those are skipped on the next incremental run).
4. If state references a missing global file, run **`--full-rebuild`** (or restore the file).

```bash
cd example/test-cases-repo   # or your repo root
pip install -r scripts/requirements.txt

python scripts/consolidate_test_cases.py --full-rebuild \
  --tasks-dir tasks \
  --output-dir output

python scripts/consolidate_test_cases.py \
  --tasks-dir tasks \
  --output-dir output
```

<<<<<<< HEAD
1. **State + rolling file** — `consolidation_state.json` records `included_task_slugs` and `last_output_relative` (usually `output/latest_consolidated.xlsx`).
2. **Next run** — The script loads that workbook, keeps all rows, and **only appends** folders under `tasks/` that are **not** in `included_task_slugs`.
3. **After write** — State is updated with the **full** slug list. By default, only task folders that had **new** rows merged this run get an updated `metadata.json` **consolidation** block; use `--refresh-all-task-metadata` to refresh every merged folder (legacy).

Options: `--state-file <path>`, `--output-name other.xlsx`, `--baseline` (override metadata), `--baseline-sheet "AutoSec_Web"`, `--refresh-all-task-metadata`.

If the previous consolidated file is missing but state still lists slugs, the script **re-merges all** task folders and rebuilds state.

When developing inside the **full platform monorepo**, you can instead run the same logic from the repo root:

`pip install -r scripts/requirements-testcases.txt` and use paths `example/test-cases-repo/baseline/...`, etc. (see `scripts/consolidate_test_cases.py` docstring).
=======
Options: `--state-file`, `--output-name`, `--baseline`, `--baseline-sheet`, `--task-sheet`.

Monorepo: `pip install -r scripts/requirements-testcases.txt` and paths under `example/test-cases-repo/`.
>>>>>>> 86de912 (Update code)

## Platform integration

1. Create a real git repo with this structure (e.g. `chat-app-test-cases`) and register it in **config-registry**.
2. Bind **`test-cases-catalog`** (or your slug) on chat-app tasks.
3. Architecture adds a **qa** subtask for Excel packs when needed (`skills/architecture-role.md`; `rules/test-cases-excel.mdc`). Execution follows **`skills/test-cases-excel.md`**.

## Sample folders

- `tasks/example-feature-auth/`, `tasks/example-api-rate-limit/`, `tasks/KAN-10-user-profile-management/` — examples (naming patterns may mix legacy and `KAN-*_*` style).
