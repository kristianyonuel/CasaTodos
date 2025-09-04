import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'jinja2': 'Jinja2',
        'requests': 'requests'
    }
    
    missing_packages = []
    for module_name, package_name in required_packages.items():
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            missing_packages.append(package_name)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages with externally-managed environment support"""
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")

def main():
    print("La Casa de Todos - NFL Fantasy League")
    print("Externally-Managed Environment Support")
    print("=====================================")
    
    # Check for missing dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing missing packages...")
        install_missing_packages(missing)
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Import and run the Flask app
        from app import app
        print("Starting La Casa de Todos NFL Fantasy League...")
        print("Access the application at: http://127.0.0.1:5000")
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print("Please ensure all dependencies are installed correctly.")
        print("Run: python install-dependencies.py")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
