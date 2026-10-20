---
ticket: T001
title: Scaffold AES project structure
sprint: sprint-01
priority: high
status: done
created: 2026-10-20
completed: 2026-10-20
---

# T001 — Scaffold AES Project Structure

## Context

The directory `/home/seyon/dev/Games/Nintendo/3DS/deck-devkitpro` was empty
(greenfield). The goal is to install devkitpro in a podman container on the
Steam Deck and expose it to this OpenCode session via MCP. Before any of that
work, the project needed an AES structure so the protocol (kanban, tickets,
hooks, docs) could govern the build.

## Acceptance Criteria

- [x] `aes/kanban.md` exists with project goal, sprints, and ticket table
- [x] `aes/tickets/`, `aes/sprints/`, `aes/handoffs/`, `aes/verification/`
      exist
- [x] `CLAUDE.md` is a real operational contract (intent, non-goals, critical
      files, never-do, evidence rules)
- [x] `docs/VISION.md`, `docs/REQUIREMENTS.md`, `docs/ROADMAP.md` describe the
      actual project
- [x] `.aes/hooks/` contains working pre-commit, pre-build, pre-review,
      pre-verify hooks
- [x] `.git/hooks/pre-commit` wired to `.aes/hooks/pre-commit.sh`
- [x] git initialised

## Scope

**In scope:** scaffolding, kanban, docs, hooks, git init.

**Out of scope:** any actual devkitpro or MCP work — that is T002+.

## Dependencies

None.

## Rollback

`rm -rf` the scaffolded files. Nothing external was modified.

## Known Risks

- The installed AES skill ships 13 hook symlinks that point to a non-existent
  `.aes/hooks/`. Real implementations live at `/opt/aes/.aes/hooks/`. This was
  discovered and fixed during scaffolding (see ROADMAP `[DISCOVERED mid-task]`).
- The `new-project.sh` script copies language templates into `docs/templates/`
  which is noise for this project. Left in place — harmless and may be useful.

## Notes

Scaffolded via `~/.config/opencode/skills/aes/scripts/new-projectpro.sh
deck-devkitpro javascript .`. Hooks copied from `/opt/aes/.aes/hooks/`.