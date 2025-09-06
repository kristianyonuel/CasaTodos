@echo off
REM SSL Certificate Generator for Casa de Todos NFL Fantasy App
REM This creates self-signed certificates for development/testing

echo.
echo 🏈 Casa de Todos - SSL Certificate Generator
echo ================================================

REM Check if OpenSSL is available
where openssl >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ OpenSSL not found. 
    echo.
    echo 💡 Install OpenSSL or use the Python method:
    echo    1. pip install cryptography
    echo    2. python generate_ssl_cert.py
    echo.
    echo 🔗 Download OpenSSL: https://slproweb.com/products/Win32OpenSSL.html
    pause
    exit /b 1
)

echo ✅ OpenSSL found, generating certificates...
echo.

REM Generate private key
echo 🔑 Generating private key...
openssl genrsa -out private.key 2048
if %errorlevel% neq 0 (
    echo ❌ Failed to generate private key
    pause
    exit /b 1
)

REM Create certificate signing request configuration
echo 📝 Creating certificate configuration...
(
echo [req]
echo distinguished_name = req_distinguished_name
echo req_extensions = v3_req
echo prompt = no
echo.
echo [req_distinguished_name]
echo C = US
echo ST = Texas
echo L = Casa
echo O = Casa de Todos
echo CN = casadetodos.eastus.cloudapp.azure.com
echo.
echo [v3_req]
echo keyUsage = keyEncipherment, dataEncipherment
echo extendedKeyUsage = serverAuth
echo subjectAltName = @alt_names
echo.
echo [alt_names]
echo DNS.1 = casadetodos.eastus.cloudapp.azure.com
echo DNS.2 = localhost
echo DNS.3 = 127.0.0.1
) > ssl_config.tmp

REM Generate certificate
echo 📜 Generating SSL certificate...
openssl req -new -x509 -key private.key -out certificate.crt -days 365 -config ssl_config.tmp -extensions v3_req
if %errorlevel% neq 0 (
    echo ❌ Failed to generate certificate
    del ssl_config.tmp
    pause
    exit /b 1
)

REM Clean up temporary file
del ssl_config.tmp

echo.
echo ✅ SSL certificate generated successfully!
echo.
echo 📁 Files created:
echo    - certificate.crt (SSL certificate)
echo    - private.key (private key)
echo.
echo ⚠️  Note: This is a self-signed certificate.
echo    Browsers will show security warnings.
echo    For production, use a proper SSL certificate from:
echo    - Let's Encrypt (free)
echo    - Your domain registrar  
echo    - A certificate authority
echo.
echo 🚀 Next steps:
echo 1. Run your Flask app: python app.py production
echo 2. Access via HTTPS (ignore browser warnings)
echo 3. For production, replace with proper SSL certificates
echo.
pause
