#!/bin/bash

# Script to fix migrations on Docker server
# Run this on your server: bash run_migrations_on_server.sh

echo "=========================================="
echo "Open edX Migration Fix Script"
echo "=========================================="
echo ""

# Check if container exists
if ! docker ps -a | grep -q edx_lms; then
    echo "ERROR: edx_lms container not found!"
    echo "Available containers:"
    docker ps -a
    exit 1
fi

echo "1. Checking LMS container status..."
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' edx_lms 2>/dev/null)
echo "   Container status: $CONTAINER_STATUS"

if [ "$CONTAINER_STATUS" != "running" ]; then
    echo "   Starting LMS container..."
    docker start edx_lms
    sleep 5
fi

echo ""
echo "2. Running LMS migrations..."
docker exec edx_lms python manage.py lms migrate --settings=devstack
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -eq 0 ]; then
    echo "   ✓ LMS migrations completed successfully"
else
    echo "   ✗ LMS migrations had errors (exit code: $MIGRATE_EXIT)"
fi

echo ""
echo "3. Running theming migrations specifically..."
docker exec edx_lms python manage.py lms migrate theming --settings=devstack
THEMING_EXIT=$?

if [ $THEMING_EXIT -eq 0 ]; then
    echo "   ✓ Theming migrations completed successfully"
else
    echo "   ✗ Theming migrations had errors (exit code: $THEMING_EXIT)"
fi

echo ""
echo "4. Verifying theming_sitetheme table exists..."
docker exec edx_lms python manage.py lms shell --settings=devstack << 'PYTHON_EOF'
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'theming_sitetheme'")
result = cursor.fetchone()
if result:
    print("   ✓ Table 'theming_sitetheme' EXISTS")
else:
    print("   ✗ Table 'theming_sitetheme' DOES NOT EXIST")
    print("   Attempting to create table manually...")
    try:
        from django.core.management import call_command
        call_command('migrate', 'theming', verbosity=2, interactive=False)
        cursor.execute("SHOW TABLES LIKE 'theming_sitetheme'")
        if cursor.fetchone():
            print("   ✓ Table created successfully!")
        else:
            print("   ✗ Failed to create table")
    except Exception as e:
        print(f"   ✗ Error: {e}")
PYTHON_EOF

echo ""
echo "5. Creating/Updating Site record..."
docker exec edx_lms python manage.py lms shell --settings=devstack << 'PYTHON_EOF'
from django.contrib.sites.models import Site
from django.conf import settings
try:
    domain = getattr(settings, 'LMS_ROOT_URL', 'http://localhost:18000').replace('http://', '').replace('https://', '')
    platform_name = getattr(settings, 'PLATFORM_NAME', 'Open edX')
    site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': platform_name})
    site.domain = domain
    site.name = platform_name
    site.save()
    if created:
        print(f"   ✓ Site created: {site.domain}")
    else:
        print(f"   ✓ Site updated: {site.domain}")
except Exception as e:
    print(f"   ✗ Error creating site: {e}")
PYTHON_EOF

echo ""
echo "6. Running CMS migrations..."
if docker ps -a | grep -q edx_cms; then
    docker exec edx_cms python manage.py cms migrate --settings=devstack
    docker exec edx_cms python manage.py cms migrate theming --settings=devstack
    echo "   ✓ CMS migrations completed"
else
    echo "   ⚠ CMS container not found, skipping CMS migrations"
fi

echo ""
echo "=========================================="
echo "Migration fix completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart LMS container: docker compose restart lms"
echo "2. Check logs: docker logs edx_lms -f"
echo "3. Test the site: curl http://localhost:18000"

