#!/bin/bash

# Script to manually fix migrations on the server
# Run this inside the LMS container: docker exec -it edx_lms bash /app/fix_migrations.sh

echo "=========================================="
echo "Running Open edX Migrations"
echo "=========================================="

echo ""
echo "1. Running LMS migrations..."
python manage.py lms migrate --settings=devstack
if [ $? -eq 0 ]; then
    echo "✓ LMS migrations completed"
else
    echo "✗ LMS migrations failed"
fi

echo ""
echo "2. Running theming migrations..."
python manage.py lms migrate theming --settings=devstack
if [ $? -eq 0 ]; then
    echo "✓ Theming migrations completed"
else
    echo "✗ Theming migrations failed"
fi

echo ""
echo "3. Checking if theming_sitetheme table exists..."
python manage.py lms shell --settings=devstack -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES LIKE \"theming_sitetheme\"'); result = cursor.fetchone(); print('✓ Table exists' if result else '✗ Table does NOT exist')"

echo ""
echo "4. Creating Site record if needed..."
python manage.py lms shell --settings=devstack -c "from django.contrib.sites.models import Site; from django.conf import settings; domain = getattr(settings, 'LMS_ROOT_URL', 'http://localhost:18000').replace('http://', '').replace('https://', ''); platform_name = getattr(settings, 'PLATFORM_NAME', 'Open edX'); site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': platform_name}); site.domain = domain; site.name = platform_name; site.save(); print('✓ Site ready: ' + site.domain)"

echo ""
echo "=========================================="
echo "Migration check completed!"
echo "=========================================="

