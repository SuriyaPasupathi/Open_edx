#!/bin/bash

# Set environment variables for Open edX configuration files
# MODIFIED: Auto-detect current directory path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LMS_CFG="$SCRIPT_DIR/lms.env.yml"
export CMS_CFG="$SCRIPT_DIR/cms.env.yml"

echo "Environment variables set:"
echo "LMS_CFG=$LMS_CFG"
echo "CMS_CFG=$CMS_CFG"
echo ""
echo "You can now run migration commands directly:"
echo "./manage.py lms migrate"
echo "./manage.py lms migrate --database=student_module_history"
echo "./manage.py cms migrate"
