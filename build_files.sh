#!/bin/bash
set -e

echo "=== Building NxTech 2K26 on Vercel ==="

# 1. Upgrade pip and install all project requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 2. Ensure user-level site-packages are visible to python3
USER_SITE=$(python3 -m site --user-site 2>/dev/null || echo "")
if [ -n "$USER_SITE" ]; then
    export PYTHONPATH="${PYTHONPATH}:${USER_SITE}"
fi
export PATH="${PATH}:/root/.local/bin:~/.local/bin"

# 3. Ensure staticfiles output directory exists
mkdir -p staticfiles

# 4. Collect static files
python3 manage.py collectstatic --noinput --clear

echo "=== Build Complete ==="


