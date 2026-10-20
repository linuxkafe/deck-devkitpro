---
ticket: T007
title: README.md + GitHub repo init + release
sprint: sprint-04
priority: medium
status: pending
created: 2026-10-20
---

# T007 — README.md + GitHub repo init + release

## Context

After building the project (container install, MCP server, Decky plugin),
document everything properly and publish to GitHub for discoverability and
easy installation.

## Acceptance Criteria

- [ ] `README.md` covers:
  - What this project is
  - Architecture diagram
  - Prerequisites
  - Installation (curl|sh)
  - Usage (MCP tools, CLI, Decky plugin)
  - Troubleshooting
- [ ] GitHub repo initialised with `git init` + first commit
- [ ] Remote added pointing to GitHub (user to confirm)
- [ ] `.github/workflows/ci.yml` for basic checks
- [ ] `LICENSE` file (MIT)
- [ ] `CHANGELOG.md` with first entry

## Scope

**In scope:**
- README.md
- GitHub repo setup
- Basic CI workflow
- License

**Out of scope:**
- Publication to npm/pypi
- Official Decky plugin registry submission

## Dependencies

- T006 (Decky plugin complete)

## Rollback

None — documentation changes are reversible.
