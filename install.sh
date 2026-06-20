#!/usr/bin/env bash
# Restore the agentic-ai-stack skill + aas-* subagents into ~/.claude
set -euo pipefail

CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents"
cp -R "$SRC/skills/agentic-ai-stack" "$CLAUDE_DIR/skills/"
cp "$SRC"/agents/aas-*.md "$CLAUDE_DIR/agents/"

echo "Installed:"
echo "  skill  -> $CLAUDE_DIR/skills/agentic-ai-stack"
echo "  agents -> $CLAUDE_DIR/agents/aas-*.md"
echo "Restart Claude Code; the skill is /agentic-ai-stack and agents are subagent_type: aas-*."
