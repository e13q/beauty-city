#!/usr/bin/env bash
# Exit on error
set -o errexit
pip install -r requirements.txt

# Apply any outstanding database migrations
python backend/manage.py migrate
python backend/manage.py shell
exec(open("supplement_data.py", encoding="utf-8").read())
exit
