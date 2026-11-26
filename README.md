# Orchestrator Lead for OpenBot

Importable agent package for a self-hosted OpenBot server: the published
instructions, seven skills and two paused routines as one zip that OpenBot
reads under **Server settings → Import**.

One agent, one purpose: orchestrate software delivery across specialized
subagents (SPEC, Worker, QA, Code Review, Security Review, Incident RCA)
instead of running one large coding chat. Merges, deploys and store releases
stay with the owner.

## Origin

The agent was published by **Fellipe** as a public share page and taken over
from there on 2026-11-26:

- Share page: <https://openbot.run/agents/xwDzXa5f7bdgNuenppquGQ>
- Template state: 2026-11-24T19:48:18Z

This repo is a working copy for import, maintenance and hand-off on your own
server, not an original work and not a marketplace listing. Rights to the text
belong to the author; the OpenBot app itself is under PolyForm Noncommercial
1.0.0. Do not present it as your own product.

Not part of the share page and therefore not here: the creator's private
system prompt, model settings, conversations and workspace files.

## What is inside

| Path | Content |
|---|---|
| `AGENT.md` | the published agent description (source for `description` in the import) |
| `skills/orchestrator-lead-getting-started/` | first conversation: name, language, harness, per-role model matrix, repos, PR norms, timezone, routines |
| `skills/multi-model-spec/` | SPEC subagent, read-only: research, architecture, verifiable plan |
| `skills/multi-model-worker/` | Worker in its own Git worktree: implementation, Simplify Pass, verification, JSON handoff |
| `skills/multi-model-qa/` | diff-driven functional testing on the real surface with before/after evidence |
| `skills/multi-model-code-review/` | two-pass P0–P3 review, inline comments or a short LGTM, never an approval |
| `skills/multi-model-security-review/` | STRIDE, OWASP Top 10 + LLM Top 10, supply chain, `[security]` comments P0–P3 |
| `skills/multi-model-incident-rca/` | read-only root-cause analysis from CI, Sentry or prod alerts |
| `routines/issues-prs-daily-chase.txt` | routine "Issues & PRs Daily Chase", Mon–Fri 09:00, paused |
| `routines/ci-dependencies-errors-watch.txt` | routine "CI, Dependencies & Errors Watch", Mon–Fri 14:00, paused |
| `import/openbot-import.json` | generated manifest of the import package |
| `dist/openbot-orchestrator-lead.zip` | finished import package |
| `scripts/build-import.py` | builds manifest and zip from the files above, checks the format limits |
| `scripts/check-import.py` | checks a finished zip against the import rules |

The source of truth is `AGENT.md`, `skills/` and `routines/`. The manifest
and the zip are built from them and are not maintained by hand.

## Download link

- **Landing page:** `docs/index.html` (ready for GitHub Pages or any static host; GitHub Pages is not available for this private repo on the current plan)
- **Latest release:** <https://github.com/smartflow-suhl-de/openbot-orchestrator-lead/releases/latest>
- **Direct zip:** <https://github.com/smartflow-suhl-de/openbot-orchestrator-lead/releases/latest/download/openbot-orchestrator-lead.zip>

A tag `v*` runs `.github/workflows/release.yml`, builds the zip and attaches
it to the release, so the direct link always points at the newest build. The
repo is private, so the link only works for accounts with access. OpenBot has
no link that installs a zip from a URL: the download plus the three clicks in
**Server settings → Import** stay necessary.

## Building

```bash
./scripts/build-import.sh
./scripts/check-import.py
```

Result: `dist/openbot-orchestrator-lead.zip` with
`openbot-import.json` and `agents/orchestrator-lead/skills/…` at the root,
as OpenBot expects.

## Installing in OpenBot

The import runs on the OpenBot machine; nothing is uploaded.

1. Copy `dist/openbot-orchestrator-lead.zip` to the machine that runs OpenBot
   (or download the file there).
2. In OpenBot open **Server settings → Import**.
3. Choose **Select file…**, pick the zip and import the shown agent
   "Orchestrator Lead".
4. OpenBot creates a copy: instructions, the seven skills and the two
   routines. Conversations, memories, model, provider and workspace files of
   the creator are not taken over.

A second import of the same file does not overwrite the existing copy but
creates another one (or renames colliding skills). Decide beforehand whether
the old copy should be deleted.

### After the import

1. **Set model and provider.** New agents otherwise tend to start on `codex`;
   without a ChatGPT login the first turn fails. To start, choose
   `provider: opencode` with a model present in the catalog and a suitable
   reasoning effort, plus a backup model.
2. **Grant access, but only what is needed.** The agent expects GitHub (`gh`
   or GitHub MCP), an issue tracker and optionally Sentry/MCP for Incident
   RCA. MCP servers are defined server-wide and granted per agent; enable
   `computerUse` only when a GUI is really needed.
3. **Leave the routines paused** until there is an owner and a real need, and
   check the timezone: the package ships `Europe/Berlin`
   (`routines/` and `scripts/build-import.py`).
4. **Run the first conversation.** The first real turn starts
   `orchestrator-lead-getting-started`: name, language, harness (OpenCode,
   Paseo, Orca, T3 Code or custom CLIs), per-role model matrix, repos, PR
   norms, timezone. From that the agent writes its `AGENTS.md` into the
   workspace.
5. **Test small.** Run one small real task through SPEC → Worker → QA →
   Review and check the artifact before the agent goes into a channel or a
   routine.
6. **Confirm the limits.** No merge, deploy or store release without the
   owner's explicit written approval in chat; an OK from another agent does
   not count.

### Installing without the zip

1. Clone the repo into the agent's workspace, e.g. to
   `Agents/<name>/openbot-orchestrator-lead`.
2. Use `AGENT.md` as the agent description (text from "You are Orchestrator
   Lead …"; max. 2,000 characters).
3. Ask the agent to register the seven folders from `skills/` with its local
   skill tools (`create_skill`). Do not overwrite the installed copies under
   `.agents/skills` by hand.
4. Create the routines from `routines/` by hand, paused, Mon–Fri 09:00 and
   14:00 in your own timezone.

## Maintenance

- Change a skill text: edit `skills/<name>/SKILL.md` (the frontmatter `name`
  must match the folder name), then run `./scripts/build-import.sh` and
  `./scripts/check-import.py`.
- Change a routine: edit the file in `routines/`; name, time and timezone
  live in `scripts/build-import.py`.
- Roll out a new version: rebuild, import, then test again. No untested
  update into a running channel.

Format limits that the script checks: agent description 2,000 characters,
name 80, title 120, 32 skills per agent, 64 routines, 80 characters per
routine name, 200 files per skill folder, no `.env` files, keys or nested
archives in the zip.
