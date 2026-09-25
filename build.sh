#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== 1. Upgrading Pip & Installing Dependencies ==="
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "=== 2. Collecting Static Files ==="
python manage.py collectstatic --no-input

echo "=== 3. Applying Database Migrations ==="
python manage.py makemigrations event4u_app
python manage.py migrate

echo "=== 4. Seeding Initial Demo Data (Admin, Events, Passes) ==="
python seed_db.py || true

echo "=== 5. Deployment Build Ready! ==="
