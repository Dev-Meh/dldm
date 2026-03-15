#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python dldm/manage.py collectstatic --noinput
python dldm/manage.py migrate

# Create superuser if it doesn't exist
python dldm/manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dldm.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF
