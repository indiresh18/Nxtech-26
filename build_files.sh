#!/bin/bash
set -e

echo "=== Building NxTech 2K26 on Vercel ==="

# Clean any existing virtual environment
rm -rf .venv

# Create fresh virtual environment using uv or python3
if command -v uv &> /dev/null; then
    echo ">> Detected uv: creating virtual environment..."
    uv venv .venv
else
    echo ">> Using python3 -m venv..."
    python3 -m venv .venv
fi

# Locate the Python executable inside virtualenv (Linux vs Windows)
if [ -f ".venv/bin/python" ]; then
    VENV_PYTHON=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
else
    VENV_PYTHON="python3"
fi

echo ">> Installing dependencies using $VENV_PYTHON..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt --python "$VENV_PYTHON" || "$VENV_PYTHON" -m pip install -r requirements.txt
else
    "$VENV_PYTHON" -m pip install -r requirements.txt
fi

# Ensure staticfiles output directory exists
mkdir -p staticfiles

echo ">> Collecting static files..."
"$VENV_PYTHON" manage.py collectstatic --noinput --clear

# Mirror static assets so both /static/ and root route resolutions succeed
mkdir -p staticfiles/static
cp -r static/* staticfiles/static/ 2>/dev/null || true
cp -r staticfiles/admin staticfiles/static/ 2>/dev/null || true

if [ -n "$DATABASE_URL" ]; then
    echo "=== Running Database Migrations on Supabase ==="
    "$VENV_PYTHON" manage.py migrate --noinput
fi

# Clean up temporary build virtual environment so it doesn't inflate the Lambda package
rm -rf .venv

echo "=== Build Complete ==="
