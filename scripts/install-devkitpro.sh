#!/bin/bash
# install-devkitpro.sh — idempotent install of the devkitpro devkitARM container
# on the Steam Deck.
#
# What it does:
#   1. Verifies the Deck is reachable via SSH.
#   2. Pulls the official devkitpro/devkitarm image (rootless podman).
#   3. Verifies the toolchain inside the image: devkitARM, libctru, 3dsx.specs.
#
# What it does NOT do:
#   - install anything on the host. devkitpro lives only inside the container.
#   - require root. Runs entirely as the unprivileged `deck` user.
#
# Idempotent: safe to run repeatedly. If the image is already present and
# healthy, it exits 0 without pulling.
set -euo pipefail

DECK="${DECK:-deck@steamdeck}"
IMAGE="${DKP_IMAGE:-docker.io/devkitpro/devkitarm}"

# --- helpers ---------------------------------------------------------------
log()  { printf '[install-devkitpro] %s\n' "$*"; }
die()  { printf '[install-devkitpro] ERROR: %s\n' "$*" >&2; exit 1; }

ssh_cmd() {
  ssh -o ConnectTimeout=10 \
      -o StrictHostKeyChecking=no \
      -o BatchMode=yes \
      -o LogLevel=ERROR \
      "$DECK" "$@"
}

# --- step 1: reachability --------------------------------------------------
log "Checking Deck reachability: $DECK"
if ! ssh_cmd true 2>/dev/null; then
  die "cannot reach $DECK via SSH. Check the Deck is on and SSH is enabled."
fi
log "Deck reachable."

# --- step 2: podman present on Deck? --------------------------------------
log "Checking podman on Deck"
if ! ssh_cmd command -v podman >/dev/null 2>&1; then
  die "podman not found on Deck. Install it first (e.g. 'sudo pacman -S podman')."
fi
DK_PODMAN_VER=$(ssh_cmd 'podman --version 2>/dev/null')
log "podman on Deck: $DK_PODMAN_VER"

# --- step 3: pull image (idempotent) --------------------------------------
log "Ensuring image present: $IMAGE"
if ssh_cmd "podman images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null" \
     | grep -qF "$IMAGE:latest"; then
  log "Image already present locally."
else
  log "Pulling $IMAGE ..."
  if ! ssh_cmd "podman pull --quiet '$IMAGE'" 2>&1; then
    die "failed to pull $IMAGE. Check the Deck has network access."
  fi
  log "Image pulled."
fi

# --- step 4: verify toolchain inside the image -----------------------------
log "Verifying toolchain inside the image..."
VERIFY=$(ssh_cmd "podman run --rm '$IMAGE' bash -c '
  set -e
  GCC=\$(command -v arm-none-eabi-gcc || echo /opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc)
  \$GCC --version | head -1
  test -f /opt/devkitpro/devkitARM/arm-none-eabi/lib/3dsx.specs || exit 11
  test -f /opt/devkitpro/libctru/lib/libctru.a || exit 12
  dkp-pacman -Ss libctru 2>/dev/null | grep -q libctru || exit 13
  echo OK
' 2>&1")
log "$VERIFY"
case "$VERIFY" in
  *OK) log "Toolchain verification passed." ;;
  *)   die "Toolchain verification failed:\n$VERIFY" ;;
esac

log "Install complete."
log "  Image:    $IMAGE"
log "  Container: run as rootless on the Deck"
log "  Compile:  podman run --rm $IMAGE make -C <project>"