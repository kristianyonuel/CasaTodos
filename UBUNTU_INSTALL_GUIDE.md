# 🐧 CasaTodos NFL Fantasy - Ubuntu Installation Guide

## Complete Setup from Scratch on Ubuntu Server

### 🚀 Quick Install Script
```bash
#!/bin/bash
# Run this entire script to set up CasaTodos on Ubuntu

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git python3.13 python3.13-venv python3.13-dev python3-pip nginx ufw

# Clone the repository
cd /home/$USER
git clone https://github.com/kristianyonuel/CasaTodos.git
cd CasaTodos

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up database
python3 setup_database.py

# Make scripts executable
chmod +x setup_ubuntu_service.sh

echo "✅ Installation complete!"
echo "🚀 To start the app: python3 app.py"
echo "🌐 Access at: http://your-server-ip"
```

---

## 📋 Step-by-Step Installation

### 1. **System Prerequisites**
```bash
# Update Ubuntu packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y git python3.13 python3.13-venv python3.13-dev python3-pip curl wget
```

### 2. **Clone the Repository**
```bash
# Navigate to home directory
cd /home/$USER

# Clone from GitHub
git clone https://github.com/kristianyonuel/CasaTodos.git

# Enter project directory
cd CasaTodos
```

### 3. **Python Environment Setup**
```bash
# Create virtual environment
python3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### 4. **Database Setup**
```bash
# Initialize the database
python3 setup_database.py

# Verify database was created
ls -la nfl_fantasy.db
```

### 5. **Environment Configuration** (Optional)
```bash
# Create environment file for production settings
cat > .env << EOF
NFL_API_SSL_VERIFY=true
FLASK_ENV=production
FLASK_DEBUG=false
EOF
```

### 6. **Test the Application**
```bash
# Start the development server
python3 app.py

# Test in another terminal
curl http://localhost:5000
```

---

## 🔧 Production Setup (Optional)

### **Install as System Service**
```bash
# Make service script executable
chmod +x setup_ubuntu_service.sh

# Run the service setup (creates systemd service)
sudo ./setup_ubuntu_service.sh

# Start the service
sudo systemctl start casatodos
sudo systemctl enable casatodos

# Check service status
sudo systemctl status casatodos
```

### **Nginx Reverse Proxy** (Optional)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/casatodos << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/casatodos /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### **Firewall Setup**
```bash
# Configure UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

---

## 🔍 Verification & Testing

### **Check Installation**
```bash
# Verify Python environment
source .venv/bin/activate
python3 --version
pip list

# Check database
python3 -c "import sqlite3; print('Database OK' if sqlite3.connect('nfl_fantasy.db') else 'Database Error')"

# Test API connectivity
python3 -c "
import requests
try:
    response = requests.get('https://api.nfl.com/v1/current/teams', verify=True, timeout=10)
    print('✅ API connectivity: OK')
except Exception as e:
    print(f'❌ API connectivity: {e}')
"
```

### **Access the Application**
- **Direct**: `http://your-server-ip:5000`
- **With Nginx**: `http://your-server-ip` or `http://your-domain.com`

### **Default Login Credentials**
- **Admin**: `admin` / `family123`
- **Users**: `dad`, `mom`, `son`, `daughter`, `uncle`, `cousin` / `family123`

---

## 🔐 Latest Features (Just Added!)

### **Case-Insensitive Login**
- Users can login with any case: `admin`, `ADMIN`, `Admin`, etc.
- Prevents duplicate usernames with different cases

### **Fixed Admin Password Reset**
- Admins can now reset user passwords without errors
- Fixed "NOT NULL constraint" issue

### **CSV Export/Import with Username Headers**
- **Export**: Usernames as column headers, picks as rows
- **Import**: Bulk upload picks from CSV files
- **Format**: `Username1,Username2,Username3...` then `Pick1,Pick2,Pick3...`

---

## 🚨 Troubleshooting

### **Common Issues**

**1. Permission Denied**
```bash
sudo chown -R $USER:$USER /home/$USER/CasaTodos
chmod +x setup_ubuntu_service.sh
```

**2. Python Module Not Found**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Database Issues**
```bash
rm -f nfl_fantasy.db
python3 setup_database.py
```

**4. SSL Certificate Issues**
```bash
export NFL_API_SSL_VERIFY=false  # Development only
python3 app.py
```

**5. Port Already in Use**
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```

### **Log Files**
```bash
# Application logs
tail -f app.log

# System service logs (if using systemd)
sudo journalctl -u casatodos -f

# Nginx logs (if using Nginx)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify all dependencies are installed
4. Ensure the virtual environment is activated

**Latest Updates**: All recent fixes including case-insensitive login and password reset are now available in the GitHub repository.

---

## 🎯 Quick Start Summary

```bash
# One-liner installation
curl -sSL https://raw.githubusercontent.com/kristianyonuel/CasaTodos/main/install.sh | bash

# Or manual installation
git clone https://github.com/kristianyonuel/CasaTodos.git
cd CasaTodos
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 setup_database.py
python3 app.py
```

🎉 **Your NFL Fantasy app is now ready on Ubuntu!**
