#!/usr/bin/env bash
# Session start hook - auto-loads GF regime and skills
# Installed by make install-session-hooks

set -euo pipefail

echo "[session-start] Initializing AES session..."

# Load GF regime (AES-native, non-blocking)
if python3 -c "from aes.gf.regime import GFRegime" 2>/dev/null; then
	echo "[session-start] GF regime available (AES-native)"
fi

# Load AES skills (if skill loader exists)
if [ -f scripts/load-skills.sh ]; then
	echo "[session-start] Loading AES skills..."
	bash scripts/load-skills.sh 2>/dev/null || true
fi

# Load debate partner protocol
if [ -f prompts/debate-partner.md ]; then
	echo "[session-start] Debate partner protocol loaded"
fi

# Load ILHA memory context (non-blocking)
if python3 -m aes.gf.wake 2>/dev/null; then
	echo "[session-start] ILHA memory context loaded"
else
	echo "[session-start] ILHA memory unavailable (first session?)"
fi

echo "[session-start] Session initialized"
