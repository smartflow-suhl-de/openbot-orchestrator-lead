---
name: multi-model-incident-rca
description: Dispatch the read-only Incident RCA subagent via the configured multi-model harness to investigate Sentry, CI, or production alerts using connectors first, trace root cause in the repository, and report impact and minimal fix without modifying code.
---

# Multi-Model Incident RCA — Read-Only Root Cause Analysis

## When to use

- On Sentry/error-tracker alerts, failing CI pipelines, or production incidents.
- **Strict monitoring rule**: during automated watch routines, run **strictly read-only**. Never edit code, open PRs, merge, or deploy without explicit owner authorization in chat.

## Harness dispatch

Read the configured harness and `dev-incident` model/effort from your `AGENTS.md`:
- **OpenCode**: invoke `subagent` with `agent: "dev-incident"` (or `Task` with `subagent_type: "dev-incident"`), read-only.
- **Paseo / Orca / T3 Code / CLI**: dispatch the configured read-only Incident RCA harness/profile.

## Investigation procedure

1. **Connector first**: prefer native MCP/connectors before CLI, API, or browser scraping:
   - Error trackers: Sentry MCP / connector, Axiom, Datadog, Grafana, etc.
   - Repo & CI: GitHub MCP / `gh`, Linear / issue tracker MCP.
2. **Collect alert evidence**:
   - Exact error message, exception type, full stacktrace (`file:function:line`).
   - Affected release/commit, environment, severity, event count, affected users, first/last seen, breadcrumbs, and OS/runtime tags.
3. **Trace in the repository**:
   - Locate the matching repo and read its `AGENTS.md` / `README`.
   - Trace the execution path from entry point through handlers, dependencies, error boundaries, and recent commits touching that area.
   - **Never** expose secrets, tokens, private DSNs, or user PII in chat or saved notes.
4. **Deliver structured RCA**:
   - **Confirmed root cause** (`file:line` + observed evidence).
   - **Contributing factors** (null state, race condition, dependency/runtime change, config drift).
   - **Failure pattern** (intermittent vs. continuous, frequency, affected version/env).
   - **Impact scope** (explicitly flag immediately if production is down, customer data is exposed, or security is impacted).
   - **Smallest recommended fix**, validation plan, and residual risk.

## Remediation & handoff

- **In scheduled watch routines**: report a short RCA with the alert link and likely root cause; if nothing new/actionable occurred, stay silent (`routine_no_update`).
- **Once authorized by the owner**: hand the RCA summary into the full delivery pipeline (`multi-model-spec` -> `multi-model-worker` -> `multi-model-qa` -> `multi-model-code-review` + `multi-model-security-review`), keeping all merge and deploy gates intact.
- Save only generic, non-secret recurring investigation quirks (never raw scripts, private URLs, or credentials).
