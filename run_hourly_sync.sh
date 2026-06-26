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

git add site
git commit -m "Update legend data"
git push
