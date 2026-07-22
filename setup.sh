#!/bin/bash
# ============================================================================
# LeadOptimizer AI — one-command setup for the AI Sales Team
# Installs 14 Claude Code skills + 5 parallel sub-agents to ~/.claude
# so /sales commands work in ANY project on this machine.
#
# Vendored from https://github.com/zubair-trabzada/ai-sales-team-claude (MIT)
# by Zubair Trabzada — AI Workshop (https://www.skool.com/aiworkshop)
# ============================================================================
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILLS="$REPO_DIR/.claude/skills"
SRC_AGENTS="$REPO_DIR/.claude/agents"
DEST_SKILLS="$HOME/.claude/skills"
DEST_AGENTS="$HOME/.claude/agents"

if [ ! -f "$SRC_SKILLS/sales/SKILL.md" ]; then
    echo "Error: run this script from the lead-gen-ai-python repo (missing .claude/skills/sales)."
    exit 1
fi

echo ""
echo -e "${BLUE}LeadOptimizer AI — AI Sales Team setup${NC}"
echo -e "14 skills + 5 parallel sub-agents for Claude Code"
echo ""

echo -e "${BLUE}Installing skills → $DEST_SKILLS${NC}"
SKILL_COUNT=0
for dir in "$SRC_SKILLS"/sales*/; do
    name="$(basename "$dir")"
    mkdir -p "$DEST_SKILLS/$name"
    cp -R "$dir." "$DEST_SKILLS/$name/"
    echo -e "  ${GREEN}✓${NC} $name"
    SKILL_COUNT=$((SKILL_COUNT + 1))
done

echo -e "${BLUE}Installing sub-agents → $DEST_AGENTS${NC}"
AGENT_COUNT=0
mkdir -p "$DEST_AGENTS"
for agent in "$SRC_AGENTS"/sales-*.md; do
    cp "$agent" "$DEST_AGENTS/"
    echo -e "  ${GREEN}✓${NC} $(basename "$agent" .md)"
    AGENT_COUNT=$((AGENT_COUNT + 1))
done

echo -e "${BLUE}Checking Python environment...${NC}"
if command -v python3 &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} $(python3 --version 2>&1)"
    for pkg in reportlab bs4; do
        if python3 -c "import $pkg" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $pkg installed"
        else
            echo -e "  ${YELLOW}⚠${NC} $pkg missing — install with: ${CYAN}pip3 install reportlab beautifulsoup4${NC}"
        fi
    done
else
    echo -e "  ${YELLOW}⚠${NC} Python 3 not found — needed for prospect analysis + PDF reports"
fi

echo ""
echo -e "${GREEN}Done!${NC} $SKILL_COUNT skills and $AGENT_COUNT sub-agents installed."
echo ""
echo -e "${BLUE}Try these inside Claude Code:${NC}"
echo -e "  ${CYAN}/sales prospect <url>${NC}       Full analysis — 5 sub-agents in parallel"
echo -e "  ${CYAN}/sales quick <url>${NC}          60-second prospect snapshot"
echo -e "  ${CYAN}/sales qualify <url>${NC}        BANT + MEDDIC lead scoring"
echo -e "  ${CYAN}/sales contacts <url>${NC}       Find decision makers"
echo -e "  ${CYAN}/sales outreach <prospect>${NC}  Cold/warm outreach sequences"
echo -e "  ${CYAN}/sales report-pdf${NC}           Client-ready PDF pipeline report"
echo ""
