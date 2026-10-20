#!/usr/bin/env python3
"""DevKitPro-Deck CLI - controla o servico devkitpro no Steam Deck.

Usage:
    devkitpro-deck status        Estado actual
    devkitpro-deck pull          Obtem a imagem devkitpro
    devkitpro-deck toolchain     Informacao da toolchain
    devkitpro-deck version       Versao do plugin

Exit codes: 0 ok, 1 erro.
"""

import argparse
import json
import os
import sys

# Compativel com o plugin Decky - reutiliza main.py
if os.path.exists(os.path.join(os.path.dirname(__file__), "main.py")):
    sys.path.insert(0, os.path.dirname(__file__))
    import main as backend
else:
    # Fallback: tenta o diretorio de plugins do Decky
    plugin_dirs = []
    for home in ["/home/deck", os.environ.get("HOME", "")]:
        p = os.path.join(home, "homebrew", "plugins")
        if os.path.isdir(p):
            plugin_dirs.append(p)
    for d in plugin_dirs:
        if not os.path.isdir(d):
            continue
        for plugin in os.listdir(d):
            mainpy = os.path.join(d, plugin, "main.py")
            if os.path.exists(mainpy) and "devkitpro" in plugin.lower():
                sys.path.insert(0, os.path.join(d, plugin))
                import main as backend
                break
        else:
            continue
        break
    else:
        print("ERROR: Could not find main.py backend")
        sys.exit(1)


def cmd_status(_args):
    status = backend.get_status()
    print(json.dumps(status, indent=2, default=str))


def cmd_pull(_args):
    result = backend.pull_image()
    print(json.dumps(result, indent=2))


def cmd_toolchain(_args):
    info = backend.toolchain_info()
    print(json.dumps(info, indent=2, default=str))


def cmd_version(_args):
    print("DevKitPro Deck v0.1.0")


def main():
    parser = argparse.ArgumentParser(
        prog="devkitpro-deck",
        description="Controla o servico devkitpro no Steam Deck.",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMANDO")

    sub.add_parser("status", help="Mostra o estado actual")
    sub.add_parser("pull", help="Obtem a imagem devkitpro")
    sub.add_parser("toolchain", help="Informacao da toolchain")
    sub.add_parser("version", help="Versao do plugin")

    args = parser.parse_args()
    dispatch = {
        "status": cmd_status,
        "pull": cmd_pull,
        "toolchain": cmd_toolchain,
        "version": cmd_version,
    }
    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()