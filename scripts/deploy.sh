#!/bin/bash
# deploy.sh - Run this on the Raspberry Pi
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "🚀 Starting Deployment..."

echo "📥 Pulling latest changes..."
git pull origin main

echo "🐍 Running migrations..."
./venv/bin/python3 scripts/db_manager.py migrate

echo "🐳 Restarting containers..."
docker compose -f infrastructure/docker-compose.yml up --build -d

echo "🧹 Cleaning up..."
./venv/bin/python3 scripts/db_manager.py cleanup

echo "✅ Deployment Successful!"
