#!/usr/bin/env bash
set -o errexit

echo "=== Starting Build Process ==="
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

echo "=== Installing Requirements ==="
pip install -r requirements.txt

echo "=== Collecting Static Files ==="
python dldm/manage.py collectstatic --noinput

echo "=== Running Migrations ==="
python dldm/manage.py migrate

echo "=== Creating Superuser ==="
python dldm/manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dldm.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

echo "=== Build Complete ==="
