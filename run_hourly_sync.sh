#!/bin/sh
set -eu

cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
  . .venv/bin/activate
fi

python3 poll_legends.py poll
python3 poll_legends.py publish

if [ -z "$(git status --porcelain)" ]; then
  exit 0
fi

git add site work
if git diff --cached --quiet; then
  exit 0
fi

git commit -m "Update legend data"

git fetch origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  git rebase origin/main
fi

git push origin HEAD:main
