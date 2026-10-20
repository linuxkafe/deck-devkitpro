# T003 — Build Output (MCP server)

## What Changed

| File | Intent |
|------|--------|
| `mcp/server.py` | Python MCP server exposing 5 tools |
| `opencode.jsonc` | Project-local config with devkitpro MCP entry |
| `~/.config/opencode/opencode.jsonc` | Global config with devkitpro MCP entry |

## Tools Exposed

| Tool | Description |
|------|-------------|
| `compile_3ds(source_path)` | Compile a 3DS project to .3dsx |
| `clean(project_path)` | Clean build artifacts |
| `toolchain_status()` | Check toolchain health |
| `list_libraries()` | List available libraries |
| `list_groups()` | List predefined groups |

## What Was Untouched

- The devkitpro container image (pulled from official registry)
- The Deck's host filesystem
- Any existing MCP servers (github, rea)

## Key Design Decisions

1. **Python over Node.js**: The Deck has Python 3.13 but no Node.js. Using Python avoids requiring host package installation.
2. **Image-based install**: The official `devkitpro/devkitarm` image (1.51 GB) has devkitARM, libctru, examples, and dkp-pacman pre-installed. This bypasses the broken package server entirely.
3. **Path extraction**: Source paths that don't exist on the host (like container-internal paths) are copied to `/tmp/dkp-compile-*` before mounting.

## Verification

```
✓ devkitpro  connected
✓ github     connected
✓ rea        connected
```

Toolchain status output:
- podman: ok (podman version 5.5.2)
- image docker.io/devkitpro/devkitarm: present
- arm-none-eabi-gcc (devkitARM) 16.1.0
- /opt/devkitpro/devkitARM/arm-none-eabi/lib/3dsx.specs
- libctru.a present
- 3ds examples present

Compile test:
- Source: /opt/devkitpro/examples/3ds/graphics/printing/hello-world
- Exit code: 0
- Output: dkp-compile-hello-world.3dsx (124260 bytes)