#!/usr/bin/env python3
"""
SSL Certificate Generator for Casa de Todos NFL Fantasy App
Generates self-signed certificates for development/testing
"""

import ssl
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

def generate_self_signed_cert(hostname="casadetodos.eastus.cloudapp.azure.com"):
    """Generate a self-signed SSL certificate"""
    
    print(f"🔐 Generating self-signed SSL certificate for: {hostname}")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Texas"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Casa"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Casa de Todos"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(hostname),
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write certificate
    with open("certificate.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Write private key
    with open("private.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print("✅ SSL certificate generated successfully!")
    print("📁 Files created:")
    print("   - certificate.crt (SSL certificate)")
    print("   - private.key (private key)")
    print("")
    print("⚠️  Note: This is a self-signed certificate.")
    print("   Browsers will show security warnings.")
    print("   For production, use a proper SSL certificate from:")
    print("   - Let's Encrypt (free)")
    print("   - Your domain registrar")
    print("   - A certificate authority")
    
    return True

def test_ssl_setup():
    """Test if SSL files can be loaded"""
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain("certificate.crt", "private.key")
        print("✅ SSL certificate test successful!")
        return True
    except Exception as e:
        print(f"❌ SSL certificate test failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    hostname = "casadetodos.eastus.cloudapp.azure.com"
    if len(sys.argv) > 1:
        hostname = sys.argv[1]
    
    print("🏈 Casa de Todos - SSL Certificate Generator")
    print("=" * 50)
    
    # Check if certificates already exist
    if os.path.exists("certificate.crt") and os.path.exists("private.key"):
        print("📋 Existing certificates found:")
        print("   - certificate.crt")
        print("   - private.key")
        print("")
        
        if test_ssl_setup():
            print("✅ Existing certificates are valid!")
            response = input("🤔 Generate new certificates anyway? (y/N): ").lower()
            if response != 'y':
                print("👍 Using existing certificates.")
                exit(0)
        else:
            print("⚠️  Existing certificates are invalid. Generating new ones...")
    
    # Generate new certificates
    if generate_self_signed_cert(hostname):
        test_ssl_setup()
        
        print("")
        print("🚀 Next steps:")
        print("1. Run your Flask app: python app.py production")
        print("2. Access via HTTPS (ignore browser warnings)")
        print("3. For production, replace with proper SSL certificates")
