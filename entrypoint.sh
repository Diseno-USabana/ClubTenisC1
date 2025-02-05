#!/bin/bash
echo ""
echo "Running migrations"
echo ""
python manage.py migrate

exec "$@"
