#!/bin/bash

# Setup Git Hooks for Price Spy

HOOKS_DIR=".git/hooks"
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit"

echo "Installing pre-commit hook..."

cat << 'EOF' > "$PRE_COMMIT_HOOK"
#!/bin/bash

# Atomic Commit Guard (Warning Mode)
STAGED_FILES=$(git diff --cached --name-only | wc -l)
LIMIT=10

if [ "$STAGED_FILES" -gt "$LIMIT" ]; then
    echo "❌ ERROR: You have staged $STAGED_FILES files. Limit is $LIMIT."
    echo "    Large commits are blocked to ensure atomic changes."
    echo "    Use 'git commit --no-verify' if you MUST bypass this guard."
    exit 1
fi

exit 0
EOF

chmod +x "$PRE_COMMIT_HOOK"

echo "✅ Pre-commit hook installed successfully!"
echo "   It will warn you if you stage more than 10 files."
