#!/usr/bin/env python3
"""
Start Flask server from correct directory with proper error handling
"""

import os
import sys
import subprocess

def start_flask_server():
    """Start Flask server from the correct directory"""
    
    # Ensure we're in the right directory
    target_dir = r"C:\Users\cjuarbe\Casa\CasaTodos"
    
    if not os.path.exists(target_dir):
        print(f"❌ Directory not found: {target_dir}")
        return False
    
    # Change to the target directory
    os.chdir(target_dir)
    print(f"📁 Changed to directory: {os.getcwd()}")
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found in current directory")
        return False
    
    # Check if templates directory exists
    if not os.path.exists("templates"):
        print("❌ templates directory not found")
        return False
        
    if not os.path.exists("templates/games.html"):
        print("❌ templates/games.html not found")
        return False
    
    print("✅ All required files found")
    print("🚀 Starting Flask server...")
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_flask_server()
