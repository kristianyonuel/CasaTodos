
# Upload local database to server
scp nfl_fantasy.db casa@20.157.116.145:/home/casa/CasaTodos/nfl_fantasy.db.new

# Connect to server and replace database
ssh casa@20.157.116.145 << 'EOF'
cd /home/casa/CasaTodos

# Backup current database
cp nfl_fantasy.db nfl_fantasy.db.backup_$(date +%s)

# Replace with new database
mv nfl_fantasy.db.new nfl_fantasy.db

# Set correct permissions
chmod 644 nfl_fantasy.db
chown casa:casa nfl_fantasy.db

# Restart Flask service
sudo systemctl stop lacasadetodos.service
sleep 3
sudo systemctl start lacasadetodos.service

echo "Database updated and service restarted!"
EOF
