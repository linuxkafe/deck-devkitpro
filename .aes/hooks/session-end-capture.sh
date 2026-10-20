#!/usr/bin/env bash
# session-end-capture.sh — Session end hook to capture chat insights
# Runs at session end, extracts insights from transcript, generates SD-META docs
# Usage: bash .aes/hooks/session-end-capture.sh

set -euo pipefail

# Source shared ID allocator
AES_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$AES_ROOT/scripts/lib/id-alloc.sh"

# Both values are read by the python3 blocks below via os.environ, so they must
# be exported. They were not, and the python side falls back to hardcoded
# /opt/aes paths — meaning this hook wrote shadow docs into the AES repo even
# when run inside a scaffolded project.
# LEARNING_DIR comes from the sourced resolver (shadow_store_dir) instead of
# being re-hardcoded, so AES_SHADOW_DIR / AES_PROJECT_ROOT / $PWD/.aes/shadow
# are honoured.
export AES_ROOT
LEARNING_DIR="$(shadow_store_dir)"
export LEARNING_DIR
EXTRACTOR="$AES_ROOT/scripts/chat-insight-extractor.sh"

# Find session transcript (Claude Code stores in ~/.claude/transcripts/)
find_transcript() {
	# Try environment variable first
	if [ -n "${CLAUDE_TRANSCRIPT:-}" ] && [ -f "$CLAUDE_TRANSCRIPT" ]; then
		echo "$CLAUDE_TRANSCRIPT"
		return 0
	fi
	# Fallback: find most recent transcript in ~/.claude/transcripts/
	if [ -d "$HOME/.claude/transcripts" ]; then
		find "$HOME/.claude/transcripts" -name '*.json' -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-
		return 0
	fi
	# Fallback: check current directory for transcript
	if [ -f "$AES_ROOT/session-transcript.json" ]; then
		echo "$AES_ROOT/session-transcript.json"
		return 0
	fi
	return 1
}

main() {
	transcript=$(find_transcript) || {
		echo "No session transcript found" >&2
		return 0 # Don't fail session
	}

	echo "Found transcript: $transcript" >&2

	# Extract insights
	if [ ! -x "$EXTRACTOR" ]; then
		echo "Extractor not executable: $EXTRACTOR" >&2
		return 0
	fi

	insights_json=$("$EXTRACTOR" "$transcript" 2>/dev/null || echo '[]')

	# Parse JSON and generate SD-META docs
	count=$(echo "$insights_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

	if [ "$count" -eq 0 ]; then
		echo "No insights extracted" >&2
		return 0
	fi

	echo "Extracted $count insight(s)" >&2

	# Generate shadow docs for each insight
	echo "$insights_json" | python3 -c "
import sys, json, os, subprocess, glob, re
insights = json.load(sys.stdin)
learning_dir = os.environ.get('LEARNING_DIR', '/opt/aes/aes/shadow')
aes_root = os.environ.get('AES_ROOT', '/opt/aes')

# Find max existing SD-OPS ID from filesystem
existing = glob.glob(os.path.join(learning_dir, 'SD-OPS-*.md'))
max_num = 0
for f in existing:
    m = re.search(r'SD-OPS-(\d+)', os.path.basename(f))
    if m:
        num = int(m.group(1))
        if num > max_num:
            max_num = num

for i, insight in enumerate(insights):
    max_num += 1
    sid = f'SD-OPS-{max_num:03d}'
    
    # Build shadow doc
    pattern = insight.get('pattern', '')
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    doc = f'''---
id: {sid}
type: lesson
epistemic_state: NÃO-VERIFICÁVEL
okf_version: '0.2'
title: \"Chat insight: {pattern[:60]}\"
synthesis: \"Extracted from session transcript: {pattern}\"
pointer:
  path: {os.environ.get('TRANSCRIPT', 'session-transcript.json')}
  content_hash: ''
generated:
  by: session-end-capture.sh
  at: {datetime.now().strftime('%Y-%m-%d')}
score:
  activation: 0.5
  pinned: false
  centrality: 0.3
provenance:
  source_ticket: T267
  source_conversation: chat-insight-capture
  generated_by: scripts/chat-insight-extractor.sh
  generated_at: {datetime.now().strftime('%Y-%m-%d')}
created: {datetime.now().strftime('%Y-%m-%d')}
last_accessed: {datetime.now().strftime('%Y-%m-%d')}
tags: [chat-insight, auto-extracted, SD-META]
---

# {sid} — Chat Insight (Auto-extracted)

## Pattern Matched
{pattern}

## Context
Auto-extracted from session transcript by session-end-capture hook.

## Synthesis
Insight captured during conversation: {pattern}
'''
    path = os.path.join(learning_dir, f'{sid}.md')
    with open(path, 'w') as f:
        f.write(doc)
    print(f'Generated {sid}.md')
"

	echo "Generated $count SD-META shadow doc(s)" >&2
}

main "$@"
