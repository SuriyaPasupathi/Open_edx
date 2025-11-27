#!/bin/bash

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Stop Django runservers (LMS/CMS)
echo "Stopping LMS/CMS runserver processes..."
pkill -f "manage.py lms runserver" 2>/dev/null || true
pkill -f "manage.py cms runserver" 2>/dev/null || true

# Stop Celery services
echo "Stopping Celery workers/beat..."
bash "$ROOT_DIR/stop_celery_services.sh" 2>/dev/null || true

# Show port status for common services
echo ""
echo "Remaining listening ports (18000, 18010, 6379, 11211):"
if command -v lsof >/dev/null 2>&1; then
	lsof -i -P -n | grep -E ":(18000|18010|6379|11211)\b" || true
elif command -v ss >/dev/null 2>&1; then
	ss -ltnp | grep -E ":(18000|18010|6379|11211)\b" || true
else
	echo "Install 'lsof' or use 'ss' to check ports."
fi

echo "Done."
