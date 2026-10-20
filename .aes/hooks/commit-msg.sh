#!/bin/sh
# Commit-msg hook for AES
# Validates the commit message format.
# Runs AFTER the commit message exists (unlike pre-commit, where
# .git/COMMIT_EDITMSG still holds the previous message).
# This is ENFORCEMENT: the commit cannot proceed without a valid message.

set -e

MSG_FILE="$1"
if [ -z "$MSG_FILE" ]; then
	exit 0
fi

if ! grep -qE '^(T[0-9]+|feat|fix|docs|chore|dogfood|meta|self|refactor|test|style|perf|ci|build|revert):' "$MSG_FILE" 2>/dev/null; then
	echo ""
	echo "══════════════════════════════════════════════════"
	echo "  Commit Message Convention Gate"
	echo "══════════════════════════════════════════════════"
	echo "  ⚠  Commit message does not follow convention:"
	echo "     Expected: ^(T\\d+|feat|fix|docs|chore|dogfood|meta|self|refactor|test|style|perf|ci|build|revert):"
	echo "     Actual: $(head -1 "$MSG_FILE")"
	echo ""
	exit 1
fi

exit 0
