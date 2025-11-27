#!/bin/bash

# Activate virtual environment
source ../env/bin/activate

# Set environment variables for configuration files
export LMS_CFG="/home/suriya-vcw/Desktop/suriya work/edx-platform/lms.env.yml"
export CMS_CFG="/home/suriya-vcw/Desktop/suriya work/edx-platform/cms.env.yml"

echo "Running LMS migrations..."
python manage.py lms migrate --settings=devstack

echo "Running LMS student module history migrations..."
python manage.py lms migrate --database=student_module_history --settings=devstack

echo "Running CMS migrations..."
python manage.py cms migrate --settings=devstack

echo "All migrations completed successfully!"
