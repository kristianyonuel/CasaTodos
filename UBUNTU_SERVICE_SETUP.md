# Ubuntu Service Setup Guide for La Casa de Todos

This guide explains how to set up La Casa de Todos NFL Fantasy League as a systemd service on Ubuntu, allowing it to run automatically in the background.

## 📋 Prerequisites

1. **Ubuntu Server/Desktop** (18.04 or later)
2. **Python 3.11+** (Python 3.13 recommended)
3. **Git** (for cloning the repository)
4. **Systemd** (standard on Ubuntu)

## 🚀 Quick Setup Commands

### 1. Update System and Install Dependencies
```bash
# Update package list
sudo apt update

# Install Python, pip, git, and other dependencies
sudo apt install python3 python3-pip python3-venv git sqlite3 -y

# Install nginx (optional, for reverse proxy)
sudo apt install nginx -y
```

### 2. Clone and Setup Application
```bash
# Your application is already in /home/casa/CasaTodos
cd /home/casa/CasaTodos

# Create virtual environment
python3 -m venv venv

# Activate virtual environment and install dependencies
./venv/bin/pip install -r requirements.txt

# Set up database
./venv/bin/python setup_database.py

# Set proper permissions for the service user
sudo chown -R casa:casa /home/casa/CasaTodos
chmod +x /home/casa/CasaTodos/app.py
```

### 3. Create Systemd Service File
```bash
# Create the service file
sudo nano /etc/systemd/system/lacasadetodos.service
```

**Copy this content into the service file:**

```ini
[Unit]
Description=La Casa de Todos NFL Fantasy League
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/casa/CasaTodos
Environment=PATH=/home/casa/CasaTodos/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/casa/CasaTodos
ExecStart=/home/casa/CasaTodos/venv/bin/python /home/casa/CasaTodos/app.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lacasadetodos

# Security settings (relaxed for root user)
PrivateTmp=yes
ReadWritePaths=/home/casa/CasaTodos

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start the Service
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable lacasadetodos

# Start the service
sudo systemctl start lacasadetodos

# Check service status
sudo systemctl status lacasadetodos
```

## 🔧 Service Management Commands

### Basic Service Control
```bash
# Start the service
sudo systemctl start lacasadetodos

# Stop the service
sudo systemctl stop lacasadetodos

# Restart the service
sudo systemctl restart lacasadetodos

# Check service status
sudo systemctl status lacasadetodos

# Enable auto-start on boot
sudo systemctl enable lacasadetodos

# Disable auto-start on boot
sudo systemctl disable lacasadetodos
```

### Monitoring and Logs
```bash
# View real-time logs
sudo journalctl -u lacasadetodos -f

# View recent logs
sudo journalctl -u lacasadetodos --since "1 hour ago"

# View all logs for the service
sudo journalctl -u lacasadetodos

# Check if service is running
sudo systemctl is-active lacasadetodos
```

## 🌐 Nginx Reverse Proxy Setup (Recommended)

For production deployment, use Nginx as a reverse proxy:

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/lacasadetodos
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files directly
    location /static {
        alias /home/casa/CasaTodos/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Enable Nginx Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/lacasadetodos /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

## 🔒 SSL/HTTPS Setup with Let's Encrypt

For HTTPS (recommended for production):

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

## 🔥 Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow direct app access (optional)
sudo ufw allow 5000

# Check firewall status
sudo ufw status
```

## 📊 Production Configuration

### Environment Variables (Optional)
Create `/home/casa/CasaTodos/.env`:

```bash
nano /home/casa/CasaTodos/.env
```

```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_PATH=/home/casa/CasaTodos/nfl_fantasy.db
HOST=127.0.0.1
PORT=5000
```

### Update Service File for Environment Variables
```bash
sudo nano /etc/systemd/system/lacasadetodos.service
```

Add this line under `[Service]`:
```ini
EnvironmentFile=/home/casa/CasaTodos/.env
```

## 🔄 Auto-Update Setup (Optional)

Create an update script:

```bash
nano /home/casa/CasaTodos/update.sh
```

```bash
#!/bin/bash
cd /home/casa/CasaTodos
git pull origin main
./venv/bin/pip install -r requirements.txt
sudo systemctl restart lacasadetodos
```

```bash
# Make executable
chmod +x /home/casa/CasaTodos/update.sh
```

## 🧪 Testing the Setup

```bash
# Check if service is running
curl http://localhost:5000

# Check with domain (if using nginx)
curl http://your-domain.com

# Test from external network
curl http://your-server-ip
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check detailed status
sudo systemctl status lacasadetodos -l

# Check logs
sudo journalctl -u lacasadetodos --since "10 minutes ago"

# Check file permissions
ls -la /home/casa/CasaTodos/

# Check virtual environment
ls -la /home/casa/CasaTodos/venv/bin/

# Test virtual environment manually
/home/casa/CasaTodos/venv/bin/python --version
/home/casa/CasaTodos/venv/bin/python -c "import flask; print('Flask OK')"

# Test app manually as root (same as service)
cd /home/casa/CasaTodos
sudo /home/casa/CasaTodos/venv/bin/python app.py

# If venv issues, recreate it
cd /home/casa/CasaTodos
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
sudo chown -R root:root venv
```

### Database Issues
```bash
# Reset database
cd /home/casa/CasaTodos
sudo -u casa ./venv/bin/python setup_database.py

# Check database permissions
ls -la /home/casa/CasaTodos/nfl_fantasy.db
```

### Network Issues
```bash
# Check if port is in use
sudo netstat -tlnp | grep :5000

# Check firewall
sudo ufw status

# Test internal connection
curl http://127.0.0.1:5000
```

## 📱 Access Your Application

After setup:
- **Direct Access**: `http://your-server-ip:5000`
- **With Nginx**: `http://your-domain.com`
- **With SSL**: `https://your-domain.com`

## 🎉 Success!

Your La Casa de Todos NFL Fantasy League is now running as a production service on Ubuntu! The service will:

- ✅ Start automatically on server boot
- ✅ Restart automatically if it crashes
- ✅ Run in the background
- ✅ Handle multiple users simultaneously
- ✅ Serve the family fantasy league 24/7

## 📞 Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u lacasadetodos -f`
2. Verify service status: `sudo systemctl status lacasadetodos`
3. Test manual startup: `cd /home/casa/CasaTodos && ./venv/bin/python app.py`
4. Check firewall and network settings

## 🔧 Alternative Service Configuration (If Virtual Environment Issues)

If you continue having issues with the virtual environment, try this simpler configuration:

### Install Dependencies Globally
```bash
# Install Python packages globally instead of venv
sudo apt install python3-flask python3-sqlite3 python3-werkzeug python3-pytz -y

# Or use pip3 globally
sudo pip3 install flask sqlite3 werkzeug pytz
```

### Simple Service File (No Virtual Environment)
```bash
sudo nano /etc/systemd/system/lacasadetodos-simple.service
```

```ini
[Unit]
Description=La Casa de Todos NFL Fantasy League (Simple)
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/casa/CasaTodos
ExecStart=/usr/bin/python3 /home/casa/CasaTodos/app.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=lacasadetodos

[Install]
WantedBy=multi-user.target
```

### Enable Simple Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable lacasadetodos-simple
sudo systemctl start lacasadetodos-simple
sudo systemctl status lacasadetodos-simple
```
