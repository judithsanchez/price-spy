#!/bin/bash
# sync_prod_db.sh - Run this on your Local machine (WSL)
set -e

# --- Configuration ---
PI_HOST="100.117.106.90" # Tailscale IP for ha-pi
PI_PATH="/home/judithvsanchezc/Desktop/dev/price-spy" # Path to the project on the Pi
# ---------------------

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

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

scp "judithvsanchezc@$PI_HOST:$PI_PATH/data/pricespy.db" data/pricespy.db

echo "✅ Sync Complete! Your local env is now using production data."
