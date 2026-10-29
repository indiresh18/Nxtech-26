#!/bin/bash
echo "=== Building NxTech 2K26 on Vercel ==="
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear

if [ -n "$DATABASE_URL" ]; then
    echo "=== Running Database Migrations on Supabase ==="
    python3 manage.py migrate --noinput
fi

echo "=== Build Complete ==="

