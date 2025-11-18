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

run() {
    echo ">>> Running: $*"
    if ! "$@"; then
        echo "!!! ERROR: Command failed: $*"
    fi
}

# ============================================
# SYSTEM UPDATE
# ============================================
run sudo apt update
run sudo apt upgrade -y

# ============================================
# INSTALL DEPENDENCIES
# ============================================
run sudo apt install -y \
    git \
    pigpio \
    python3 \
    python3-pip \
    python3-venv \
    python3-smbus \
    i2c-tools \
    avahi-daemon avahi-utils    # // CHANGED: added mDNS packages

# ============================================
# ENABLE I²C // CHANGED
# ============================================
run sudo raspi-config nonint do_i2c 0

# Enable pigpio daemon
run sudo systemctl enable --now pigpiod

# ============================================
# CLONE OR UPDATE REPO
# ============================================
if [ -d "$APP_DIR" ]; then
    echo "Repository already exists. Updating..."
    run sudo -u $USER_NAME git -C "$APP_DIR" fetch --all
    run sudo -u $USER_NAME git -C "$APP_DIR" reset --hard origin/main
else
    echo "Cloning repository..."
    run sudo -u $USER_NAME git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

# ============================================
# CREATE VENV
# ============================================
if [ ! -d ".venv" ]; then
    run sudo -u $USER_NAME python3 -m venv .venv
fi

# Upgrade pip
run sudo -u $USER_NAME .venv/bin/pip install --upgrade pip

# ============================================
# PYTHON DEPENDENCIES
# ============================================
run sudo -u $USER_NAME .venv/bin/pip install \
    obd \
    RPLCD \
    pigpio \
    smbus2               # // CHANGED: added smbus2 manually

# Flask if using web UI
if [ ! -z "$(grep -R \"from flask\" -n src 2>/dev/null)" ]; then
    echo "Detected Flask usage — installing Flask"   # // CHANGED
    run sudo -u $USER_NAME .venv/bin/pip install flask
fi

# Install requirements if file exists
if [ -f "requirements.txt" ]; then
    run sudo -u $USER_NAME .venv/bin/pip install -r requirements.txt
fi

# ============================================
# COPY SYSTEMD SERVICES
# ============================================
run sudo cp systemd/${SERVICE_NAME}.service /etc/systemd/system/
run sudo cp systemd/update-repo.service /etc/systemd/system/
run sudo cp systemd/update-repo.timer /etc/systemd/system/

run sudo systemctl daemon-reload

# Enable services
run sudo systemctl enable --now ${SERVICE_NAME}.service
run sudo systemctl enable --now update-repo.timer

echo "=== INSTALL COMPLETE ==="
echo " "

# ============================================
# FINAL CHECKLIST
# ============================================
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
