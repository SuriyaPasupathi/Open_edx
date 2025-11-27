#!/bin/bash

# Open edX Celery Services Startup Script
# This script starts all necessary Celery services for Open edX

echo "🚀 Starting Open edX Celery Services..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "set_env.sh" ]; then
    echo "❌ Error: set_env.sh not found. Please run this script from the edx-platform directory."
    exit 1
fi

# Get script directory and find virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Set absolute paths for PID files
LMS_PIDFILE="$SCRIPT_DIR/celery_lms.pid"
CMS_PIDFILE="$SCRIPT_DIR/celery_cms.pid"
BEAT_PIDFILE="$SCRIPT_DIR/celery_beat.pid"
FLOWER_PIDFILE="$SCRIPT_DIR/celery_flower.pid"

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ -f "$PARENT_DIR/env/bin/activate" ]; then
    source "$PARENT_DIR/env/bin/activate"
    echo "   ✅ Virtual environment activated from $PARENT_DIR/env"
elif [ -f "/home/suriya-vcw/Desktop/manual build/env/bin/activate" ]; then
    source "/home/suriya-vcw/Desktop/manual build/env/bin/activate"
    echo "   ✅ Virtual environment activated"
else
    echo "   ⚠️  Virtual environment not found. Trying common locations..."
    # Try to find and activate
    if [ -d "$PARENT_DIR/env" ]; then
        source "$PARENT_DIR/env/bin/activate" 2>/dev/null || echo "   ⚠️  Could not activate. Please activate manually: source ../env/bin/activate"
    fi
fi

# Set environment variables
echo "🔧 Setting environment variables..."
source set_env.sh

echo ""
echo "🎯 Starting Celery Services:"
echo ""

# Function to check if process is running by PID
check_process() {
    local pid=$1
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for PID file and verify process
wait_for_pidfile() {
    local pidfile=$1
    local service_name=$2
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if [ -f "$pidfile" ]; then
            local pid=$(cat "$pidfile" 2>/dev/null)
            if [ -n "$pid" ] && check_process "$pid"; then
                echo "   ✅ $service_name started (PID: $pid)"
                return 0
            fi
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    # Final check - maybe process started but PID file wasn't created
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile" 2>/dev/null)
        if check_process "$pid"; then
            echo "   ✅ $service_name started (PID: $pid)"
            return 0
        fi
    fi
    
    # Check if process is running by name
    if pgrep -f "celery.*$service_name" > /dev/null 2>&1; then
        echo "   ⚠️  $service_name process is running but PID file not found"
        return 1
    else
        echo "   ❌ $service_name failed to start"
        return 1
    fi
}

# Clean up stale PID files
cleanup_stale_pidfile() {
    local pidfile=$1
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile" 2>/dev/null)
        if [ -n "$pid" ] && ! check_process "$pid"; then
            echo "   🧹 Removing stale PID file: $pidfile"
            rm -f "$pidfile"
        fi
    fi
}

# Start LMS Celery Worker
echo "1️⃣  Starting LMS Celery Worker..."
cleanup_stale_pidfile "$LMS_PIDFILE"
celery -A lms worker --loglevel=info --concurrency=2 --detach --pidfile="$LMS_PIDFILE" --logfile="$SCRIPT_DIR/celery_lms.log" 2>&1
wait_for_pidfile "$LMS_PIDFILE" "LMS Worker"

# Start CMS Celery Worker
echo "2️⃣  Starting CMS Celery Worker..."
cleanup_stale_pidfile "$CMS_PIDFILE"
celery -A cms worker --loglevel=info --concurrency=2 --detach --pidfile="$CMS_PIDFILE" --logfile="$SCRIPT_DIR/celery_cms.log" 2>&1
wait_for_pidfile "$CMS_PIDFILE" "CMS Worker"

# Start Celery Beat Scheduler
echo "3️⃣  Starting Celery Beat Scheduler..."
cleanup_stale_pidfile "$BEAT_PIDFILE"
celery -A lms beat --loglevel=info --detach --pidfile="$BEAT_PIDFILE" --logfile="$SCRIPT_DIR/celery_beat.log" 2>&1
wait_for_pidfile "$BEAT_PIDFILE" "Beat Scheduler"

# Start Celery Flower (optional monitoring)
echo "4️⃣  Starting Celery Flower (Monitoring)..."
cleanup_stale_pidfile "$FLOWER_PIDFILE"
if celery -A lms flower --port=5555 --detach --pidfile="$FLOWER_PIDFILE" --logfile="$SCRIPT_DIR/celery_flower.log" 2>/dev/null; then
    wait_for_pidfile "$FLOWER_PIDFILE" "Flower Monitor"
else
    echo "   ⚠️  Flower not available (optional)"
fi

echo ""
echo "🎉 Celery services startup completed!"
echo ""
echo "📊 Service Status:"
if [ -f "$LMS_PIDFILE" ]; then
    lms_pid=$(cat "$LMS_PIDFILE" 2>/dev/null)
    if check_process "$lms_pid"; then
        echo "   - LMS Worker:     ✅ Running (PID: $lms_pid)"
    else
        echo "   - LMS Worker:     ❌ PID file exists but process not running"
    fi
else
    echo "   - LMS Worker:     ❌ Not running (PID file not found)"
fi

if [ -f "$CMS_PIDFILE" ]; then
    cms_pid=$(cat "$CMS_PIDFILE" 2>/dev/null)
    if check_process "$cms_pid"; then
        echo "   - CMS Worker:     ✅ Running (PID: $cms_pid)"
    else
        echo "   - CMS Worker:     ❌ PID file exists but process not running"
    fi
else
    echo "   - CMS Worker:     ❌ Not running (PID file not found)"
fi

if [ -f "$BEAT_PIDFILE" ]; then
    beat_pid=$(cat "$BEAT_PIDFILE" 2>/dev/null)
    if check_process "$beat_pid"; then
        echo "   - Beat Scheduler: ✅ Running (PID: $beat_pid)"
    else
        echo "   - Beat Scheduler: ❌ PID file exists but process not running"
    fi
else
    echo "   - Beat Scheduler: ❌ Not running (PID file not found)"
fi

if [ -f "$FLOWER_PIDFILE" ]; then
    flower_pid=$(cat "$FLOWER_PIDFILE" 2>/dev/null)
    if check_process "$flower_pid"; then
        echo "   - Flower Monitor:  ✅ Running (PID: $flower_pid)"
        echo ""
        echo "🌐 Access Celery Flower at: http://localhost:5555"
    else
        echo "   - Flower Monitor:  ❌ PID file exists but process not running"
    fi
else
    echo "   - Flower Monitor:  ⚠️  Not running (optional)"
fi
echo ""
echo "🛑 To stop all services, run: ./stop_celery_services.sh"
echo "📋 To check status, run: ps aux | grep celery"
echo ""
echo "✨ Your Open edX platform is now ready for background task processing!"
echo ""
echo "💡 IMPORTANT: The LMS Worker is required for certificate generation!"
echo "   After this, generate certificates using Django shell (see guides)"
