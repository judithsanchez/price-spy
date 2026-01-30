#!/bin/bash
# Check if app/ changes are accompanied by docs/ or README.md changes

# Get staged files
STAGED_FILES=$(git diff --cached --name-only)

# Count app changes
APP_CHANGES=$(echo "$STAGED_FILES" | grep "^app/" | wc -l)

# Count doc changes (including GEMINI.md as it's a key dev doc)
DOC_CHANGES=$(echo "$STAGED_FILES" | grep -E "^docs/|^README.md|^GEMINI.md" | wc -l)

if [ "$APP_CHANGES" -gt 0 ] && [ "$DOC_CHANGES" -eq 0 ]; then
  echo "❌ ERROR: Code changed in app/ but no changes found in docs/, README.md, or GEMINI.md."
  echo "Please update documentation or bypass with 'git commit --no-verify' if documentation is not applicable."
  exit 1
fi

exit 0
