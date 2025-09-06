#!/usr/bin/env python3
"""
SSL Certificate Creator for CasaTodos NFL Fantasy App
Creates self-signed SSL certificates for development and testing.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_openssl():
    """Check if OpenSSL is available"""
    try:
        result = subprocess.run(['openssl', 'version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Found OpenSSL: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        print("Ubuntu/Debian: sudo apt install openssl")
        print("Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return False

def create_ssl_certificates():
    """Create self-signed SSL certificates"""
    
    # Check if OpenSSL is available
    if not check_openssl():
        return False
    
    # Create SSL directory if it doesn't exist
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = "cert.pem"
    key_file = "key.pem"
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        response = input(f"Certificates {cert_file} and {key_file} already exist. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Certificate creation cancelled.")
            return True
    
    print("🔒 Creating SSL certificates...")
    print("You'll be prompted for certificate details (you can press Enter for defaults)")
    
    # OpenSSL command to create self-signed certificate
    cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', key_file,
        '-out', cert_file,
        '-days', '365',
        '-nodes',
        '-subj', '/C=US/ST=State/L=City/O=CasaTodos/OU=IT/CN=localhost'
    ]
    
    try:
        # Run the OpenSSL command
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("✅ SSL certificates created successfully!")
            print(f"📄 Certificate: {cert_file}")
            print(f"🔑 Private key: {key_file}")
            print()
            print("Your Flask app will now automatically detect and use these certificates.")
            print("To run with HTTPS: python app.py")
            print("Access your app at: https://localhost:443")
            return True
        else:
            print("❌ Failed to create certificates")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating certificates: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_custom_certificate():
    """Create certificate with custom details"""
    
    if not check_openssl():
        return False
    
    print("🔧 Custom Certificate Creation")
    print("Enter certificate details (or press Enter for defaults):")
    
    country = input("Country Code (US): ") or "US"
    state = input("State/Province (State): ") or "State" 
    city = input("City (City): ") or "City"
    org = input("Organization (CasaTodos): ") or "CasaTodos"
    unit = input("Organizational Unit (IT): ") or "IT"
    common_name = input("Common Name (localhost): ") or "localhost"
    
    cert_file = "cert.pem"
    key_file = "key.pem"
    
    subject = f"/C={country}/ST={state}/L={city}/O={org}/OU={unit}/CN={common_name}"
    
    cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', key_file,
        '-out', cert_file,
        '-days', '365',
        '-nodes',
        '-subj', subject
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("✅ Custom SSL certificate created successfully!")
            return True
        else:
            print("❌ Failed to create custom certificate")
            return False
    except Exception as e:
        print(f"❌ Error creating custom certificate: {e}")
        return False

def view_certificate_info():
    """Display information about existing certificates"""
    
    cert_files = ['cert.pem', 'ssl/cert.pem', 'certificate.crt', 'fullchain.pem']
    
    found_cert = None
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            found_cert = cert_file
            break
    
    if not found_cert:
        print("❌ No SSL certificates found in the project.")
        return
    
    print(f"📄 Certificate information for: {found_cert}")
    
    try:
        cmd = ['openssl', 'x509', '-in', found_cert, '-text', '-noout']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract key information
        lines = result.stdout.split('\n')
        for line in lines:
            line = line.strip()
            if 'Subject:' in line or 'Issuer:' in line or 'Not Before:' in line or 'Not After:' in line:
                print(f"  {line}")
                
    except Exception as e:
        print(f"❌ Error reading certificate: {e}")

def main():
    """Main function"""
    
    print("🔒 CasaTodos SSL Certificate Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Create default SSL certificate (localhost)")
        print("2. Create custom SSL certificate")
        print("3. View existing certificate info")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            create_ssl_certificates()
        elif choice == '2':
            create_custom_certificate()
        elif choice == '3':
            view_certificate_info()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
