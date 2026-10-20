---
ticket: T004
title: Wire MCP into OpenCode config
sprint: sprint-03
priority: medium
status: done
completed: 2026-10-20
created: 2026-10-20
---

# T004 — Wire MCP into OpenCode config

## Context

The MCP server (T003) runs on the Deck but is only useful if this OpenCode
session can see its tools. That requires an MCP entry in `.opencode/config.json`
pointing at the Deck-side server.

## Acceptance Criteria

- [ ] `.opencode/config.json` exists with an MCP server entry for the Deck
- [ ] The entry uses the stdio transport and references the running server
- [ ] After reloading the config, the MCP tools appear in this session's
      toolset (verified by listing available tools)
- [ ] `compile_3ds` is callable from this session

## Scope

**In scope:** the OpenCode MCP config entry only.

**Out of scope:** the server itself (T003), the compile verification (T005).

## Dependencies

- T003 (MCP server implemented and running on Deck)

## Rollback

Remove the MCP entry from `.opencode/config.json`. No other state is touched.

## Known Risks

- **R1 — config schema.** OpenCode's MCP config schema may differ from the
  documented one. Mitigation: check the actual schema before writing the file.
- **R2 — server path.** The config must reference the server by a path that
  resolves on the Deck, not locally. Mitigation: the server runs on the Deck;
  the config entry's `command` is an SSH-forwarded invocation or the server is
  reachable over a forwarded port.

## Notes

The MCP server runs on the Deck. Options for connectivity:
- SSH port forward from local to Deck, config points at `localhost:<port>`.
- The server runs over stdio and the config entry shells into the Deck via
  SSH and pipes stdio.

The stdio-over-SSH approach is preferred because it needs no port management.