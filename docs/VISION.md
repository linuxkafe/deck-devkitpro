# Vision

## Problem

Nintendo 3DS homebrew development requires the **devkitpro** toolchain
(devkitARM, libctru, FUSE, etc.). Installing devkitpro is heavyweight — it
pulls hundreds of megabytes of cross-compilers, libraries, and example code.
Doing it on a desktop machine means the dev environment is tied to one box;
doing it on the Steam Deck (which has a fast x86_64 CPU, plenty of RAM, and
is already where the user lives) is attractive but fragile if done directly on
the host SteamOS image.

Without a containerised toolchain:
- The Deck's host state is polluted by devkitpro's pacman repo and files.
- Updating SteamOS can break the toolchain silently.
- There is no clean way to share or reproduce the environment.
- This OpenCode session has no programmatic way to invoke 3DS compilation —
  it would have to shell out over SSH ad hoc, with no standard interface.

## Solution

Run devkitpro inside a **podman rootless container** on the Steam Deck, and
expose its capabilities to this OpenCode session through a **MCP (Model
Context Protocol) server**.

- The container is built from a declarative `docker/` context and runs on the
  Deck, isolated from the host SteamOS.
- The MCP server (Node.js, running on the Deck) wraps devkitpro commands and
  presents them as MCP tools — `compile_3ds`, `clean`, `list_libraries`,
  `toolchain_status`, etc.
- This OpenCode session consumes the MCP server via `.opencode/config.json`,
  so 3DS compilation is available as first-class tooling rather than an
  ad-hoc SSH command.

## Value

- **Reproducibility**: the container image is versioned; rebuild it and the
  toolchain state is identical.
- **Isolation**: devkitpro never touches the Deck's host filesystem.
- **Portability**: the same MCP server can serve any agent that speaks MCP.
- **Verifiability**: success is a real `.3dsx` produced from a real source
  tree using the containerised devkitARM, not a simulated compile.

## Success Criteria

1. `podman run` on the Deck produces a working devkitpro environment.
2. `dkp-pacman -S devkitARM` succeeds inside the container.
3. The MCP server is reachable from this OpenCode session and exposes at
   least `compile_3ds`.
4. A minimal 3DS homebrew hello-world compiles to `.3dsx` through the MCP
   server end-to-end.