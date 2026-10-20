#!/bin/bash
# Post-learn hook for AES
# Runs sleep consolidation after learn phase completes

set -euo pipefail

echo ""
echo "=================================================="
echo "  POST-LEARN: Running sleep consolidation (make sleep)"
echo "=================================================="

# Run sleep to consolidate shadow docs: recompute scores, demote stale, merge dupes, regenerate INDEX.md
if make sleep 2>&1; then
	echo "  Sleep consolidation: COMPLETED"
else
	echo "  Sleep consolidation: FAILED (non-blocking)"
	# Non-fatal — consolidation failure shouldn't block the pipeline
fi

echo "=================================================="
echo ""

exit 0
