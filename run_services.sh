#!/bin/bash

# Activate virtual environment
source ../env/bin/activate

# Set environment variables
export LMS_CFG="/home/suriya-vcw/Desktop/manual build/edx-platform/lms.env.yml"
export CMS_CFG="/home/suriya-vcw/Desktop/manual build/edx-platform/cms.env.yml"

# Function to run LMS
run_lms() {
    echo "Starting LMS service..."
    python manage.py lms runserver 18000 --settings=devstack
}

# Function to run CMS
run_cms() {
    echo "Starting CMS service..."
    python manage.py cms runserver 18010 --settings=devstack
}

# Check if argument is provided
if [ "$1" = "lms" ]; then
    run_lms
elif [ "$1" = "cms" ]; then
    run_cms
else
    echo "Usage: $0 {lms|cms}"
    echo "  lms - Start Learning Management System on port 18000"
    echo "  cms - Start Content Management System (Studio) on port 18010"
fi
