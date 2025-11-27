#!/bin/bash

# Resolve repo root
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate virtual environment (fallback to absolute path if relative fails)
if [ -f "$ROOT_DIR/../env/bin/activate" ]; then
	source "$ROOT_DIR/../env/bin/activate"
elif [ -f "/home/suriya-vcw/Desktop/suriya work/env/bin/activate" ]; then
	source "/home/suriya-vcw/Desktop/suriya work/env/bin/activate"
else
	echo "[WARN] Python venv not found. Proceeding without activating a venv."
fi

# Set environment variables for configuration files
export LMS_CFG="/home/suriya-vcw/Desktop/suriya work/edx-platform/lms.env.yml"
export CMS_CFG="/home/suriya-vcw/Desktop/suriya work/edx-platform/cms.env.yml"

cd "$ROOT_DIR" || exit 1

# NOTE: This script does NOT start MySQL or MongoDB.
# Ensure those are running elsewhere if your config requires them.

# Optional: start caches if you want (commented out by default)
# sudo systemctl start redis-server || true
# sudo systemctl start memcached || memcached -p 11211 -u nobody -d

echo "Starting LMS service on port 18000..."
python manage.py lms runserver 18000 --settings=devstack &

sleep 2

echo "Starting CMS service on port 18010..."
python manage.py cms runserver 18010 --settings=devstack &

sleep 2

echo "Starting Celery workers and beat for LMS/CMS..."
# Use built-in helper to start all celery workers/beat
bash "$ROOT_DIR/start_celery_services.sh" &

echo "Both web services and Celery workers are starting in the background."
echo "Access LMS at http://localhost:18000"
echo "Access CMS at http://localhost:18010"

echo ""
echo "Service port status (listening sockets):"
if command -v lsof >/dev/null 2>&1; then
	lsof -i -P -n | grep -E ":(18000|18010|6379|11211)\b" || true
elif command -v ss >/dev/null 2>&1; then
	ss -ltnp | grep -E ":(18000|18010|6379|11211)\b" || true
else
	echo "Install 'lsof' or use 'ss' to check ports."
fi

echo ""
echo "To stop web services: pkill -f 'manage.py.*runserver'"
echo "To stop Celery services: bash $ROOT_DIR/stop_celery_services.sh"
