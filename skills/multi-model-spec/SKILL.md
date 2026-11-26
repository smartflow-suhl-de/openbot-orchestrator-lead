---
name: multi-model-spec
description: Dispatch the read-only SPEC subagent via the configured multi-model harness (OpenCode, Paseo, Orca, T3 Code, or CLI) to research a codebase, design architecture, and produce a self-contained implementation plan with verification assertions before any code is written.
---

# Multi-Model SPEC — Research & Technical Specification (Read-Only)

## When to use

- Before implementing any feature, structural refactor, or non-trivial bug fix.
- To map module boundaries, API contracts, data flows, and blast radius without modifying files.

## Harness dispatch

Read the configured harness and `dev-spec` model/effort from your `AGENTS.md`:
- **OpenCode**: invoke `subagent` with `agent: "dev-spec"` (or `Task` with `subagent_type: "dev-spec"`). Do not override `model` in the call when `~/.config/opencode/agents/dev-spec.md` already sets the validated model and effort.
- **Paseo**: run a read-only agent session via `paseo run --provider x3Cspec-provider/model> ...` pointing at the repo path with strict read-only instructions.
- **Orca / T3 Code / CLI**: dispatch the configured read-only SPEC harness/profile with the prompt guidelines below.

## Subagent prompt & guidelines

Pass the issue/goal, acceptance criteria, project `AGENTS.md` constraints, and these `x3Cspec_mode_guidelines>`:

```xml
x3Cspec_mode_guidelines>
1. Explicit Activation: Spec Mode is active for this planning pass.

2. Read-Only Discipline:
   - Your SOLE focus is research and planning.
   - NEVER modify files, create commits, or run destructive commands.
   - Use ONLY read-only tools (read, grep, glob, read-only shell inspection) to gather context.

3. Specification Requirements:
   - The plan must be comprehensive and self-contained so an isolated Worker can execute it without guessing.
   - Include exact file paths, symbol names, line numbers, and concrete code snippets showing what will change and where.
   - Explain the "Why" and "How" for every step, including edge cases and failure modes.
   - Define explicit verification assertions (`fulfills`) and exact commands/surfaces that Worker and QA must prove before concluding.

4. Diagrams:
   - Include Mermaid diagrams (```mermaid) only when architecture, state transitions, or data flows gain clarity.
   - Keep node/participant labels short (x3C 20 chars).
   - Use only supported types: flowchart/graph, stateDiagram, sequenceDiagram, classDiagram, erDiagram, xychart-beta.
x3C/spec_mode_guidelines>
```

## Coordinator check

1. Review the returned spec for completeness, missing edge cases, or over-engineering.
2. Confirm the spec respects repository conventions and does not introduce unnecessary abstractions.
3. Hand the approved spec, isolated worktree path, target files, and `fulfills` assertions to the `multi-model-worker` stage.
