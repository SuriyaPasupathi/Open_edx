#!/bin/bash

# ============================================================================
# Start LMS with MFE Integration
# ============================================================================
# This script properly sets all environment variables and starts LMS
# ============================================================================

echo "=========================================="
echo "Starting LMS with Learning MFE Support"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set paths
EDX_PLATFORM_DIR="$SCRIPT_DIR"
VENV_DIR="$(dirname "$SCRIPT_DIR")/env"
LMS_CONFIG_FILE="$EDX_PLATFORM_DIR/lms.env.yml"

# Check if config file exists
if [ ! -f "$LMS_CONFIG_FILE" ]; then
    echo "❌ ERROR: Config file not found at: $LMS_CONFIG_FILE"
    exit 1
fi

echo "✓ Config file found: $LMS_CONFIG_FILE"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ ERROR: Virtual environment not found at: $VENV_DIR"
    exit 1
fi

echo "✓ Virtual environment found: $VENV_DIR"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Set required environment variables
export LMS_CFG="$LMS_CONFIG_FILE"
export DJANGO_SETTINGS_MODULE=lms.envs.devstack
export SERVICE_VARIANT=lms

echo "✓ Environment variables set:"
echo "  LMS_CFG=$LMS_CFG"
echo "  DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "  SERVICE_VARIANT=$SERVICE_VARIANT"
echo ""

# Check if MySQL is running
if ! systemctl is-active --quiet mysql; then
    echo "⚠ WARNING: MySQL is not running"
    echo "  Start it with: sudo systemctl start mysql"
    echo ""
fi

# Check if MongoDB is running
if ! systemctl is-active --quiet mongod; then
    echo "⚠ WARNING: MongoDB is not running"
    echo "  Start it with: sudo systemctl start mongod"
    echo ""
fi

# Check if port 18000 is already in use
if lsof -Pi :18000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠ WARNING: Port 18000 is already in use"
    echo "  Kill existing process with: pkill -f 'manage.py lms runserver'"
    echo ""
fi

echo "=========================================="
echo "Starting LMS Development Server"
echo "=========================================="
echo ""
echo "LMS will be available at: http://localhost:18000"
echo "Press CTRL+C to stop"
echo ""
echo "=========================================="
echo ""

# Start LMS
python manage.py lms runserver 0.0.0.0:18000 --settings=devstack

