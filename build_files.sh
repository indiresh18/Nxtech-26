#!/bin/bash
set -e

echo "=== Building NxTech 2K26 on Vercel ==="

# Use an isolated virtual environment to satisfy PEP 668 in uv-managed Python environments
if command -v uv &> /dev/null; then
    echo ">> Detected uv: creating isolated virtual environment..."
    uv venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    echo ">> Using python3 -m venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Ensure output directory exists and collect static assets
mkdir -p staticfiles
python manage.py collectstatic --noinput --clear

echo "=== Build Complete ==="


