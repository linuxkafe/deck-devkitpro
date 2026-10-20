#!/bin/sh
# Prepare-commit-msg hook for AES
# Adds bypass trailer to commit message when AES_BYPASS is set

BYPASS_FILE=".git/AES_BYPASS"
if [ -f "$BYPASS_FILE" ]; then
	BYPASS_CONTENT=$(cat "$BYPASS_FILE")
	rm -f "$BYPASS_FILE"

	echo "" >>"$1"
	echo "Bypass: $BYPASS_CONTENT" >>"$1"
	echo "Bypass-User: $(git config user.name) <$(git config user.email)>" >>"$1"
	echo "Bypass-Time: $(date -Iseconds)" >>"$1"
fi

exit 0
