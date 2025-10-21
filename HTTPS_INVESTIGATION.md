# HTTPS Investigation Commands for Port 443

## Check if app is running on port 443 (HTTPS)

### 1. Check port 443 status:
```bash
ss -tlnp | grep :443
# OR if netstat is available:
sudo netstat -tlnp | grep :443
```

### 2. Test HTTPS connection:
```bash
# Test local HTTPS connection
curl -k -I https://localhost:443
curl -k -I https://127.0.0.1:443

# Test external HTTPS connection  
curl -k -I https://20.157.116.145:443
```

### 3. Check SSL certificate status:
```bash
ls -la *.crt *.key *.pem
ls -la certificate.crt private.key
```

### 4. Check if app is configured for HTTPS:
```bash
grep -n -A5 -B5 "443\|ssl\|https\|certificate" app.py
grep -n "app.run" app.py
```

### 5. Check system services:
```bash
sudo systemctl status nginx
sudo systemctl status apache2
sudo systemctl status casa-todos
```

### 6. Check what's actually listening on 443:
```bash
sudo lsof -i :443
sudo fuser -v 443/tcp
```

### 7. Check SSL/TLS setup in Flask:
```bash
# Look for SSL context in the app
grep -n -A10 -B5 "SSLContext\|ssl_context\|cert\|key" app.py
```

### 8. Test if it's a reverse proxy setup:
```bash
# Check if nginx/apache is proxying to Flask
sudo cat /etc/nginx/sites-available/default 2>/dev/null | grep -A10 -B10 "proxy_pass"
sudo cat /etc/apache2/sites-available/*.conf 2>/dev/null | grep -A5 -B5 "ProxyPass"
```

## Possible HTTPS Configurations:

1. **Direct Flask HTTPS**: Flask app running with SSL certificate on port 443
2. **Reverse Proxy**: Nginx/Apache handling HTTPS and proxying to Flask on port 5000
3. **System Service**: Flask running as systemd service with HTTPS

## If App Crashed on Port 443:

Check for these common HTTPS issues:
- SSL certificate expired/invalid
- Permission issues accessing certificate files  
- Port 443 already in use by another service
- SSL context configuration errors

Run these commands and let me know the results!