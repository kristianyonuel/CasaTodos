# Multi-Port Server Setup Guide

## Overview

The La Casa de Todos NFL Fantasy app now supports running on multiple ports simultaneously, including both HTTP and HTTPS protocols.

## Server Modes

### 1. Development Mode
```bash
python app.py dev
# or
python run_server.py dev
```
- Runs on port 5000
- Debug mode enabled
- Single threaded
- Best for development and testing

### 2. HTTP Only
```bash
python app.py http
# or
python run_server.py http
```
- Runs on port 80 (or 8080 if no privileges)
- HTTP protocol only
- Production ready

### 3. HTTPS Only
```bash
python app.py https
# or
python run_server.py https
```
- Runs on port 443 (or 8443 if no privileges)
- HTTPS protocol with SSL/TLS encryption
- Auto-generates self-signed certificate if needed
- Production ready

### 4. Production Mode (Both HTTP and HTTPS)
```bash
python app.py production
# or
python run_server.py production
```
- Runs HTTP on port 80/8080 AND HTTPS on port 443/8443
- Both servers run simultaneously
- Best for production deployment

## SSL Certificates

### Auto-Generated Certificates
The app will automatically create self-signed SSL certificates if none are found:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

### Custom Certificates
To use your own SSL certificates:
1. Place your certificate file as `cert.pem`
2. Place your private key file as `key.pem`
3. Both files should be in the same directory as `app.py`

### Certificate Requirements
For production use, obtain certificates from a trusted Certificate Authority (CA) like:
- Let's Encrypt (free)
- Cloudflare
- DigiCert
- Comodo

## Port Permissions

### Privileged Ports (80, 443)
On Linux/Unix systems, ports 80 and 443 require root privileges:
```bash
sudo python app.py production
```

### Alternative Ports (8080, 8443)
If you don't have root privileges, the app will automatically use:
- HTTP: Port 8080 instead of 80
- HTTPS: Port 8443 instead of 443

## Installation

### Install Dependencies
```bash
pip install -r requirements.txt
# or
python run_server.py install
```

### Required Packages
- Flask 3.0.3
- cryptography 41.0.7 (for SSL certificate generation)
- All other existing dependencies

## Usage Examples

### Development
```bash
python run_server.py dev
```
Access at: http://localhost:5000

### HTTP Production
```bash
sudo python run_server.py http
```
Access at: http://localhost or http://localhost:8080

### HTTPS Production
```bash
sudo python run_server.py https
```
Access at: https://localhost or https://localhost:8443

### Full Production (Recommended)
```bash
sudo python run_server.py production
```
Access at: 
- http://localhost (redirects available)
- https://localhost (secure)

## Security Considerations

### Self-Signed Certificates
- Browsers will show security warnings
- Not recommended for public production
- Good for internal/private networks

### Trusted Certificates
- No browser warnings
- Required for public websites
- Provides proper encryption

### HTTP Redirection
Consider implementing HTTP to HTTPS redirection for production use.

## Firewall Configuration

Ensure your firewall allows the ports you're using:

### Linux (UFW)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp
```

### Linux (iptables)
```bash
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### Windows Firewall
Add inbound rules for ports 80, 443, 8080, and 8443 through Windows Defender Firewall.

## Troubleshooting

### Port Already in Use
```
Error: [Errno 98] Address already in use
```
- Another service is using the port
- Stop other web servers (Apache, Nginx, etc.)
- Use `netstat -tulpn | grep :80` to find what's using the port

### Permission Denied
```
Error: [Errno 13] Permission denied
```
- Use `sudo` for privileged ports
- Or use alternative ports (8080/8443)

### SSL Certificate Errors
```
Error creating SSL context
```
- Install cryptography: `pip install cryptography`
- Or install OpenSSL
- Check file permissions on cert.pem and key.pem

### Missing Dependencies
```
ModuleNotFoundError: No module named 'cryptography'
```
- Run: `python run_server.py install`
- Or: `pip install -r requirements.txt`

## Performance Tips

### Production Deployment
- Use a proper WSGI server (Gunicorn, uWSGI)
- Use a reverse proxy (Nginx, Apache)
- Use a process manager (systemd, supervisor)

### Example with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Example with Nginx Reverse Proxy
```nginx
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

You can set these environment variables to customize behavior:
- `SSL_CERT_FILE` - Path to SSL certificate
- `SSL_KEY_FILE` - Path to SSL private key
- `HTTP_PORT` - Custom HTTP port (default: 80)
- `HTTPS_PORT` - Custom HTTPS port (default: 443)

## Monitoring

The app logs server startup information:
- Which ports are being used
- SSL certificate status
- Any errors or warnings

Check the logs for troubleshooting and monitoring.
