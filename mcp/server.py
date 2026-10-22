#!/usr/bin/env python3
"""
deck-3dsdevkit MCP Server

Exposes the Nintendo 3DS devkitARM toolchain to OpenCode via the Model
Context Protocol. Runs on the Steam Deck, calls podman directly.

Container: docker.io/devkitpro/devkitarm (rootless podman on Deck).
Transport: stdio.
"""
import asyncio
import os
import re
import subprocess
import sys

from mcp.server.mcpserver import MCPServer


IMAGE = os.environ.get("DKP_IMAGE", "docker.io/devkitpro/devkitarm")
DEVKITPRO = "/opt/devkitpro"
DEVKITARM = f"{DEVKITPRO}/devkitARM"

AZAHAR = os.environ.get("AZAHAR", "/home/deck/Applications/squashfs-root/usr/bin/azahar")
SDMC = os.environ.get("SDMC", "/run/media/mmcblk0p1/Emulation/storage/azahar/sdmc")


def die(msg: str) -> None:
    print(f"[devkitpro-mcp] FATAL: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def sanitize_path(p: str | None) -> str | None:
    """Reject paths with shell metacharacters or traversal sequences."""
    if not isinstance(p, str) or not p.strip():
        return None
    s = p.strip()
    if re.search(r"[\s;|&$`(){}!\\\"'<>]", s):
        return None
    return s


def run_podman(args: list[str], timeout: int = 180) -> tuple[int, str, str]:
    """Run a podman command, return (exit_code, stdout, stderr)."""
    cmd = ["podman"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "podman not found"


# ── Server setup ─────────────────────────────────────────────────────────────
mcps = MCPServer(name="deck-3dsdevkit", version="0.1.0")


@mcps.tool(
    name="compile_3ds",
    description=(
        "Compile a Nintendo 3DS project to .3dsx using the devkitARM "
        "toolchain inside the podman container on the Steam Deck. "
        "The project directory must contain a valid Makefile."
    ),
)
async def compile_3ds(source_path: str) -> str:
    resolved = sanitize_path(source_path)
    if not resolved:
        return "ERROR: Invalid source_path: must be a non-empty string without shell metacharacters."
    if not os.path.isabs(resolved):
        resolved = os.path.abspath(resolved)

    # If the path doesn't exist on the host, try to extract it from the container
    if not os.path.exists(resolved):
        # Try to copy from container to a temp dir on the Deck
        tmp_dir = f"/tmp/dkp-compile-{os.path.basename(resolved)}"
        os.makedirs(tmp_dir, exist_ok=True)
        extract_cmd = [
            "run", "--rm",
            "--volume", f"{tmp_dir}:{tmp_dir}",
            IMAGE,
            "bash", "-c",
            f"""
if [ -d {resolved} ]; then
  cp -r {resolved}/* {tmp_dir}/ 2>/dev/null || true
  cp -r {resolved}/. {tmp_dir}/ 2>/dev/null || true
  echo "COPIED"
else
  echo "ERROR: Path {resolved} not found in container"
  exit 1
fi
""",
        ]
        rc, stdout, stderr = run_podman(extract_cmd, timeout=60)
        if rc != 0:
            return f"ERROR: Could not find source at {resolved}: {stderr or stdout}"
        resolved = tmp_dir

    container_cmd = [
        "run", "--rm",
        "--volume", f"{resolved}:{resolved}",
        "--workdir", resolved,
        IMAGE,
        "bash", "-c",
        f"""
export DEVKITPRO={DEVKITPRO}
export DEVKITARM={DEVKITARM}
export PATH=$DEVKITARM/bin:/opt/devkitpro/tools/bin:$PATH
if [ ! -f Makefile ]; then
  echo "ERROR: No Makefile found at {resolved}/Makefile"
  exit 1
fi
echo "=== building {resolved} ==="
make 2>&1
rc=$?
echo "MAKE_EXIT=$rc"
ls -la *.3dsx 2>/dev/null || true
exit $rc
""",
    ]

    rc, stdout, stderr = run_podman(container_cmd, timeout=180)
    output = f"Exit code: {rc}\n\nSTDOUT:\n{stdout}"
    if stderr:
        output += f"\nSTDERR:\n{stderr}"
    return output


@mcps.tool(
    name="clean",
    description="Clean build artifacts for a 3DS project by running `make clean` inside the container.",
)
async def clean(project_path: str) -> str:
    resolved = sanitize_path(project_path)
    if not resolved:
        return "ERROR: Invalid project_path."
    if not os.path.isabs(resolved):
        resolved = os.path.abspath(resolved)

    container_cmd = [
        "run", "--rm",
        "--volume", f"{resolved}:{resolved}",
        "--workdir", resolved,
        IMAGE,
        "bash", "-c",
        f"""
export DEVKITPRO={DEVKITPRO}
export DEVKITARM={DEVKITARM}
export PATH=$DEVKITARM/bin:/opt/devkitpro/tools/bin:$PATH
[ -f Makefile ] && make clean 2>&1 || echo "No Makefile found; nothing to clean"
""",
    ]
    rc, stdout, stderr = run_podman(container_cmd, timeout=30)
    output = f"Exit code: {rc}\n\n{stdout}"
    if stderr:
        output += f"\nSTDERR:\n{stderr}"
    return output


@mcps.tool(
    name="toolchain_status",
    description="Check the health of the devkitpro toolchain: compiler version, libctru presence, installed examples, and local podman/image status.",
)
async def toolchain_status() -> str:
    lines = []

    # Local health
    rc, stdout, _ = run_podman(["--version"])
    lines.append(f"podman: {'ok' if rc == 0 else 'MISSING'} ({stdout.strip()})")

    rc, stdout, _ = run_podman(["images", "--format", "{{.Repository}}:{{.Tag}}"])
    has_image = IMAGE + ":latest" in stdout
    lines.append(f"image {IMAGE}: {'present' if has_image else 'MISSING'}")

    # Inside container
    container_cmd = [
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
    rc, stdout, stderr = run_podman(container_cmd, timeout=30)
    lines.append("--- container output ---")
    lines.append(stdout)
    if stderr:
        lines.append(stderr)
    lines.append(f"toolchain_status exit: {rc}")

    return "\n".join(lines)


@mcps.tool(
    name="list_libraries",
    description="List devkitpro library packages available in the container.",
)
async def list_libraries() -> str:
    container_cmd = [
        "run", "--rm", IMAGE, "bash", "-c",
        "dkp-pacman -Sl 2>/dev/null | head -80",
    ]
    rc, stdout, stderr = run_podman(container_cmd, timeout=30)
    output = f"Exit code: {rc}\n\n{stdout}"
    if stderr:
        output += f"\nSTDERR:\n{stderr}"
    return output


@mcps.tool(
    name="list_groups",
    description="List devkitpro predefined install groups (3ds-dev, gba-dev, nds-dev, etc.).",
)
async def list_groups() -> str:
    container_cmd = [
        "run", "--rm", IMAGE, "bash", "-c",
        "dkp-pacman -Sg 2>/dev/null",
    ]
    rc, stdout, stderr = run_podman(container_cmd, timeout=30)
    output = f"Exit code: {rc}\n\n{stdout}"
    if stderr:
        output += f"\nSTDERR:\n{stderr}"
    return output


def _xauth_path() -> str:
    env = os.environ.get("XAUTHORITY", "")
    if env:
        return env
    import glob
    cands = sorted(glob.glob("/run/user/1000/xauth_*"))
    return cands[0] if cands else ""


@mcps.tool(
    name="debug_headless",
    description=(
        "Run a Nintendo 3DS .3dsx under the Azahar emulator in headless mode on "
        "the Steam Deck, assert it renders N frames and self-terminates, and "
        "return the gate result. Used for behavioural debugging of 3DS builds."
    ),
)
async def debug_headless(rom_path: str, frames: int = 120, timeout: int = 180) -> str:
    resolved = sanitize_path(rom_path)
    if not resolved:
        return "ERROR: Invalid rom_path: must be a non-empty string without shell metacharacters."
    if not os.path.isabs(resolved):
        resolved = os.path.abspath(resolved)
    if not os.path.exists(resolved):
        return f"ERROR: ROM not found at {resolved}"
    try:
        frames = int(frames)
    except (TypeError, ValueError):
        frames = 120
    if frames < 1:
        frames = 1
    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        timeout = 180
    if timeout < 10:
        timeout = 10

    if not os.path.exists(AZAHAR) or not os.access(AZAHAR, os.X_OK):
        return f"ERROR: Azahar not found or not executable at {AZAHAR}"

    os.makedirs(SDMC, exist_ok=True)
    result_file = os.path.join(SDMC, "sm_gate_result.txt")
    try:
        os.remove(result_file)
    except FileNotFoundError:
        pass
    try:
        with open(os.path.join(SDMC, "sm_max_frames"), "w") as f:
            f.write(str(frames))
    except OSError as e:
        return f"ERROR: could not write frame budget to SDMC: {e}"

    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["QT_QPA_PLATFORM"] = "xcb"
    xauth = _xauth_path()
    if xauth:
        env["XAUTHORITY"] = xauth

    cmd = ["/usr/bin/timeout", str(timeout), AZAHAR, resolved]
    rc = -1
    stdout = ""
    stderr = ""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15, env=env)
        rc = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc = -1
        stdout = (e.stdout or "") if isinstance(e.stdout, str) else (e.stdout.decode("utf-8", "replace") if e.stdout else "")
        stderr = (e.stderr or "") if isinstance(e.stderr, str) else (e.stderr.decode("utf-8", "replace") if e.stderr else "")
        stderr += "\n[outer timeout]"
    except FileNotFoundError as e:
        return f"ERROR: failed to launch emulator: {e}"

    result_text = ""
    if os.path.exists(result_file):
        try:
            with open(result_file) as f:
                result_text = f.read()
        except OSError as e:
            result_text = f"ERROR reading result file: {e}"

    got_frames = ""
    got_max = ""
    with_core = ""
    for line in result_text.splitlines():
        if line.startswith("frames="):
            got_frames = line.split("=", 1)[1].strip()
        elif line.startswith("max_frames="):
            got_max = line.split("=", 1)[1].strip()
        elif line.startswith("with_core="):
            with_core = line.split("=", 1)[1].strip()

    out = []
    out.append(f"ROM: {resolved}")
    out.append(f"Requested frames: {frames}")
    out.append(f"Emulator exit code: {rc}")
    if result_text:
        out.append("--- gate result ---")
        out.append(result_text.strip())
    else:
        out.append("ERROR: no sm_gate_result.txt produced by the guest")
    if got_frames:
        status = "PASS" if got_frames == str(frames) and got_max == str(frames) else "FAIL"
        out.append(f"GATE {status}: frames={got_frames} max_frames={got_max} with_core={with_core}")
    if stderr.strip():
        out.append("--- stderr (tail) ---")
        out.append(stderr.strip()[-2000:])
    return "\n".join(out)



# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ensure unbuffered output for MCP stdio transport
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    print(f"[devkitpro-mcp] Starting server (IMAGE={IMAGE})", file=sys.stderr, flush=True)
    mcps.run(transport="stdio")
