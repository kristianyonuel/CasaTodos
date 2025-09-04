#!/usr/bin/env python3
"""
Quick start script for La Casa de Todos NFL Fantasy App
Provides better error handling and user feedback
"""

import subprocess
import sys
import time
import os

def main():
    print("🏈 La Casa de Todos NFL Fantasy Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found in current directory")
        print("💡 Make sure you're in the La Casa de Todos directory")
        return
    
    # Determine mode
    mode = 'dev' if len(sys.argv) < 2 else sys.argv[1].lower()
    
    print(f"🚀 Starting in '{mode}' mode...")
    
    if mode == 'dev':
        print("🛠️ Development server starting on port 5000...")
        print("📍 Access at: http://localhost:5000")
    elif mode == 'http':
        print("🌐 HTTP server starting...")
        print("📍 Access at: http://localhost or http://localhost:8080")
    elif mode == 'https':
        print("🔒 HTTPS server starting...")
        print("📍 Access at: https://localhost or https://localhost:8443")
    elif mode in ['production', 'both']:
        print("🌐🔒 Starting both HTTP and HTTPS servers...")
        print("📍 HTTP Access: http://localhost or http://localhost:8080")
        print("📍 HTTPS Access: https://localhost or https://localhost:8443")
    else:
        print("❌ Invalid mode. Available modes:")
        print("   dev, http, https, production")
        return
    
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    try:
        # Start the app
        if mode in ['production', 'both']:
            mode = 'production'
        
        process = subprocess.Popen(
            [sys.executable, 'app.py', mode],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Show output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        print("✅ Server stopped")
    except FileNotFoundError:
        print("❌ Python not found. Make sure Python is installed and in PATH")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()
