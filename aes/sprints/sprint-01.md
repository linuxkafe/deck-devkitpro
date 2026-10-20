---
sprint: sprint-01
period: 2026-10-20 → 2026-10-20
status: done
---

# Sprint 01 — Project scaffolding + reconnaissance

## Tickets

| ID | Title | Status |
|----|-------|--------|
| T001 | Scaffold AES project structure | done |

## Retrospective

### What went well
- Greenfield detection ran before any scaffolding, so nothing was overwritten.
- Deck reconnaissance (SSH, podman, GCC, internet) ran before committing to a
  design — this caught that devkitpro was not installed and that SteamOS is
  Arch-based, which changes the install path.
- The broken AES hook symlinks were found and fixed during bootstrap rather
  than discovered mid-flight.

### What went wrong
- The installed AES skill ships 13 hooks as symlinks to a non-existent
  `.aes/hooks/`. The real implementations live at `/opt/aes/.aes/hooks/`.
  This is a defect in the AES install, not in this project. Worked around by
  copying from `/opt/aes/.aes/hooks/`.

### What to change next sprint
- Prefer `/opt/aes/.aes/hooks/` as the canonical hook source when copying.
- Consider reporting the broken symlinks to the AES maintainers.