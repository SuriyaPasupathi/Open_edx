#!/bin/bash

# This script runs migrations for Open edX in Docker
# Environment variables LMS_CFG and CMS_CFG should be set by docker-compose

echo "Running LMS migrations..."
python manage.py lms migrate --settings=devstack || echo "LMS migrations failed or already applied"

echo "Running LMS student module history migrations..."
python manage.py lms migrate --database=student_module_history --settings=devstack || echo "Student module history migrations failed or already applied"

echo "Running theming migrations..."
python manage.py lms migrate theming --settings=devstack || echo "Theming migrations failed or already applied"

echo "Running CMS migrations..."
python manage.py cms migrate --settings=devstack || echo "CMS migrations failed or already applied"

echo "Running CMS theming migrations..."
python manage.py cms migrate theming --settings=devstack || echo "CMS theming migrations failed or already applied"

echo "All migrations completed!"
