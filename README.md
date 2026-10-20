# DevKitPro Deck

[Decky Loader](https://decky.xyz) plugin to control the **devkitpro** toolchain
on the Steam Deck. devkitpro runs inside a rootless podman container and
exposes a **Model Context Protocol (MCP) server** that this OpenCode session
consumes for Nintendo 3DS compilation.

## Features

- **On-demand service control** — start/stop the MCP server from the Decky
  overlay in Gaming Mode
- **Status panel** — image present, container running, toolchain version
- **Toolchain info** — devkitARM version, libctru, 3dsx.specs, examples
- **CLI** — `devkitpro-deck` command for SSH/headless control
- **MCP server** — exposes `compile_3ds`, `clean`, `toolchain_status`,
  `list_libraries`, `list_groups` tools to OpenCode

## Architecture

```
Steam Deck (deck@steamdeck)
├── podman container (docker.io/devkitpro/devkitarm)
│   ├── devkitARM 16.1.0
│   ├── libctru
│   ├── dkp-pacman
│   └── 3DS examples
├── MCP server (mcp/server.py) — stdio transport
├── Decky plugin (main.py + src/index.tsx)
└── CLI (cli.py)
```

## Prerequisites

- Steam Deck with Decky Loader installed
- Rootless podman (comes with SteamOS)
- devkitpro image pulled (the plugin can pull it)

## Installation

### Quick

```bash
curl -fsSL https://raw.githubusercontent.com/linuxkafe/deck-devkitpro/main/install.sh | sh
```

The installer downloads the plugin, installs it to the Decky plugins directory,
and restarts the plugin loader.

### Manual

```bash
# Clone and copy
git clone https://github.com/linuxkafe/deck-devkitpro.git
sudo cp -r deck-devkitpro /home/deck/homebrew/plugins/devkitpro-deck
# Restart Decky (Settings > Reload)
```

## Usage

### Decky Plugin

Open Game Mode → Decky → DevKitPro Deck. Shows:
- Image status (present/missing)
- Container status (running/stopped)
- Toolchain version
- Pull button if image missing

### CLI

```bash
devkitpro-deck status        # Full status JSON
devkitpro-deck pull          # Pull the devkitpro image
devkitpro-deck toolchain     # Toolchain info
devkitpro-deck version       # Plugin version
```

### MCP Tools (OpenCode)

Once the MCP server is running, this OpenCode session can use:

| Tool | Description |
|------|-------------|
| `compile_3ds(source_path)` | Compile a 3DS project to `.3dsx` |
| `clean(project_path)` | Clean build artifacts |
| `toolchain_status()` | Check toolchain health |
| `list_libraries()` | List available libraries |
| `list_groups()` | List predefined groups |

## Troubleshooting

### Image not found
```bash
devkitpro-deck pull
```

### Plugin not loading
- Restart Decky: Settings → Reload
- Check logs: `journalctl -u plugin_loader`

### Container not starting
```bash
podman run --rm docker.io/devkitpro/devkitarm echo "OK"
```

## License

MIT