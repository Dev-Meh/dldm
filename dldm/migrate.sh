#!/usr/bin/env bash
echo "Running Django migrations..."
cd dldm
python manage.py makemigrations
python manage.py migrate
echo "Migrations completed!"
