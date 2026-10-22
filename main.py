#!/usr/bin/env python3
"""DevKitPro Deck — Decky plugin backend.

Wraps the podman container that holds devkitpro and exposes callable
functions for the Decky UI: status, start/stop, toolchain info.
"""

import asyncio
import json
import os
import re
import shlex
import subprocess
import sys
from typing import Any, Optional

try:
    import decky
except ImportError:
    decky = None  # type: ignore[assignment]

IMAGE = os.environ.get("DKP_IMAGE", "docker.io/devkitpro/devkitarm")
DEVKITARM = "/opt/devkitpro/devkitARM"
SERVICE_NAME = "devkitpro-deck"


def log(msg: str) -> None:
    if decky is not None:
        decky.logger.info(msg)


def _user_env() -> dict:
    env = os.environ.copy()
    uid = str(os.getuid())
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    return env


def _podman(args: list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Run a podman command, return (exit_code, stdout, stderr)."""
    cmd = ["podman"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_user_env(),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "podman not found"


def _fault(msg: str) -> dict:
    return {"ok": False, "error": msg}


def image_present() -> bool:
    """Check if the devkitpro image is pulled locally."""
    rc, stdout, _ = _podman(["images", "--format", "{{.Repository}}:{{.Tag}}"])
    return IMAGE + ":latest" in stdout


def container_running() -> bool:
    """Check if the devkitpro container is currently running."""
    rc, stdout, _ = _podman(["ps", "--format", "{{.Repository}}:{{.Tag}}", "--filter", f"image={IMAGE}"])
    return IMAGE + ":latest" in stdout


def toolchain_info() -> dict:
    """Get toolchain info from inside the container."""
    if not image_present():
        return {"ok": False, "error": "Image not pulled", "version": None}

    cmd = [
        "run", "--rm", IMAGE, "bash", "-c",
        f"""
export DEVKITARM={DEVKITARM}
export PATH=$DEVKITARM/bin:/opt/devkitpro/tools/bin:$PATH
echo "=== gcc ==="
arm-none-eabi-gcc --version 2>&1 | head -1
echo "=== specs ==="
ls /opt/devkitpro/devkitARM/arm-none-eabi/lib/3dsx.specs 2>&1
echo "=== libctru ==="
find /opt/devkitpro -name 'libctru*' 2>/dev/null | head -5
echo "=== examples ==="
ls /opt/devkitpro/examples/3ds/ 2>/dev/null | head -10
echo "STATUS=OK"
""",
    ]
    rc, stdout, stderr = _podman(cmd, timeout=30)
    if rc != 0:
        return {"ok": False, "error": stderr or stdout, "version": None}

    version = None
    for line in stdout.splitlines():
        if "devkitARM" in line:
            m = re.search(r"devkitARM\)\s+([\d.]+)", line)
            if m:
                version = m.group(1)
                break

    return {
        "ok": True,
        "version": version,
        "output": stdout,
        "error": "",
    }


def debug_status() -> dict:
    """Check debug (headless emulator) dependencies on the Deck."""
    import glob
    azahar = "/home/deck/Applications/squashfs-root/usr/bin/azahar"
    sdmc = "/run/media/mmcblk0p1/Emulation/storage/azahar/sdmc"
    xauths = glob.glob("/run/user/1000/xauth_*")
    return {
        "azahar_present": os.path.exists(azahar) and os.access(azahar, os.X_OK),
        "azahar_path": azahar,
        "sdmc_exists": os.path.isdir(sdmc),
        "sdmc_path": sdmc,
        "xauth_present": len(xauths) > 0,
        "ok": os.path.exists(azahar) and os.path.isdir(sdmc),
    }


def configure_debug() -> dict:
    """Create SD card directories needed by the headless debug gate."""
    sdmc = "/run/media/mmcblk0p1/Emulation/storage/azahar/sdmc"
    try:
        os.makedirs(sdmc, exist_ok=True)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "sdmc": sdmc, "message": "Debug SD directory ready"}


def get_status() -> dict:
    """Get full service status for the UI."""
    status = {
        "image_present": image_present(),
        "container_running": container_running(),
        "toolchain": toolchain_info(),
        "error": "",
    }
    return status


def pull_image() -> dict:
    """Pull the devkitpro image if not present."""
    if image_present():
        return {"ok": True, "message": "Image already present"}
    rc, stdout, stderr = _podman(["pull", IMAGE], timeout=300)
    if rc != 0:
        return _fault(f"Failed to pull image: {stderr or stdout}")
    return {"ok": True, "message": "Image pulled"}


class Plugin:
    """DevKitPro Deck Decky plugin."""

    def __init__(self):
        self.settings = {}
        self._sync_task: Optional[asyncio.Task] = None

    async def _unload(self) -> None:
        """Called when the plugin is unloaded."""
        pass

    async def _uninstall(self) -> None:
        """Called when the plugin is uninstalled."""
        pass

    async def get_status(self) -> dict:
        """Return service status for the UI."""
        return get_status()

    async def pull_image(self) -> dict:
        """Pull the devkitpro image."""
        return pull_image()

    async def toolchain_info(self) -> dict:
        """Return toolchain info."""
        return toolchain_info()

    async def debug_status(self) -> dict:
        """Return headless debug dependency status."""
        return debug_status()

    async def configure_debug(self) -> dict:
        """Configure headless debug dependencies on the Deck."""
        return configure_debug()


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Smoke test: run get_status and print JSON
    result = get_status()
    print(json.dumps(result, indent=2))