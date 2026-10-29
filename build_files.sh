#!/bin/bash
echo "=== Building NxTech 2K26 on Vercel ==="
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "=== Build Complete ==="

