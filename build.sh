#!/bin/bash
set -e

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "Running migrations..."
python3 run_migrations.py

echo ""
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo ""
echo "Build complete! Vehicle data will load automatically on app startup."
