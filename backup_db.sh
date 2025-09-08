#!/bin/bash
# Emergency backup script for NFL Fantasy database
# Run this before any admin operations

DB_FILE="nfl_fantasy.db"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/nfl_fantasy_backup_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "🔄 Creating database backup..."
cp "$DB_FILE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t ${BACKUP_DIR}/nfl_fantasy_backup_*.db | tail -n +11 | xargs -r rm
    echo "📁 Cleaned old backups (keeping last 10)"
else
    echo "❌ Backup failed!"
    exit 1
fi
