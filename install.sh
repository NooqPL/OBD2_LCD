#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/NooqPL/OBD2_LCD"
APP_DIR="/home/mx5/app"
SERVICE_NAME="ob2_lcd"
USER_NAME="mx5"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo "=== mx5 installer ==="

# Function to run commands and report errors
run() {
    echo ">>> Running: $*"
    if ! "$@"; then
        echo "!!! ERROR: Command failed: $*"
    fi
}

# Update system
run sudo apt update
run sudo apt upgrade -y

# Install dependencies
run sudo apt install -y \
    git \
    pigpio \
    python3 \
    python3-pip \
    python3-venv \
    python3-smbus \
    i2c-tools

# Enable pigpio daemon
run sudo systemctl enable --now pigpiod

# Clone or update repository
if [ -d "$APP_DIR" ]; then
    echo "Repository already exists. Updating..."
    run sudo -u $USER_NAME git -C "$APP_DIR" fetch --all
    run sudo -u $USER_NAME git -C "$APP_DIR" reset --hard origin/main
else
    echo "Cloning repository..."
    run sudo -u $USER_NAME git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

# Create virtual environment
if [ ! -d ".venv" ]; then
    run sudo -u $USER_NAME python3 -m venv .venv
fi

# Upgrade pip
run sudo -u $USER_NAME .venv/bin/pip install --upgrade pip

# Install Python dependencies for OBD & LCD
run sudo -u $USER_NAME .venv/bin/pip install \
    obd \
    RPLCD \
    pigpio

# Install requirements if exist
if [ -f "requirements.txt" ]; then
    run sudo -u $USER_NAME .venv/bin/pip install -r requirements.txt
fi

# Copy systemd services
run sudo cp systemd/${SERVICE_NAME}.service /etc/systemd/system/
run sudo cp systemd/update-repo.service /etc/systemd/system/
run sudo cp systemd/update-repo.timer /etc/systemd/system/

run sudo systemctl daemon-reload

# Enable services
run sudo systemctl enable --now ${SERVICE_NAME}.service
run sudo systemctl enable --now update-repo.timer

echo "=== INSTALL COMPLETE ==="
echo " "

# Final checklist
echo "=== FINAL CHECKLIST ==="
for cmd in git python3 pip3 pigpiod i2cdetect; do
    if command -v $cmd >/dev/null 2>&1; then
        printf "[${GREEN}OK${NC}] %s installed\n" "$cmd"
    else
        printf "[${RED}MISSING${NC}] %s not found\n" "$cmd"
    fi
done

for svc in pigpiod ${SERVICE_NAME} update-repo.timer; do
    if systemctl is-active --quiet $svc; then
        printf "[${GREEN}RUNNING${NC}] %s service active\n" "$svc"
    else
        printf "[${RED}STOPPED${NC}] %s service not running\n" "$svc"
    fi
done

echo " "
echo "Installation finished. Check above for errors."
echo " "
