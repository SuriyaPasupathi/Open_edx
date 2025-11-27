#!/bin/bash

# Open edX Celery Services Shutdown Script
# This script stops all Celery services for Open edX

echo "🛑 Stopping Open edX Celery Services..."
echo "======================================="

# Get script directory for absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set absolute paths for PID files
LMS_PIDFILE="$SCRIPT_DIR/celery_lms.pid"
CMS_PIDFILE="$SCRIPT_DIR/celery_cms.pid"
BEAT_PIDFILE="$SCRIPT_DIR/celery_beat.pid"
FLOWER_PIDFILE="$SCRIPT_DIR/celery_flower.pid"

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "⚠️  Force killing $service_name..."
                kill -9 "$pid"
            fi
            echo "   ✅ $service_name stopped"
        else
            echo "   ℹ️  $service_name was not running (stale PID file)"
        fi
        rm -f "$pid_file"
    else
        echo "   ℹ️  No PID file found for $service_name"
    fi
}

# Stop all services
stop_service "LMS Worker" "$LMS_PIDFILE"
stop_service "CMS Worker" "$CMS_PIDFILE"
stop_service "Beat Scheduler" "$BEAT_PIDFILE"
stop_service "Flower Monitor" "$FLOWER_PIDFILE"

# Clean up any remaining celery processes
echo ""
echo "🧹 Cleaning up any remaining Celery processes..."
pkill -f 'celery.*worker' 2>/dev/null && echo "   ✅ Remaining workers stopped" || echo "   ℹ️  No remaining workers found"
pkill -f 'celery.*beat' 2>/dev/null && echo "   ✅ Remaining beat processes stopped" || echo "   ℹ️  No remaining beat processes found"
pkill -f 'celery.*flower' 2>/dev/null && echo "   ✅ Remaining flower processes stopped" || echo "   ℹ️  No remaining flower processes found"

echo ""
echo "🎉 All Celery services stopped successfully!"
echo ""
echo "📋 To verify, run: ps aux | grep celery"
echo "🚀 To restart, run: ./start_celery_services.sh"
