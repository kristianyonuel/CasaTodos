#!/bin/bash
# Script to upload and deploy Week 9 fix on Azure VM
# Run this locally to deploy everything to the server

echo "🚀 DEPLOYING WEEK 9 FIX TO SERVER"
echo "=================================="

# Server details
SERVER="casa@20.157.116.145"
SERVER_PATH="/home/casa/CasaTodos"

echo "📁 Uploading diagnostic scripts..."
scp check_server_database.py $SERVER:$SERVER_PATH/
scp copy_week9_to_server.py $SERVER:$SERVER_PATH/
scp nfl_fantasy.db $SERVER:$SERVER_PATH/nfl_fantasy.db.local_copy

echo "✅ Files uploaded successfully"

echo "🔧 Executing server-side operations..."
ssh $SERVER << 'EOF'
cd /home/casa/CasaTodos

echo "📋 Running database diagnostics..."
python3 check_server_database.py

echo "🗃️ Backing up current database..."
cp nfl_fantasy.db nfl_fantasy.db.backup_$(date +%s)

echo "📦 Copying Week 9 data to server database..."
python3 copy_week9_to_server.py

echo "🔄 Restarting Flask service..."
sudo systemctl stop lacasadetodos.service
sleep 3
sudo systemctl start lacasadetodos.service
sleep 5

echo "✅ Service status:"
sudo systemctl status lacasadetodos.service --no-pager -l

echo "🎯 Week 9 deployment complete!"
echo "👀 Check admin interface for Week 9 picks now"
EOF

echo "🌟 DEPLOYMENT COMPLETE!"
echo "Your Week 9 data should now be visible in the admin interface"
echo "URL: https://lacasadetodos.org/admin"