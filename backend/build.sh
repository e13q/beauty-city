#!/usr/bin/env bash
# Exit on error
set -o errexit
pip install -r requirements.txt
pip install gunicorn
pip install uvicorn

# Apply any outstanding database migrations
python backend/manage.py migrate
