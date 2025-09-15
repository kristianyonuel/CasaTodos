#!/bin/bash
# Process Watchdog for La Casa de Todos
# This script ensures the app process is always running

SERVICE_NAME="lacasadetodos"
APP_DIR="/home/casa/CasaTodos"
PYTHON_PATH="$APP_DIR/venv/bin/python"
APP_SCRIPT="$APP_DIR/app.py"
PID_FILE="/var/run/lacasadetodos.pid"
LOG_FILE="/var/log/lacasadetodos-watchdog.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if process is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the application
start_app() {
    log "Starting La Casa de Todos application..."
    
    cd "$APP_DIR"
    
    # Kill any existing processes
    pkill -f "python.*app.py" 2>/dev/null
    sleep 2
    
    # Start the application
    nohup "$PYTHON_PATH" "$APP_SCRIPT" production > /var/log/lacasadetodos-app.log 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 5
    if kill -0 "$pid" 2>/dev/null; then
        log "Application started successfully (PID: $pid)"
        return 0
    else
        log "Failed to start application"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the application
stop_app() {
    log "Stopping La Casa de Todos application..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 5
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid"
                sleep 2
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "python.*app.py" 2>/dev/null
    
    log "Application stopped"
}

# Function to restart the application
restart_app() {
    log "Restarting La Casa de Todos application..."
    stop_app
    sleep 3
    start_app
}

# Main watchdog logic
case "$1" in
    start)
        if is_running; then
            log "Application is already running"
        else
            start_app
        fi
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        if is_running; then
            local pid=$(cat "$PID_FILE")
            log "Application is running (PID: $pid)"
        else
            log "Application is not running"
        fi
        ;;
    watch)
        log "Starting watchdog mode..."
        while true; do
            if ! is_running; then
                log "Application not running, attempting to start..."
                start_app
                
                if ! is_running; then
                    log "Failed to start application, waiting 30 seconds before retry..."
                    sleep 30
                fi
            fi
            sleep 60  # Check every minute
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|watch}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the application"
        echo "  stop    - Stop the application" 
        echo "  restart - Restart the application"
        echo "  status  - Check if application is running"
        echo "  watch   - Run in watchdog mode (continuously monitor)"
        exit 1
        ;;
esac
