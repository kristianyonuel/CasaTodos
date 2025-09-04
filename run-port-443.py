import sys
import os
import subprocess
import importlib.util

def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart script with administrator privileges"""
    try:
        import ctypes
        if sys.argv[-1] != 'asadmin':
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            return True
    except:
        return False
    return False

def main():
    print("La Casa de Todos - Port 443 Launcher")
    print("====================================")
    
    # Check if running as administrator
    if not check_admin_privileges():
        print("Port 443 requires administrator privileges.")
        print("Attempting to restart with admin rights...")
        if run_as_admin():
            return
        else:
            print("Failed to get admin privileges. Running on alternative port...")
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Import and run the Flask app
        from app import app
        import ssl
        
        print("Starting La Casa de Todos on port 443...")
        
        # Try HTTPS first
        try:
            print("Starting HTTPS server on port 443...")
            print("Access at: https://localhost:443")
            app.run(debug=False, host='0.0.0.0', port=443, ssl_context='adhoc')
        except Exception as e:
            print(f"HTTPS failed: {e}")
            print("Trying HTTP on port 443...")
            app.run(debug=False, host='0.0.0.0', port=443)
            
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to port 5000...")
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    main()
