---
ticket: T006
title: Decky plugin — on/off control + status UI
sprint: sprint-03
priority: high
status: in-progress
created: 2026-10-20
---

# T006 — Decky plugin for devkitpro service control

## Context

The devkitpro toolchain runs inside a podman container on the Steam Deck and
exposes MCP tools to this OpenCode session. The user wants a **Decky plugin**
(like ollama-deck) that allows toggling the service on/off directly from the
Steam Deck's gaming overlay, showing status, version, and health.

The plugin follows the ollama-deck pattern:
- `main.py` — Python backend that interfaces with podman
- `src/index.tsx` — React frontend for Decky UI
- `plugin.json` — Decky manifest
- `cli.py` — CLI wrapper for SSH/headless control
- `install.sh` — Installer script

## Acceptance Criteria

- [ ] `main.py` exposes callable functions for:
  - `get_status()` — container health, image present, toolchain version
  - `start_service()` — starts the MCP server (if not running)
  - `stop_service()` — stops the MCP server
  - `get_toolchain_info()` — compiler version, libctru, groups
- [ ] `src/index.tsx` shows:
  - Service status (running/stopped)
  - Toggle button to start/stop
  - Toolchain version info
  - Container image info
- [ ] `plugin.json` follows Decky schema
- [ ] `install.sh` installs to `~/.local/share/Steam/extensions/plugins/`
- [ ] Plugin loads without errors in Decky
- [ ] Status reflects actual container state
- [ ] CLI `devkitpro-deck` available after install

## Scope

**In scope:**
- Decky plugin Python backend
- Decky plugin TypeScript frontend
- CLI wrapper (reuses existing mcp/server.py logic)
- install.sh script
- README update

**Out of scope:**
- Modifying the existing MCP server (mcp/server.py)
- Adding new MCP tools
- GPU-specific optimizations

## Dependencies

- T002 (devkitpro container installed)
- T003 (MCP server implemented)
- T004 (OpenCode wiring done)
- ollama-deck pattern reference at `/home/seyon/dev/ollama-deck/`

## Rollback

Remove the plugin directory from `~/.local/share/Steam/extensions/plugins/`.
No host state is modified by the plugin.

## Known Risks

- **R1 — Podman socket access.** Rootless podman may not be accessible from
  all contexts. Mitigation: run podman commands as the `deck` user.
- **R2 — Plugin hot-reload.** Decky may not reload plugins correctly after
  install. Mitigation: document restart procedure.
- **R3 — Path conflicts.** Plugin dirs may vary between Decky versions.
  Mitigation: check multiple known locations in install.sh.

## Notes

The MCP server runs on the Deck and talks podman directly. The plugin just
needs to show status and provide start/stop controls. It does NOT need to
be the MCP server itself — that remains separate.
