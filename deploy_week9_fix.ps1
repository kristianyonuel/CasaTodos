# PowerShell script to deploy Week 9 fix to Azure VM
# Run this in PowerShell to deploy everything to the server

Write-Host "🚀 DEPLOYING WEEK 9 FIX TO SERVER" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Server details
$SERVER = "casa@20.157.116.145"
$SERVER_PATH = "/home/casa/CasaTodos"

Write-Host "📁 Uploading diagnostic scripts..." -ForegroundColor Yellow

# Upload files using scp
scp check_server_database.py "${SERVER}:${SERVER_PATH}/"
scp copy_week9_to_server.py "${SERVER}:${SERVER_PATH}/"
scp nfl_fantasy.db "${SERVER}:${SERVER_PATH}/nfl_fantasy.db.local_copy"

Write-Host "✅ Files uploaded successfully" -ForegroundColor Green

Write-Host "🔧 Executing server-side operations..." -ForegroundColor Yellow

# Execute commands on server
$commands = @"
cd /home/casa/CasaTodos

echo "📋 Running database diagnostics..."
python3 check_server_database.py

echo "🗃️ Backing up current database..."
cp nfl_fantasy.db nfl_fantasy.db.backup_`$(date +%s)

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
"@

ssh $SERVER $commands

Write-Host "🌟 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Your Week 9 data should now be visible in the admin interface" -ForegroundColor Cyan
Write-Host "URL: https://lacasadetodos.org/admin" -ForegroundColor Cyan