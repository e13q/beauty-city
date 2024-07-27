#!/usr/bin/env bash
# Exit on error
set -o errexit
pip install -r requirements.txt
pip install gunicorn

# Apply any outstanding database migrations
python backend/manage.py migrate
