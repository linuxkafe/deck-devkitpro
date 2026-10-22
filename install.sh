#!/bin/sh
# DevKitPro-Deck installer — installs the Decky plugin.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/linuxkafe/deck-3dsdevkit/main/install.sh | sh
#
# Options (env):
#   DKP_DECK_BRANCH     git ref to install (default: main)
#   DKP_DECK_PLUGIN_DIR override the Decky plugin directory

set -eu

REPO="linuxkafe/deck-3dsdevkit"
BRANCH="${DKP_DECK_BRANCH:-master}"
PLUGIN_NAME="devkitpro-deck"
PLUGIN_VERSION="0.1.0"

say()  { printf '\033[1;34m%s\033[0m\n' "$*"; }
warn() { printf '\033[1;33mWARN\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31mERROR\033[0m %s\n' "$*" >&2; exit 1; }

# Find Decky plugins directory
plugins_dir="${DKP_DECK_PLUGIN_DIR:-}"
if [ -z "$plugins_dir" ]; then
  for h in /home/deck/homebrew/plugins /home/*/.local/share/Steam/extensions/plugins; do
    if [ -d "$h" ]; then
      plugins_dir="$h"
      break
    fi
  done
  [ -n "$plugins_dir" ] || die "Decky plugins dir not found (set DKP_DECK_PLUGIN_DIR)"
fi

dest="$plugins_dir/$PLUGIN_NAME"
say "Installing $PLUGIN_NAME (v$PLUGIN_VERSION, branch=$BRANCH) into $dest"

# Download
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

if [ -d ".git" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  say "Installing from local repo..."
  cp -r . "$tmp/"
else
  say "Downloading from GitHub..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" -o "$tmp/plugin.tar.gz"
  tar -xzf "$tmp/plugin.tar.gz" -C "$tmp" --strip-components=1
fi

for required in plugin.json main.py; do
  [ -f "$tmp/$required" ] || die "archive is missing $required"
done

# Determine sudo needs
sudo_cmd=""
if [ -d "$plugins_dir" ]; then
  [ -w "$plugins_dir" ] || sudo_cmd="sudo"
elif [ -w "$(dirname "$plugins_dir" 2>/dev/null)" ]; then
  :
else
  sudo_cmd="sudo"
fi

# Backup existing
if [ -d "$dest" ]; then
  ts="$(date +%Y%m%d%H%M%S)"
  backup="$dest.bak.$ts"
  say "Backing up existing install to $backup"
  $sudo_cmd rm -rf "$backup" 2>/dev/null || true
  $sudo_cmd mv "$dest" "$backup"
fi

# Remove stale backups
for old in "$dest".bak.*; do
  if [ -d "$old" ]; then
    say "Removing stale backup $old"
    $sudo_cmd rm -rf "$old"
  fi
done

# Install
$sudo_cmd mkdir -p "$dest"
$sudo_cmd cp -r "$tmp"/. "$dest/"
if [ -n "$sudo_cmd" ]; then
  owner="$(stat -c %u:%g "$plugins_dir" 2>/dev/null || true)"
  [ -n "$owner" ] && $sudo_cmd chown -R "$owner" "$dest"
fi

# CLI wrapper
deck_home=""
case "$plugins_dir" in
  /home/*/homebrew/plugins) deck_home=${plugins_dir%/homebrew/plugins} ;;
  *) deck_home="$HOME" ;;
esac
bin_dir="$deck_home/.local/bin"
$sudo_cmd mkdir -p "$bin_dir"
cli_wrapper="$bin_dir/devkitpro-deck"
$sudo_cmd tee "$cli_wrapper" >/dev/null << CLIEOF
#!/bin/sh
exec python3 "$dest/cli.py" "\$@"
CLIEOF
$sudo_cmd chmod +x "$cli_wrapper"
case ":$PATH:" in
  *":$bin_dir:"*) ;;
  *) say "Tip: add $bin_dir to PATH to use 'devkitpro-deck' directly." ;;
esac

# Restart Decky
say "Restarting Decky plugin loader..."
if [ -n "$sudo_cmd" ]; then
  $sudo_cmd systemctl restart plugin_loader 2>/dev/null || true
fi
say "Plugin loader restarted."

say "Done. Open Game Mode and check Decky > DevKitPro Deck."
say "CLI: devkitpro-deck status"
say "To update: curl -fsSL https://raw.githubusercontent.com/$REPO/$BRANCH/install.sh | sh"