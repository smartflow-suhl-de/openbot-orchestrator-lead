---
name: multi-model-code-review
description: Dispatch the read-only Code Review subagent via the configured multi-model harness to perform a two-pass P0-P3 bug review on a PR diff and post inline comments (or a short LGTM when clean), without approving or requesting changes.
---

# Multi-Model Code Review — Two-Pass High-Confidence PR Review

## Harness dispatch

Read the configured harness and `dev-code-review` model/effort from your `AGENTS.md` (ideally a different model family from the Worker to catch blind spots):
- **OpenCode**: invoke `subagent` with `agent: "dev-code-review"` (or `Task` with `subagent_type: "dev-code-review"`), strictly read-only.
- **Paseo / Orca / T3 Code / CLI**: dispatch the configured read-only Code Review harness/profile in parallel with `multi-model-security-review`.

## Methodology

1. **Understand context & diff**: read linked issue/PR description and compute the diff (`git diff $(git merge-base HEAD x3Cbase>)..HEAD`). Inspect every changed file.
2. **Pass 1 — Candidate generation**: look for high-confidence, actionable defects:
   - Null/undefined dereferences, unchecked lookups, missing JSON keys.
   - Resource leaks (unclosed files, connections, listeners, missing error-path cleanup).
   - Logic bugs, wrong variable/shadowing, AND/OR inversions, off-by-one/pagination bugs, contract mismatches.
   - Concurrency hazards (TOCTOU, lost updates, unsafe shared state) and async/await pitfalls (`forEach` with async callbacks, missing `await`, unhandled rejections).
   - Missing error handling on critical I/O, auth, persistence, or migrations.
   - Dead/unused code left from incomplete refactors.
3. **Pass 2 — Strict validation & deduplication**:
   - **Reject** speculative "might" findings without a concrete trigger, subjective style nitpicks not backed by repo conventions (`AGENTS.md` / sibling files), findings unanchored to changed lines, or duplicates of existing PR comments.
   - **Severity bar**:
     - `[P0]`: definite crash, data corruption, or exploit with verified trigger path.
     - `[P1]`: verified logic bug or broken contract.
     - `[P2]`: reject by default unless independently verified with a realistic caller trigger (never edge-case defensive nitpicks).
     - `[P3]`: minor confirmed issue only when clearly actionable.
   - Deduplicate candidates sharing the same root cause — keep only the sharpest anchor.

## Posting to the PR

Whenever the PR is known and posting is enabled:
1. Verify every inline anchor lands on a changed line inside `gh pr diff x3Cpr> --patch` (`RIGHT` for additions/context, `LEFT` only for deletion-only findings without suggestion blocks).
2. Post inline findings via GitHub's PR Reviews API (`comments[]` with snake_case `path`, `line`, `side`, `start_line`, `start_side`, `body`) and `event: "COMMENT"`. **Never** use `APPROVE` or `REQUEST_CHANGES` — merge approval belongs strictly to the human owner.
3. **Clean review (zero findings)**: post one short top-level comment (e.g., `LGTM — no issues found.`) without caveats or padding.
4. **Idempotency**: do not post twice for the same `headRefOid`.
5. If posting is unavailable (no PR yet, permissions, network), return the structured findings in chat and state plainly that the PR comment was not posted and why.
6. Write all finding prose and summaries in the owner's configured language.
