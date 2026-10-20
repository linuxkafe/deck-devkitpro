# Roadmap

## [HIGH] Project scaffolding + reconnaissance
- Impact: High — foundation for everything else
- Effort: Low
- Status: done
- Notes: AES scaffold created, kanban initialised, Deck verified reachable
  with podman 5.5.2 and GCC 15.1.1. devkitpro not yet installed.

## [HIGH] Install devkitpro in podman container on Deck
- Impact: High — without this there is nothing to expose
- Effort: Medium
- Status: todo
- Ticket: T002
- Notes: devkitpro-pacman + devkitARM + libctru. Container must be rootless
  and isolated from host SteamOS. Official install path is
  `https://apt.devkitpro.org/install-devkitpro-pacman` — SteamOS is
  Arch-based so the pacman-style install is used, not apt.

## [HIGH] Implement MCP server exposing 3DS compile tooling
- Impact: High — the delivery mechanism for this OpenCode session
- Effort: Medium
- Status: todo
- Ticket: T003
- Notes: Node.js MCP server, stdio transport. Tools: `compile_3ds`, `clean`,
  `toolchain_status`, `list_libraries`.

## [MEDIUM] Wire MCP into OpenCode config
- Impact: Medium — makes the server usable from this session
- Effort: Low
- Status: todo
- Ticket: T004
- Notes: `.opencode/config.json` MCP entry pointing at the Deck-side server.

## [HIGH] End-to-end 3DS hello-world compile verification
- Impact: High — proves the whole chain works
- Effort: Medium
- Status: todo
- Ticket: T005
- Notes: minimal libctru hello-world → `.3dsx` via MCP → server → podman →
  devkitARM.

## [LOW] Harden: logging, retry, container lifecycle
- Impact: Low — operational polish
- Effort: Low
- Status: todo
- Notes: container start/stop automation, build log capture, retry on transient
  SSH failures.

## [LOW] Additional devkitpro libraries
- Impact: Low — expand as projects need them
- Effort: Low
- Status: todo
- Notes: `dkp-pacman -S <lib>` as needed. Not part of the initial scope.

## [DISCOVERED mid-task] Broken AES hook symlinks
- Impact: Medium — pre-commit/pre-review hooks were non-functional
- Effort: Low
- Status: done
- Notes: The installed AES skill ships 13 hooks as symlinks pointing to a
  non-existent `.aes/hooks/`. Real implementations live at
  `/opt/aes/.aes/hooks/`. Copied them into the project's `.aes/hooks/`.