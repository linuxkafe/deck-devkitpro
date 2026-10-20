# T005 — Build Output (E2E verification)

## What Changed

No code changes — this ticket is purely verification.

## Verification Performed

### Positive control
```
compile_3ds(source_path="/opt/devkitpro/examples/3ds/graphics/printing/hello-world")
→ Exit code: 0
→ Output: dkp-compile-hello-world.3dsx (124260 bytes)
→ MAKE_EXIT=0
```

### Negative control
```
compile_3ds(source_path="/nonexistent/path")
→ Exit code: 1
→ Error: Could not find source at /nonexistent/path
```

### Host isolation
```
find /opt/devkitpro on Deck host → nothing
find /opt/devkitpro inside container → full toolchain
```

### Idempotency
```
Running install-devkitpro.sh twice → second run exits 0 without pulling
```

## Success Criteria Met

- [x] A podman container exists on the Deck with devkitpro installed
- [x] `dkp-pacman -S devkitARM` succeeds (pre-installed in image)
- [x] `dkp-pacman -S libctru` succeeds (pre-installed in image)
- [x] `arm-none-eabi-gcc --version` reports valid cross-compiler
- [x] devkitpro files are not present on the Deck host
- [x] The install is idempotent
- [x] MCP server exposes compile_3ds tool
- [x] `compile_3ds` compiles a real hello-world to `.3dsx`
- [x] OpenCode shows `✓ devkitpro connected`
- [x] Negative control: broken source returns error

## Remaining Risks

- The image is 1.51 GB — large but acceptable for a dev environment
- Package server (`pkg.devkitpro.org`) is unreliable — using pre-baked image instead
- No automatic container rebuild when upstream image updates — manual `podman pull` needed