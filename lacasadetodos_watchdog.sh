#!/bin/bash
# Process Watchdog for La Casa de Todos NFL Fantasy Server
# Monitors the lacasadetodos service and performs health checks

SERVICE_NAME="lacasadetodos"
HEALTH_URL="http://localhost/health/simple"
LOG_FILE="/home/casa/CasaTodos/watchdog.log"
MAX_RESTART_ATTEMPTS=3
RESTART_COOLDOWN=300  # 5 minutes

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to check if service is running
check_service_status() {
    systemctl is-active --quiet "$SERVICE_NAME"
    return $?
}

# Function to check application health
check_app_health() {
    # First try simple health check
    if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
        return 0
    fi
    
    # If simple health fails, try detailed health check
    if curl -f -s "http://localhost/health" > /dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# Function to restart service
restart_service() {
    log_message "Attempting to restart $SERVICE_NAME service..."
    
    # Stop the service first
    systemctl stop "$SERVICE_NAME"
    sleep 5
    
    # Kill any remaining processes
    pkill -f "python.*app.py" 2>/dev/null
    sleep 2
    
    # Start the service
    systemctl start "$SERVICE_NAME"
    sleep 10
    
    if check_service_status; then
        log_message "Service $SERVICE_NAME restarted successfully"
        return 0
    else
        log_message "Failed to restart $SERVICE_NAME service"
        return 1
    fi
}

# Function to send notification (optional)
send_notification() {
    local message="$1"
    log_message "ALERT: $message"
    
    # You can add email/webhook notifications here
    # Example: curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$message"'"}' YOUR_WEBHOOK_URL
}

# Main monitoring loop
main() {
    local restart_count=0
    local last_restart_time=0
    
    log_message "Starting watchdog for $SERVICE_NAME service"
    
    while true; do
        current_time=$(date +%s)
        
        # Check if service is running
        if ! check_service_status; then
            log_message "Service $SERVICE_NAME is not running"
            
            # Check restart cooldown
            if [ $((current_time - last_restart_time)) -lt $RESTART_COOLDOWN ]; then
                log_message "In restart cooldown period, waiting..."
                sleep 30
                continue
            fi
            
            # Attempt restart
            if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                restart_count=$((restart_count + 1))
                last_restart_time=$current_time
                
                if restart_service; then
                    restart_count=0  # Reset counter on successful restart
                    send_notification "Service $SERVICE_NAME was down and has been restarted (attempt $restart_count)"
                else
                    send_notification "Failed to restart $SERVICE_NAME (attempt $restart_count)"
                fi
            else
                send_notification "Service $SERVICE_NAME failed to restart after $MAX_RESTART_ATTEMPTS attempts. Manual intervention required."
                log_message "Max restart attempts reached. Entering passive monitoring mode."
                restart_count=0
                last_restart_time=$current_time
            fi
        else
            # Service is running, check application health
            if ! check_app_health; then
                log_message "Service is running but health check failed"
                
                # Check restart cooldown
                if [ $((current_time - last_restart_time)) -lt $RESTART_COOLDOWN ]; then
                    log_message "In restart cooldown period, waiting..."
                    sleep 30
                    continue
                fi
                
                # Attempt restart for health failure
                if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                    restart_count=$((restart_count + 1))
                    last_restart_time=$current_time
                    
                    log_message "Health check failed, restarting service"
                    if restart_service; then
                        restart_count=0  # Reset counter on successful restart
                        send_notification "Service $SERVICE_NAME health check failed, service restarted"
                    else
                        send_notification "Failed to restart $SERVICE_NAME after health check failure"
                    fi
                else
                    send_notification "Service $SERVICE_NAME health checks continue to fail after $MAX_RESTART_ATTEMPTS restart attempts"
                    log_message "Max restart attempts reached for health failures. Continuing monitoring."
                    restart_count=0
                    last_restart_time=$current_time
                fi
            else
                # Everything is healthy
                if [ $restart_count -gt 0 ]; then
                    log_message "Service is healthy, resetting restart counter"
                    restart_count=0
                fi
            fi
        fi
        
        # Wait before next check
        sleep 60
    done
}

# Handle script termination
cleanup() {
    log_message "Watchdog script terminated"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start the watchdog
main "$@"
