#!/bin/bash
# Quick Service Management Script for La Casa de Todos

SERVICE_NAME="lacasadetodos"

echo "🏈 La Casa de Todos Service Manager"
echo "=================================="

# Function to show service status with color
show_status() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Service Status: RUNNING"
    else
        echo "❌ Service Status: STOPPED"
    fi
    
    echo ""
    systemctl status "$SERVICE_NAME" --no-pager -l
}

# Function to show recent logs
show_logs() {
    echo "📋 Recent Service Logs:"
    echo "======================"
    journalctl -u "$SERVICE_NAME" -n 20 --no-pager
}

# Function to restart service with health check
restart_with_check() {
    echo "🔄 Restarting $SERVICE_NAME..."
    
    systemctl restart "$SERVICE_NAME"
    
    echo "⏳ Waiting for service to start..."
    sleep 10
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Service restarted successfully!"
        
        # Check health endpoint
        echo "🏥 Checking health endpoint..."
        if curl -sf http://localhost/health >/dev/null 2>&1; then
            echo "✅ Health check passed!"
        else
            echo "⚠️  Health check failed - service may still be starting"
        fi
    else
        echo "❌ Service failed to start"
        echo "📋 Error logs:"
        journalctl -u "$SERVICE_NAME" -n 10 --no-pager
    fi
}

# Main menu
case "$1" in
    status|"")
        show_status
        ;;
    logs)
        show_logs
        ;;
    restart)
        restart_with_check
        ;;
    start)
        echo "🚀 Starting $SERVICE_NAME..."
        systemctl start "$SERVICE_NAME"
        sleep 5
        show_status
        ;;
    stop)
        echo "🛑 Stopping $SERVICE_NAME..."
        systemctl stop "$SERVICE_NAME"
        sleep 3
        show_status
        ;;
    monitor)
        echo "📊 Monitoring $SERVICE_NAME (Press Ctrl+C to exit)..."
        journalctl -u "$SERVICE_NAME" -f
        ;;
    health)
        echo "🏥 Health Check:"
        echo "==============="
        if curl -sf http://localhost/health 2>/dev/null | python3 -m json.tool; then
            echo "✅ Health check successful"
        else
            echo "❌ Health check failed"
        fi
        ;;
    quick-fix)
        echo "🔧 Running quick fix sequence..."
        systemctl stop "$SERVICE_NAME"
        pkill -f "python.*app.py" 2>/dev/null || true
        sleep 3
        systemctl start "$SERVICE_NAME"
        sleep 10
        show_status
        ;;
    *)
        echo "Usage: $0 {status|logs|restart|start|stop|monitor|health|quick-fix}"
        echo ""
        echo "Commands:"
        echo "  status     - Show service status (default)"
        echo "  logs       - Show recent service logs"
        echo "  restart    - Restart service with health check"
        echo "  start      - Start the service"
        echo "  stop       - Stop the service"
        echo "  monitor    - Monitor live logs"
        echo "  health     - Check health endpoint"
        echo "  quick-fix  - Stop, kill processes, and restart"
        echo ""
        echo "Examples:"
        echo "  sudo $0 restart    # Restart with verification"
        echo "  sudo $0 logs       # View recent logs"
        echo "  sudo $0 health     # Check if app is responding"
        exit 1
        ;;
esac
