#!/bin/bash

# Script to fix theming_sitetheme table issue
# Run on server: docker exec edx_lms bash /app/fix_theming_table.sh

echo "=========================================="
echo "Fixing theming_sitetheme Table Issue"
echo "=========================================="
echo ""

echo "1. Checking if theming_sitetheme table exists..."
python manage.py lms shell --settings=devstack -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES LIKE \"theming_sitetheme\"'); result = cursor.fetchone(); print('Table EXISTS' if result else 'Table DOES NOT EXIST')"

echo ""
echo "2. Checking migration status for theming app..."
python manage.py lms showmigrations theming --settings=devstack

echo ""
echo "3. Checking django_migrations table for theming entries..."
python manage.py lms shell --settings=devstack -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT * FROM django_migrations WHERE app LIKE \"%theming%\"'); results = cursor.fetchall(); print('Found migrations:', len(results)); [print(f'  - {r}') for r in results]"

echo ""
echo "4. Attempting to fake-unapply and reapply theming migrations..."
python manage.py lms migrate theming zero --settings=devstack --fake || echo "Failed to fake-unapply"
python manage.py lms migrate theming --settings=devstack --fake || echo "Failed to fake-apply"

echo ""
echo "5. If fake doesn't work, creating table directly..."
python manage.py lms shell --settings=devstack << 'PYEOF'
from django.db import connection
cursor = connection.cursor()

# Check if table exists
cursor.execute("SHOW TABLES LIKE 'theming_sitetheme'")
if cursor.fetchone():
    print("Table already exists, skipping creation")
else:
    print("Creating theming_sitetheme table...")
    try:
        # Create the table based on the migration
        cursor.execute("""
            CREATE TABLE theming_sitetheme (
                id INT AUTO_INCREMENT PRIMARY KEY,
                theme_dir_name VARCHAR(255) NOT NULL,
                site_id INT NOT NULL,
                FOREIGN KEY (site_id) REFERENCES django_site(id),
                INDEX idx_theming_sitetheme_site_id (site_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("SUCCESS: Table created!")
        
        # Mark migration as applied
        from django.db import transaction
        with transaction.atomic():
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('theming', '0001_initial', NOW())
                ON DUPLICATE KEY UPDATE applied = NOW()
            """)
        print("SUCCESS: Migration marked as applied!")
    except Exception as e:
        print(f"ERROR creating table: {e}")
PYEOF

echo ""
echo "6. Verifying table exists..."
python manage.py lms shell --settings=devstack -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES LIKE \"theming_sitetheme\"'); result = cursor.fetchone(); print('SUCCESS: Table exists!' if result else 'ERROR: Table still missing!')"

echo ""
echo "=========================================="
echo "Fix completed!"
echo "=========================================="

