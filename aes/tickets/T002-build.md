# T002 — Build Output (devkitpro install)

## What Changed

| File | Intent |
|------|--------|
| `scripts/install-devkitpro.sh` | Idempotent Deck-side install script |
| `docker/` | (reserved for future Dockerfile) |

## What Was Untouched

- The Deck's host SteamOS — devkitpro lives only inside the container
- No system packages installed on the host
- No root/sudo required

## Remaining Risks

- R1: Image pull requires internet on Deck (verified working)
- R2: Container uses ~1.5 GB disk (verified: 203 GB free)
- R3: Package server (`pkg.devkitpro.org`) is Cloudflare-protected; the official image bypasses this but is 1.51 GB

## Verification

```
[install-devkitpro] Checking Deck reachability: deck@steamdeck
[install-devkitpro] Deck reachable.
[install-devkitpro] podman on Deck: podman version 5.5.2
[install-devkitpro] Image already present locally.
[install-devkitpro] arm-none-eabi-gcc (devkitARM) 16.1.0
OK
[install-devkitpro] Toolchain verification passed.
[install-devkitpro] Install complete.
```

Host isolation verified: `find /opt/devkitpro` on host returns nothing; all toolchain files live inside the container.