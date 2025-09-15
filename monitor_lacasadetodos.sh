#!/bin/bash
# Health Monitor and Auto-Restart Script for La Casa de Todos
# Run this script as a cron job every 2 minutes for monitoring

SERVICE_NAME="lacasadetodos"
APP_URL="http://localhost"
HEALTH_ENDPOINT="/health"
LOG_FILE="/var/log/lacasadetodos-monitor.log"
MAX_RESTART_ATTEMPTS=3
RESTART_COOLDOWN=300  # 5 minutes

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if service is running
check_service() {
    systemctl is-active --quiet "$SERVICE_NAME"
    return $?
}

# Function to check HTTP health
check_http_health() {
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 30 "$APP_URL$HEALTH_ENDPOINT" 2>/dev/null)
    
    if [ "$response_code" = "200" ]; then
        return 0
    else
        log "Health check failed: HTTP $response_code"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local db_check
    db_check=$(cd /home/casa/CasaTodos && /home/casa/CasaTodos/venv/bin/python -c "
import sqlite3
try:
    conn = sqlite3.connect('nfl_fantasy.db', timeout=5)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users LIMIT 1')
    conn.close()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null)
    
    if [ "$db_check" = "OK" ]; then
        return 0
    else
        log "Database check failed: $db_check"
        return 1
    fi
}

# Function to restart service
restart_service() {
    log "Attempting to restart $SERVICE_NAME service..."
    
    # Stop the service
    systemctl stop "$SERVICE_NAME"
    sleep 5
    
    # Kill any remaining processes
    pkill -f "python.*app.py" 2>/dev/null
    sleep 2
    
    # Start the service
    systemctl start "$SERVICE_NAME"
    sleep 10
    
    if check_service; then
        log "Service $SERVICE_NAME restarted successfully"
        return 0
    else
        log "Failed to restart $SERVICE_NAME service"
        return 1
    fi
}

# Function to send alert (customize this for your notification system)
send_alert() {
    local message="$1"
    log "ALERT: $message"
    
    # Add your notification method here:
    # - Email notification
    # - Slack webhook
    # - Discord webhook
    # - SMS service
    
    # Example: Send email (requires mailutils)
    # echo "$message" | mail -s "La Casa de Todos Alert" admin@yourdomain.com
    
    # Example: Slack webhook
    # curl -X POST -H 'Content-type: application/json' \
    #      --data "{\"text\":\"$message\"}" \
    #      YOUR_SLACK_WEBHOOK_URL
}

# Main monitoring logic
main() {
    log "Starting health check for $SERVICE_NAME"
    
    # Check if service is running
    if ! check_service; then
        log "Service $SERVICE_NAME is not running"
        restart_service
        if ! check_service; then
            send_alert "Failed to restart $SERVICE_NAME service"
            exit 1
        fi
    fi
    
    # Check HTTP health
    if ! check_http_health; then
        log "HTTP health check failed"
        
        # Check database first
        if ! check_database; then
            log "Database connectivity issue detected"
        fi
        
        restart_service
        
        # Wait and recheck
        sleep 30
        if ! check_http_health; then
            send_alert "HTTP health check still failing after restart"
        fi
    fi
    
    # Check database connectivity
    if ! check_database; then
        log "Database connectivity check failed"
        restart_service
        
        # Wait and recheck
        sleep 30
        if ! check_database; then
            send_alert "Database connectivity still failing after restart"
        fi
    fi
    
    log "Health check completed successfully"
}

# Run the main function
main
