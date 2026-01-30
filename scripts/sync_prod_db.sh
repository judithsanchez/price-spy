#!/bin/bash
# sync_prod_db.sh - Run this on your Local machine (WSL)
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# --- Configuration ---
if [ -f .env ]; then
    # Manually parse specific variables to avoid sourcing issues
    PI_HOST=$(grep "^PI_HOST=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    PI_USER=$(grep "^PI_USER=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    PI_PATH=$(grep "^PI_PATH=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
fi

if [ -z "$PI_HOST" ]; then
    echo "❌ Error: PI_HOST not set in .env"
    exit 1
fi
# Default defaults if not set
PI_USER="${PI_USER:-pi}"
PI_PATH="${PI_PATH:-/home/pi/price-spy}"
# ---------------------

echo "🔄 Syncing Production Database from $PI_HOST..."

# Create backup of current local db
if [ -f data/pricespy.db ]; then
    echo "💾 Backing up local DB to data/pricespy.db.bak_$(date +%Y%m%d_%H%M%S)"
    cp data/pricespy.db data/pricespy.db.bak_$(date +%Y%m%d_%H%M%S)
fi

echo "📡 Transferring database..."
# Fix local permissions if needed (in case Docker created the file as root)
if [ -f data/pricespy.db ]; then
    sudo chown $USER:$USER data/pricespy.db
fi

scp "$PI_USER@$PI_HOST:$PI_PATH/data/pricespy.db" data/pricespy.db

echo "✅ Sync Complete! Your local env is now using production data."
