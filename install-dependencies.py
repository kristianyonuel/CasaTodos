import subprocess
import sys
import os

def install_with_pip():
    """Try installing with pip directly"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def install_with_user_flag():
    """Try installing with --user flag"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def install_with_break_system():
    """Try installing with --break-system-packages flag"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def install_individual_packages():
    """Install packages individually with different methods"""
    packages = [
        "Flask==2.3.3",
        "Werkzeug==2.3.7", 
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.3",
        "itsdangerous==2.1.2",
        "click==8.1.7",
        "blinker==1.6.3",
        "requests==2.31.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
                print(f"✓ Installed {package} (with --break-system-packages)")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")

def main():
    print("Installing dependencies for externally-managed environment...")
    
    # Method 1: Standard pip install
    if install_with_pip():
        print("✓ Dependencies installed successfully with standard pip")
        return
    
    # Method 2: User installation
    print("Standard pip failed, trying --user installation...")
    if install_with_user_flag():
        print("✓ Dependencies installed successfully with --user flag")
        return
    
    # Method 3: Break system packages (for externally-managed environments)
    print("User installation failed, trying --break-system-packages...")
    if install_with_break_system():
        print("✓ Dependencies installed successfully with --break-system-packages")
        return
    
    # Method 4: Individual package installation
    print("Bulk installation failed, trying individual packages...")
    install_individual_packages()
    print("Individual package installation completed")

if __name__ == "__main__":
    main()
