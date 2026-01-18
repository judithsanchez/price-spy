# Raspberry Pi Setup Guide

A step-by-step guide to run Price Spy on your Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (2GB+ RAM recommended) or Raspberry Pi 5
- Raspberry Pi OS (64-bit recommended for better Docker performance)
- MicroSD card (16GB+ recommended)
- Internet connection

## Step 1: Install Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash Raspberry Pi OS (64-bit) to your SD card
3. Enable SSH during setup (click the gear icon in Imager)
4. Boot your Pi and connect via SSH or directly

## Step 2: Update Your System

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 3: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
exit
# SSH back in or reboot
```

Verify Docker is working:
```bash
docker --version
docker run hello-world
```

## Step 4: Install Docker Compose

```bash
# Install docker-compose plugin
sudo apt install docker-compose-plugin -y

# Verify
docker compose version
```

## Step 5: Clone Price Spy

```bash
# Install git if needed
sudo apt install git -y

# Clone the repository
git clone https://github.com/YOUR_USERNAME/price-spy.git
cd price-spy
```

## Step 6: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the key (starts with `AIza...`)

## Step 7: Configure Environment

Create a `.env` file in the project root:

```bash
nano .env
```

Add your API key:
```
GEMINI_API_KEY=AIzaSy...your_key_here
```

Save and exit (Ctrl+X, Y, Enter).

## Step 8: Build and Start

```bash
# Build the Docker image (takes 5-10 minutes on Pi)
docker compose -f infrastructure/docker-compose.yml build

# Start the service
docker compose -f infrastructure/docker-compose.yml up -d
```

## Step 9: Access the Dashboard

Open a browser and go to:
```
http://YOUR_PI_IP:8000
```

Find your Pi's IP address with:
```bash
hostname -I
```

## Step 10: Add Sample Data (Optional)

To see how the UI looks with data:

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli seed-test-data
```

Refresh the dashboard to see sample products with prices.

---

## Useful Commands

### Start/Stop the Service

```bash
# Start
docker compose -f infrastructure/docker-compose.yml up -d

# Stop
docker compose -f infrastructure/docker-compose.yml down

# Restart
docker compose -f infrastructure/docker-compose.yml restart
```

### View Logs

```bash
# Follow logs in real-time
docker compose -f infrastructure/docker-compose.yml logs -f

# Last 100 lines
docker compose -f infrastructure/docker-compose.yml logs --tail 100
```

### Update to Latest Version

```bash
cd price-spy
git pull
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d
```

### Check Scheduler Status

```bash
curl http://localhost:8000/api/scheduler/status
```

### Trigger Manual Extraction

```bash
curl -X POST http://localhost:8000/api/scheduler/run-now
```

---

## Auto-Start on Boot

To make Price Spy start automatically when your Pi boots:

```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Create a startup script
nano ~/start-pricespy.sh
```

Add:
```bash
#!/bin/bash
cd /home/$USER/price-spy
docker compose -f infrastructure/docker-compose.yml up -d
```

Make it executable:
```bash
chmod +x ~/start-pricespy.sh
```

Add to crontab:
```bash
crontab -e
```

Add this line:
```
@reboot sleep 30 && /home/pi/start-pricespy.sh
```

---

## Troubleshooting

### "Permission denied" errors
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Low memory issues
If the Pi runs out of memory during build:
```bash
# Create swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Container won't start
```bash
# Check logs for errors
docker compose -f infrastructure/docker-compose.yml logs

# Rebuild from scratch
docker compose -f infrastructure/docker-compose.yml down
docker compose -f infrastructure/docker-compose.yml build --no-cache
docker compose -f infrastructure/docker-compose.yml up -d
```

### Can't access from other devices
Make sure port 8000 is not blocked:
```bash
# Check if service is listening
sudo netstat -tlnp | grep 8000
```

---

## Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| Storage | 16GB | 32GB+ |
| Pi Model | Pi 4 | Pi 4 (4GB) or Pi 5 |

The Chromium browser used for screenshots needs decent RAM. 2GB works but 4GB is more comfortable.

---

## Network Setup Tips

### Access from anywhere on your network
Use your Pi's hostname:
```
http://pricespy.local:8000
```

### Set a static IP (recommended)
Edit `/etc/dhcpcd.conf` or use your router's DHCP reservation.

### Remote access outside your network
Consider using:
- Tailscale (easiest)
- WireGuard VPN
- Cloudflare Tunnel

---

## Next Steps

1. Read the [User Guide](./USER_GUIDE.md) to learn how to use Price Spy
2. Add your own products and stores through the web UI
3. The scheduler will automatically check prices daily at 8:00 AM
