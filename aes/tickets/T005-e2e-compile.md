---
ticket: T005
title: End-to-end 3DS hello-world compile verification
sprint: sprint-04
priority: high
status: done
completed: 2026-10-20
created: 2026-10-20
---

# T005 — End-to-end 3DS hello-world compile verification

## Context

The whole chain (MCP → server → podman container → devkitARM) must be proven
to work with a real compile, not a simulation. A minimal 3DS homebrew
hello-world using libctru is the smallest possible proof.

## Acceptance Criteria

- [ ] A minimal 3DS source tree exists (libctru hello-world: `main.c` +
      `Makefile` using `3dsx.specs`)
- [ ] `compile_3ds` called from this OpenCode session returns exit 0 and a
      `.3dsx` path
- [ ] The `.3dsx` file exists and is non-empty
- [ ] The build log shows `arm-none-eabi-gcc` was invoked (real toolchain,
      not a stub)
- [ ] A second, deliberately broken source returns a non-zero exit and a
      structured error (negative control)

## Scope

**In scope:**
- the hello-world source tree
- the end-to-end compile through MCP
- the negative control (broken source)

**Out of scope:**
- any actual 3DS application logic beyond the hello-world

## Dependencies

- T002 (devkitpro in container)
- T003 (MCP server)
- T004 (MCP wired into OpenCode)

## Rollback

Remove the hello-world source tree and its build artifacts. The toolchain is
unaffected.

## Known Risks

- **R1 — libctru API changes.** The libctru hello-world pattern is stable but
  upstream may have moved. Mitigation: check against the installed libctru
  headers before writing the source.
- **R2 — specs file name.** `3dsx.specs` is the correct specs file for 3DS
  homebrew. Mitigation: verify it exists in the container after install.

## Notes

This is the acceptance gate for the whole project. Until T005 passes, the
project is not done.