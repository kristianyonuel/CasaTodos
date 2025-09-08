#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

try:
    from app import app
    
    # Start the app in debug mode to see errors
    if __name__ == "__main__":
        app.run(debug=True, port=8080, host='127.0.0.1')
        
except Exception as e:
    print(f"Error starting app: {e}")
    import traceback
    traceback.print_exc()
