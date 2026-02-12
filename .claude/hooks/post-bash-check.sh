#!/bin/bash
# PostToolUse hook for Bash — detects git commit and git push
# Reads tool input/output from stdin (JSON)

input=$(cat)

if echo "$input" | grep -q "git commit"; then
  echo "COMMIT COMPLETED: Ask the user if they want to push to remote."
fi

if echo "$input" | grep -q "git push"; then
  echo "PUSH COMPLETED: Check if a major phase or pipeline step just finished. If so, suggest /compact or /clear to free context before starting the next phase. Read canon/session-state.md to determine phase boundaries."
fi
