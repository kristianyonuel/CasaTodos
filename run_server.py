#!/usr/bin/env python3
"""
La Casa de Todos - Multi-Port Server Launcher

This script provides easy ways to run the NFL Fantasy app on different ports and protocols.
"""

import subprocess
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("La Casa de Todos - Server Launcher")
        print("=" * 40)
        print("Usage: python run_server.py [mode]")
        print()
        print("Available modes:")
        print("  dev        - Development server (port 5000)")
        print("  http       - HTTP only (port 80/8080)")
        print("  https      - HTTPS only (port 443/8443)")
        print("  production - Both HTTP and HTTPS")
        print("  install    - Install required dependencies")
        print()
        print("Examples:")
        print("  python run_server.py dev")
        print("  python run_server.py production")
        print("  sudo python run_server.py production  # For ports 80/443")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == 'install':
        print("Installing dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
        return
    
    # Check if requirements are installed
    try:
        import flask
        import cryptography
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: python run_server.py install")
        return
    
    # Check if running as admin/root for privileged ports
    if mode in ['http', 'https', 'production']:
        try:
            # Try to bind to a privileged port to test permissions
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 80))
            s.close()
            has_privileges = True
        except PermissionError:
            has_privileges = False
            print("⚠️  Warning: No permission for privileged ports (80/443)")
            print("   Will use alternative ports (8080/8443)")
            print("   For ports 80/443, run with: sudo python run_server.py", mode)
        except OSError:
            # Port might be in use, but we have permissions
            has_privileges = True
    
    # Run the app with the specified mode
    print(f"Starting server in '{mode}' mode...")
    try:
        subprocess.run([sys.executable, 'app.py', mode], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")

if __name__ == '__main__':
    main()
