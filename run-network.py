import socket
import sys
import os

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine IP"

def main():
    print("La Casa de Todos - Network Launcher")
    print("=" * 40)
    
    local_ip = get_local_ip()
    
    print(f"Local IP Address: {local_ip}")
    print("Starting application on all network interfaces...")
    print()
    print("Access URLs:")
    print(f"  Local:   http://127.0.0.1:5000")
    print(f"  Network: http://{local_ip}:5000")
    print(f"  External: http://[PUBLIC-IP]:5000 (if port forwarded)")
    print()
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Import and run the Flask app
        from app import app
        
        # Configure for network access
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        # Run on all interfaces
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
