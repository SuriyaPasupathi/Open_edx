#!/usr/bin/env python
"""Create Site record for Open edX"""
import os
import django
import sys

# Try LMS settings first, then CMS
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.envs.devstack')
    django.setup()
except:
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.envs.devstack')
        django.setup()
    except Exception as e:
        print(f'ERROR: Failed to setup Django - {e}')
        sys.exit(1)

from django.contrib.sites.models import Site
from django.conf import settings

try:
    domain = getattr(settings, 'LMS_ROOT_URL', 'http://localhost:18000').replace('http://', '').replace('https://', '')
    platform_name = getattr(settings, 'PLATFORM_NAME', 'Open edX')
    site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': platform_name})
    site.domain = domain
    site.name = platform_name
    site.save()
    print(f'SUCCESS: Site ready - {site.domain}')
except Exception as e:
    print(f'WARNING: Site creation error - {e}')

