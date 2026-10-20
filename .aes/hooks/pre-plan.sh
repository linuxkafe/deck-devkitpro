#!/bin/bash
# Pre-plan hook: runs `make wake` to load INDEX.md + open loops + current ticket.
set -e
echo ""
echo "══════════════════════════════════════════════════"
echo "  PRE-PLAN: Loading context via make wake"
echo "══════════════════════════════════════════════════"
make wake 2>&1 || echo "  ⚠  make wake failed — continuing without context"
echo "══════════════════════════════════════════════════"
echo ""
