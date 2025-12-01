#!/usr/bin/env python
"""Verify theming_sitetheme table exists"""
import os
import django
import sys

# Try LMS settings first, then CMS
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.envs.devstack')
    django.setup()
except:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.envs.devstack')
    django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'theming_sitetheme'")
result = cursor.fetchone()
if result:
    print('SUCCESS: theming_sitetheme table exists')
    sys.exit(0)
else:
    print('ERROR: theming_sitetheme table does NOT exist!')
    sys.exit(1)

