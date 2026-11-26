---
name: multi-model-qa
description: Dispatch the QA subagent via the configured multi-model harness to run diff-driven functional testing on the real user surface (web, mobile/emulator, CLI/TUI, or API) and return before/after evidence.
---

# Multi-Model QA — Diff-Driven Functional Validation

**Scope:** Manual/functional QA only — verify the application works by interacting with it as a real user would (browser, mobile emulator/simulator, terminal, or HTTP/API client). Do **not** duplicate unit tests, ESLint, typecheck, or CI checks.

## Harness dispatch

Read the configured harness and `dev-qa` model/effort from your `AGENTS.md`:
- **OpenCode**: invoke `subagent` with `agent: "dev-qa"` (or `Task` with `subagent_type: "dev-qa"`).
- **Paseo / Orca / T3 Code / CLI**: dispatch the configured QA harness/profile against the branch worktree or preview environment.

Pass: repo/worktree path, base branch, target test environment/surface, and `fulfills` assertions from the SPEC.

## Procedure

1. **Load project QA config**: read the project's `AGENTS.md` or QA config (e.g., `.factory/skills/qa/config.yaml` if present) for URLs, startup commands, test personas, and environment restrictions (never perform destructive actions or create fake users in production).
2. **Analyze `git diff`**: map changed files to affected apps/surfaces.
   - Test **only** apps and flows affected by the diff plus direct integration neighbors.
   - Do **not** test untouched surfaces (e.g., skip backend flows if only web CSS changed).
   - If no application code changed (docs-only, CI-only, config-only), report `INCONCLUSIVE: No app code changed — QA not applicable for this diff.`
3. **Test real branch code**: run against the branch's local dev server, preview deployment, or branch build — not stale staging/main (except when capturing the "Before" baseline).
4. **Before & After evidence**: whenever UI or user-facing behavior changes, capture both baseline (base branch) and updated (PR branch) evidence using text snapshots (accessibility tree, terminal output, structured HTTP responses) plus screenshots or recordings when visual.
5. **Test Quality Gate**:
   - At least half the tests directly verify the new/changed behavior in the diff.
   - Include integration checks where the change meets adjacent features.
   - Include at least **1 negative / boundary test** (error handling, invalid input, empty/limit states).
   - Mark `INCONCLUSIVE` rather than `PASS` if you cannot verify the actual behavioral delta.
   - **Never silently skip a flow**: report failures as `FAIL` and environment issues as `BLOCKED` with exact error and remediation, then continue remaining flows.

## Output format

Return a concise `## QA Report`:
- Results table using statuses: `PASS`, `FAIL`, `BLOCKED`, `FLAKY`, `INCONCLUSIVE` (list only user-facing verification rows, not build/setup steps).
- Short **Action Required** section if anything failed or was blocked.
- Collapsed `x3Cdetails>` block containing trimmed, clearly labeled before/after evidence and local artifact paths (never embed unverified/broken image URLs).
- Optional **Environment Insights** table only if a genuinely reusable testing quirk was discovered.
