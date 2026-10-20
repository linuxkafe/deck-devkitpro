---
ticket: T002
title: Install devkitpro in podman container on Deck
sprint: sprint-02
priority: high
status: done
completed: 2026-10-20
created: 2026-10-20
---

# T002 — Install devkitpro in podman container on Deck

## Context

The Steam Deck (`deck@steamdeck`) has podman 5.5.2 and GCC 15.1.1 but
**no devkitpro**. devkitpro is the toolchain needed to compile Nintendo 3DS
homebrew (`devkitARM`, `libctru`, FUSE). Installing it directly on the host
SteamOS would pollute the host and risk breaking on OS updates. The chosen
approach is a rootless podman container that holds all devkitpro state.

The official install path is `https://apt.devkitpro.org/install-devkitpro-pacman`.
SteamOS is **Arch-based** (`ID=steamos`, `ID_LIKE=arch`), so the apt-based
installer does not apply — the pacman-based install is required instead.

## Acceptance Criteria

- [ ] A podman container exists on the Deck with devkitpro installed
- [ ] `dkp-pacman -S devkitARM` succeeds inside the container
- [ ] `dkp-pacman -S libctru` succeeds inside the container
- [ ] `arm-none-eabi-gcc --version` reports a valid cross-compiler inside the
      container
- [ ] devkitpro files are **not** present on the Deck host (verified with a
      find before/after)
- [ ] The install is idempotent — re-running the install script is a no-op

## Scope

**In scope:**
- Creating the podman container image with devkitpro
- installing devkitARM and libctru
- a script (`scripts/install-devkitpro.sh`) that performs the install on the
  Deck idempotently

**Out of scope:**
- the MCP server (T003)
- writing any 3DS source code
- devkitPPC or devkitA64

## Dependencies

- Deck reachable via SSH (`deck@steamdeck`) — verified at recon
- podman on Deck — verified at recon
- internet on Deck — verified at recon

## Rollback

`podman rm` the container. devkitpro files live only inside the container so
removing it removes the toolchain. The host is untouched.

## Known Risks

- **R1 — pacman repo availability.** devkitpro's pacman repository must be
  reachable from inside the container. If the container has no network, the
  install fails. Mitigation: verify container network before installing.
- **R2 — rootless podman limitations.** Some devkitpro packages may need
  privileges. Mitigation: run the container as the `deck` user (rootless);
  escalate only if a package explicitly fails and the user confirms.
- **R3 — disk space.** devkitpro + toolchains can exceed 1 GB. Mitigation:
  check `df -h` on the Deck before starting and surface it to the user.
- **R4 — SteamOS updates.** A container insulates devkitpro from host
  updates, but the podman runtime itself is host-provided. Mitigation: document
  the runtime dependency.

## Notes

The install must be scripted and idempotent. Never run privileged Deck
commands without explicit user confirmation (per CLAUDE.md Never Do).