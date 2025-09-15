#!/bin/bash
# Auto-restart monitoring script for Casa Todos NFL Fantasy App
# This script monitors the Flask app and restarts it automatically on issues

APP_NAME="casa-todos"
APP_DIR="/home/casa/CasaTodos"
APP_SCRIPT="app.py"
PID_FILE="/tmp/casa-todos.pid"
LOG_FILE="$APP_DIR/monitor.log"
ERROR_LOG="$APP_DIR/error.log"
MAX_RESTART_ATTEMPTS=5
RESTART_DELAY=10
HEALTH_CHECK_INTERVAL=30
PORT_CHECK_TIMEOUT=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if app process is running
is_app_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Check if it's actually our app
            if ps -p "$pid" -o cmd= | grep -q "$APP_SCRIPT"; then
                return 0
            fi
        fi
        # PID file exists but process is not running, remove it
        rm -f "$PID_FILE"
    fi
    return 1
}

# Health check - test if app responds on HTTP
health_check() {
    # Check if port 80 is responding
    if timeout $PORT_CHECK_TIMEOUT bash -c "</dev/tcp/localhost/80" 2>/dev/null; then
        return 0
    fi
    
    # Check if port 8080 is responding (HTTP mode)
    if timeout $PORT_CHECK_TIMEOUT bash -c "</dev/tcp/localhost/8080" 2>/dev/null; then
        return 0
    fi
    
    # Check if port 5000 is responding (dev mode)
    if timeout $PORT_CHECK_TIMEOUT bash -c "</dev/tcp/localhost/5000" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

# Start the application
start_app() {
    log_message "Starting $APP_NAME..."
    
    cd "$APP_DIR" || {
        log_message "ERROR: Cannot change to app directory $APP_DIR"
        return 1
    }
    
    # Activate virtual environment and start app
    source venv/bin/activate || {
        log_message "ERROR: Cannot activate virtual environment"
        return 1
    }
    
    # Kill any existing processes first
    pkill -f "python.*$APP_SCRIPT" 2>/dev/null
    sleep 2
    
    # Start app in background and save PID
    nohup python "$APP_SCRIPT" production > "$LOG_FILE" 2> "$ERROR_LOG" &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and verify it started
    sleep 5
    if is_app_running; then
        log_message "✅ $APP_NAME started successfully (PID: $pid)"
        return 0
    else
        log_message "❌ Failed to start $APP_NAME"
        return 1
    fi
}

# Stop the application
stop_app() {
    log_message "Stopping $APP_NAME..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            sleep 5
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid"
                sleep 2
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "python.*$APP_SCRIPT" 2>/dev/null
    log_message "🛑 $APP_NAME stopped"
}

# Restart the application
restart_app() {
    log_message "🔄 Restarting $APP_NAME..."
    stop_app
    sleep $RESTART_DELAY
    start_app
}

# Monitor loop
monitor_loop() {
    local restart_count=0
    local last_restart_time=0
    
    log_message "🔍 Starting monitoring loop for $APP_NAME"
    
    while true; do
        current_time=$(date +%s)
        
        # Reset restart count every hour
        if [ $((current_time - last_restart_time)) -gt 3600 ]; then
            restart_count=0
        fi
        
        # Check if app is running
        if ! is_app_running; then
            log_message "⚠️ Process not running, attempting restart..."
            
            if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                restart_app
                if [ $? -eq 0 ]; then
                    restart_count=$((restart_count + 1))
                    last_restart_time=$current_time
                else
                    log_message "❌ Restart failed, will retry in $HEALTH_CHECK_INTERVAL seconds"
                fi
            else
                log_message "❌ Maximum restart attempts reached ($MAX_RESTART_ATTEMPTS), stopping monitor"
                exit 1
            fi
        else
            # Process is running, check health
            if ! health_check; then
                log_message "⚠️ Health check failed, app not responding on expected ports"
                
                if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                    restart_app
                    if [ $? -eq 0 ]; then
                        restart_count=$((restart_count + 1))
                        last_restart_time=$current_time
                    fi
                else
                    log_message "❌ Maximum restart attempts reached, stopping monitor"
                    exit 1
                fi
            else
                # All good, log success every 10 checks to avoid spam
                if [ $((current_time % 300)) -eq 0 ]; then
                    log_message "✅ $APP_NAME is running healthy"
                fi
            fi
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Signal handlers
cleanup() {
    log_message "🛑 Monitor received shutdown signal"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main script logic
case "${1:-monitor}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        if is_app_running; then
            echo -e "${GREEN}✅ $APP_NAME is running${NC}"
            if health_check; then
                echo -e "${GREEN}✅ Health check passed${NC}"
            else
                echo -e "${YELLOW}⚠️ Health check failed${NC}"
            fi
        else
            echo -e "${RED}❌ $APP_NAME is not running${NC}"
        fi
        ;;
    monitor)
        monitor_loop
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the application"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  status  - Check application status"
        echo "  monitor - Start monitoring loop (default)"
        exit 1
        ;;
esac
