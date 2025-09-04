import sys
import os

def main():
    print("La Casa de Todos - Simple Launcher")
    print("==================================")
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Import and run the Flask app
        from app import app
        
        print("Starting La Casa de Todos NFL Fantasy League...")
        print("Access at: http://127.0.0.1:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
