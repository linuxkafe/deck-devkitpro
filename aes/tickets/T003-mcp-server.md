---
ticket: T003
title: Implement MCP server exposing 3DS compile tooling
sprint: sprint-03
priority: high
status: done
completed: 2026-10-20
created: 2026-10-20
---

# T003 — Implement MCP server exposing 3DS compile tooling

## Context

The devkitpro container (T002) is useful only if this OpenCode session can
invoke it programmatically. Rather than ad-hoc SSH commands, the toolchain is
exposed through a **Model Context Protocol (MCP) server** running on the Deck.
The server wraps devkitpro operations and presents them as MCP tools.

## Acceptance Criteria

- [ ] `mcp/` contains a Node.js MCP server using the official `@modelcontextprotocol/sdk`
- [ ] Server exposes these tools, each with a JSON Schema input:
  - `compile_3ds(source_path, output_path?)` — compiles a 3DS source tree to
    `.3dsx` using the containerised devkitARM. Returns output path and build
    log. Non-zero exit on compile failure.
  - `clean(project_path)` — removes build artifacts for a project.
  - `toolchain_status()` — reports devkitpro version, installed libraries,
    toolchain health.
  - `list_libraries()` — lists devkitpro library groups available via pacman.
- [ ] Each tool invokes the real devkitpro command inside the container —
  no faked or stubbed behaviour
- [ ] `make test` passes (see test plan below)
- [ ] `make lint` passes

## Scope

**In scope:**
- the MCP server implementation in `mcp/`
- the tool wrappers around devkitpro commands
- unit tests for argument handling and error paths

**Out of scope:**
- the OpenCode config wiring (T004)
- the end-to-end compile (T005)
- a UI or web interface

## Dependencies

- T002 (devkitpro installed in container on Deck)

## Rollback

Remove `mcp/`. No external state is created by the server itself — it shells
out to the container.

## Known Risks

- **R1 — MCP SDK version drift.** The `@modelcontextprotocol/sdk` API changes.
  Mitigation: pin the version in `package.json` and test against it.
- **R2 — long-running compiles.** `compile_3ds` may take seconds to minutes.
  The MCP stdio transport must not time out mid-compile. Mitigation: the server
  runs the compiler synchronously and streams output; the client must use an
  appropriate timeout.
- **R3 — path traversal.** Tool arguments reach the shell. Mitigation: validate
  and sanitise paths before passing them to the compiler; never interpolate
  untrusted input into shell commands.

## Test Plan

- `compile_3ds` with a missing source path returns a structured error, not a
  crash.
- `clean` on a path with no build artifacts is a no-op (exit 0).
- `toolchain_status` returns a parseable object with a `healthy` boolean.
- Argument sanitisation: a path containing `;` or `|` is rejected.

## Notes

Transport: stdio. The server runs on the Deck; the client runs locally in
OpenCode.