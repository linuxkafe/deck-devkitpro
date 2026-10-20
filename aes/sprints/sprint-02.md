---
sprint: sprint-02
period: 2026-10-20 → 2026-10-20
status: done
---

# Sprint 02 — devkitpro in podman + MCP server + OpenCode wiring

## Tickets

| ID | Title | Status |
|----|-------|--------|
| T002 | Install devkitpro in podman container on Deck | done |
| T003 | Implement MCP server exposing 3DS compile tooling | done |
| T004 | Wire MCP into OpenCode config | done |
| T005 | End-to-end 3DS hello-world compile verification | done |

## Retrospective

### What went well
- The official `devkitpro/devkitarm` Docker image (1.51 GB) has everything pre-installed: devkitARM 16.1.0, libctru, dkp-pacman, examples. This bypasses the broken package server entirely.
- Host isolation is clean — devkitpro lives only inside the container, zero host pollution.
- Python MCP SDK v2.3.0 works well; the `MCPServer` API with `@server.tool()` decorator is clean.
- SSH-based stdio transport works reliably for remote MCP servers.
- Negative control (broken source) correctly returns error.

### What went wrong
- **Broken AES hook symlinks**: The installed AES skill at `~/.config/opencode/skills/aes/hooks/` ships 13 hooks as symlinks pointing to a non-existent `../.aes/hooks/`. Real implementations live at `/opt/aes/.aes/hooks/`. Copied from `/opt/aes/` as workaround.
- **Package server Cloudflare protection**: `pkg.devkitpro.org` blocks non-browser UAs with 403. The apt-based installer won't work in containers without browser-like headers. Workaround: use the pre-baked Docker image.
- **MCP server stdout buffering**: Python's stdio buffering caused silent failures when testing. Fixed with `sys.stdout.reconfigure(line_buffering=True)`.
- **Container path vs host path**: Examples live inside the container, not on the Deck host. Added path extraction logic to copy from container to `/tmp/dkp-compile-*` before compiling.

### What to change next sprint
- Consider building a custom Dockerfile that layers on top of the official image with any additional libraries needed.
- Add a `Makefile` target for common operations (`make compile`, `make clean`, `make status`).
- Consider adding a `dkp-pacman` wrapper to install additional libraries on demand.
- Report the broken AES hook symlinks to the AES maintainers.
