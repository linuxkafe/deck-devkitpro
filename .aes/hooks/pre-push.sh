#!/bin/sh
# Pre-push hook for AES
# Blocks pushes if `make check` fails (the structural gate against red pushes)
set -e

echo ""
echo "══════════════════════════════════════════════════"
echo "  Pre-Push Verification Gate"
echo "══════════════════════════════════════════════════"

if [ ! -f "aes/kanban.md" ]; then
	echo "  Not in an AES project — skipping"
	exit 0
fi

# T322 — agent lease check. Two agents on one machine must not silently push
# over each other. This is the PREVENTION layer, and it lives here rather than
# in a plugin because it is the one that can actually refuse: opencode's prompt
# hook has no typed rejection API, so a plugin can warn but never block.
#
# Deliberately a WARNING with a counted override, not a wall. A human who cannot
# get past a gate has no route forward, and a wall with no door is an invitation
# to disable everything at once. The AES already has the precedent: debt-gate
# COUNTS gate overrides. Refuted here, not banned.
if [ -x "scripts/agent-lease.sh" ]; then
	LEASE_OUT="$(scripts/agent-lease.sh list 2>/dev/null || true)"
	LEASE_COUNT="$(printf '%s' "$LEASE_OUT" | grep -c '^lease:' || true)"
	if [ "${LEASE_COUNT:-0}" -gt 0 ]; then
		echo ""
		echo "  ┌─ [aes/lease] outros agentes declare âmbito neste projecto:"
		printf '%s\n' "$LEASE_OUT" | sed 's/^/  │ /'
		echo "  │ Se estás a empurrar trabalho que sobrepõe a esse âmbito, coordena"
		echo "  │ antes. Para registar a sobreposição em vez de a negar:"
		echo "  │   scripts/agent-lease.sh check --scope <ambito> --override"
		echo "  └─"
		echo ""
	fi
fi

echo "  Running: make check"
echo ""

if ! make check; then
	echo ""
	echo "  ❌ PUSH BLOCKED: make check failed"
	echo "  Fix all quality gate failures before pushing."
	echo "  To bypass (emergency only): git push --no-verify"
	echo ""
	exit 1
fi

echo ""
echo "  ✅ All quality gates passed — push allowed"
echo ""
exit 0
