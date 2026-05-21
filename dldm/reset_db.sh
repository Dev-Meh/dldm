#!/usr/bin/env bash
set -o errexit

echo "=== Force Database Reset ==="

# Remove all migration files except __init__.py
find dldm/*/migrations/ -name "*.py" -not -name "__init__.py" -delete

# Create fresh migrations
echo "Creating fresh migrations..."
python dldm/manage.py makemigrations auths --noinput
python dldm/manage.py makemigrations homepages --noinput  
python dldm/manage.py makemigrations Salesmanager --noinput
python dldm/manage.py makemigrations SystemAdmin --noinput
python dldm/manage.py makemigrations StockManager --noinput

# Apply migrations
echo "Applying migrations..."
python dldm/manage.py migrate --fake-initial

# Create superuser
echo "Creating superuser..."
python dldm/manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dldm.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

echo "=== Database Reset Complete ==="
