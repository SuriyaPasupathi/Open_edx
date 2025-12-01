#!/bin/bash

# Script to check and run theming migrations
# Run this inside LMS container: docker exec edx_lms bash /app/check_theming_migrations.sh

echo "=========================================="
echo "Checking Theming App Migrations"
echo "=========================================="
echo ""

echo "1. Checking installed apps..."
python manage.py lms shell --settings=devstack -c "from django.conf import settings; apps = [app for app in settings.INSTALLED_APPS if 'theming' in app.lower()]; print('Found theming apps:', apps)" || echo "Failed to check apps"

echo ""
echo "2. Listing all available migrations..."
python manage.py lms showmigrations --settings=devstack | grep -i theming || echo "No theming migrations found"

echo ""
echo "3. Checking app label..."
python manage.py lms shell --settings=devstack << 'PYEOF'
try:
    from openedx.core.djangoapps.theming.models import SiteTheme
    print(f"App label: {SiteTheme._meta.app_label}")
    print(f"App name: {SiteTheme._meta.app_config.name}")
    print(f"Model name: {SiteTheme._meta.db_table}")
except Exception as e:
    print(f"Error: {e}")
PYEOF

echo ""
echo "4. Checking if theming_sitetheme table exists..."
python manage.py lms shell --settings=devstack -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES LIKE \"theming_sitetheme\"'); result = cursor.fetchone(); print('Table EXISTS' if result else 'Table DOES NOT EXIST')"

echo ""
echo "5. Attempting to run migrations with different app names..."
echo "   Trying: openedx.core.djangoapps.theming"
python manage.py lms migrate openedx.core.djangoapps.theming --settings=devstack --noinput 2>&1 | head -20

echo ""
echo "   Trying: theming"
python manage.py lms migrate theming --settings=devstack --noinput 2>&1 | head -20

echo ""
echo "=========================================="
echo "Check completed!"
echo "=========================================="

