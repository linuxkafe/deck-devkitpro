# Requirements

## Functional

### F-1 — devkitpro installed on the Deck
- devkitpro-pacman must be installed and functional inside a podman container
  on `deck@steamdeck`.
- `devkitARM` (the ARM11/ARM9 cross-compiler toolchain) must be installable
  via `dkp-pacman -S devkitARM`.
- `libctru` (the 3DS homebrew library) must be present so a minimal program
  links and produces a `.3dsx`.

### F-2 — MCP server exposing 3DS tooling
- A Node.js MCP server runs on the Deck and exposes tools over the MCP
  protocol.
- At minimum these tools must exist:
  - `compile_3ds(source_path, output_path?)` — compile a 3DS source tree to
    `.3dsx` using the containerised devkitARM. Returns the output path and
    build log.
  - `clean(project_path)` — remove build artifacts for a project.
  - `toolchain_status()` — report devkitpro version, installed libraries, and
    whether the toolchain is healthy.
  - `list_libraries()` — list devkitpro library groups available via pacman.
- The server must be reachable from this OpenCode session.

### F-3 — OpenCode consumption
- `.opencode/config.json` must wire the MCP server so tools appear in this
  session's toolset without manual invocation.
- Compiling via the MCP tool must work end-to-end from this session.

### F-4 — Build verification
- A minimal 3DS hello-world (using libctru) must compile to `.3dsx` through
  the full chain: MCP → server → podman container → devkitARM.

## Non-Functional

- **Performance**: compile latency is bounded by the Deck's CPU and the
  container's I/O. A trivial hello-world must compile in under 60 seconds.
- **Security**: the container runs rootless where possible. No credentials or
  Deck passwords are stored in this repository — SSH keys are used, and the
  Deck's `deck` user is unprivileged.
- **Maintainability**: the podman container context (`docker/`) and the MCP
  server (`mcp/`) are separate, each with a `Makefile` target. The Deck-side
  install is a single idempotent script (`scripts/install-devkitpro.sh`).
- **Reproducibility**: the container image is built from `docker/` and tagged;
  rebuilding yields a deterministic toolchain state.
- **Isolation**: devkitpro must never modify the Deck's host SteamOS. All
  devkitpro files live inside the container's mount.

## Constraints

- **Language**: JavaScript (Node.js) for the MCP server; bash for Deck-side
  orchestration scripts.
- **Deployment target**: the Steam Deck (`deck@steamdeck`, SteamOS, Arch-based).
- **Runtime**: podman 5.x rootless containers on the Deck.
- **Target platform**: Nintendo 3DS (ARM11 + ARM9, `arm-none-eabi-gcc` via
  devkitARM, `-specs=3dsx.specs`).
- **MCP version**: Model Context Protocol, stdio transport (server runs on
  Deck, client runs locally in OpenCode).

## Out of Scope

- Writing 3DS application code — only the toolchain and its MCP exposure.
- Emulation or running 3DS binaries — compilation only.
- Wii/Wii U/Switch toolchains — devkitPPC/devkitA64 are not targets.
- Distributing devkitpro binaries — the container builds them from the
  official pacman repository at runtime.