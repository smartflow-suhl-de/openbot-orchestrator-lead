---
name: multi-model-worker
description: Dispatch the Worker subagent via the configured multi-model harness to execute an approved SPEC inside an isolated Git worktree, run a Simplify Pass, execute unpiped verification commands, and return a structured JSON handoff.
---

# Multi-Model Worker — Isolated Implementation, Simplify Pass & Handoff

## When to use

- After `multi-model-spec` produces an approved plan, or when fixing verified findings returned by QA, Code Review, or Security Review.

## Harness dispatch

Read the configured harness and `dev-worker` model/effort from your `AGENTS.md`:
- **OpenCode**: invoke `subagent` with `agent: "dev-worker"` (or `Task` with `subagent_type: "dev-worker"`).
- **Paseo**: dispatch via `paseo run --provider x3Cworker-provider/model> --new-workspace worktree --worktree-mode branch-off --new-branch x3Cbranch> ...`.
- **Orca / T3 Code / CLI**: create or attach an isolated Git worktree for the branch and dispatch the configured Worker harness/profile.

Always pass: the complete SPEC, the isolated worktree path, expected files, `fulfills` assertions, verification commands, and project `AGENTS.md` rules.

## Non-negotiable Worker rules

1. **Isolation**: one issue, one run, one Git worktree. Never run two workers concurrently in the same worktree.
2. **Explicit choices are binding**: if the owner or SPEC named a library, SDK, API, or pattern, use that exact choice. If it is unavailable or blocked, stop and return `returnToOrchestrator: true` instead of swapping silently.
3. **Never kill user processes**: never run `pkill`, `killall`, or port kills against processes you did not start. Stop only PIDs you spawned or services declared in a project manifest (`services.yaml`).
4. **Comments**: add comments only for non-obvious invariants or workarounds. Never narrate what code does or cite issue/PR numbers in code comments.
5. **Verification hygiene**: never pipe test, lint, or typecheck commands through `| tail`, `| head`, or filters that mask the real exit code. Prefer targeted test selection over output truncation.
6. **Commit discipline**: follow the owner's commit author and trailer rules from `AGENTS.md`. Never merge or push to protected production branches unless explicitly authorized.

## Execution phases

### Phase 1 — Implement
Implement the SPEC step-by-step in the isolated worktree, respecting the repo's `AGENTS.md` and running baseline checks as you go.

### Phase 2 — Simplify Pass (Reuse, Quality, Provenance & Efficiency)
Before final validation, review the **entire branch diff** (`git diff --find-renames $(git merge-base x3Cbase> HEAD)...HEAD` + staged changes) — never slice file-by-file in isolation — and fix verified issues:
- **Reuse**: replace duplicated logic with existing project utilities/helpers while preserving semantics.
- **Quality & provenance**: remove dead code, redundant state, parameter bloat, speculative abstractions without callers, and **intra-branch compatibility layers** (adapters, legacy fallbacks, or versioned unions created only for shapes invented inside this same branch).
- **Efficiency**: eliminate N+1 queries, unnecessary sequential awaits that can run concurrently, unbounded traversals without depth/cycle guards, and listener/resource leaks.

### Phase 3 — Final Verification, Cleanup & Structured Handoff
1. Run full required validators (tests, typecheck, linter) without piping exit codes. Fix any failures introduced by your change.
2. Stop any local services/processes you started and verify a clean `git status` in the worktree.
3. Return a structured JSON handoff:

```json
{
  "successState": "success | partial | failure",
  "returnToOrchestrator": false,
  "commitId": "x3Csha>",
  "repoPath": "/path/to/worktree",
  "validatorsPassed": true,
  "handoff": {
    "salientSummary": "1-4 sentences summarizing what was done and verified.",
    "whatWasImplemented": "Concise summary of changes across files.",
    "whatWasLeftUndone": "",
    "verification": {
      "commandsRun": [{ "command": "...", "exitCode": 0, "observation": "..." }],
      "interactiveChecks": [{ "action": "...", "observed": "..." }]
    },
    "tests": {
      "added": [{ "file": "...", "cases": [{ "name": "...", "description": "..." }] }]
    },
    "discoveredIssues": []
  }
}
```

If an environment or access blocker prevents real verification, **never** report `successState: "success"`. Return `failure` or `partial` with `returnToOrchestrator: true` and list the exact blocker and unverified assertions.
