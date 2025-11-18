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

printf "=== ${YELLOW}mx5 installer${NC} ===\n"

run() {
    echo ">>> Running: $*"
    if ! "$@"; then
        echo "!!! ERROR: Command failed: $*"
    fi
}

echo "============================================"
printf " ${YELLOW}SYSTEM UPDATE${NC}\n"
echo "============================================"

run sudo apt update
run sudo apt upgrade -y


echo "============================================"
printf " ${YELLOW}INSTALL DEPENDENCIES${NC}\n"
echo "============================================"
run sudo apt install -y \
    git \
    pigpio \
    python3 \
    python3-pip \
    python3-venv \
    python3-smbus \
    i2c-tools \
    avahi-daemon avahi-utils    # // CHANGED: added mDNS packages


echo "============================================"
printf " ${YELLOW}ENABLE I²C // CHANGED${NC}\n"
echo "============================================"
run sudo raspi-config nonint do_i2c 0




# Enable pigpio daemon
printf "${YELLOW}Enable pigpio daemon${NC}\n"
run sudo systemctl enable --now pigpiod


echo "============================================"
printf " ${YELLOW}CLONE OR UPDATE REPO${NC}\n"
echo "============================================"
if [ -d "$APP_DIR" ]; then
    printf "${YELLOW}Repository already exists. Updating...${NC}\n"
    run sudo -u $USER_NAME git -C "$APP_DIR" fetch --all
    run sudo -u $USER_NAME git -C "$APP_DIR" reset --hard origin/main
else
    printf "${YELLOW}Cloning repository...${NC}\n"
    run sudo -u $USER_NAME git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "============================================"
printf " ${YELLOW}CREATE VENV${NC}\n"
echo "============================================"
if [ ! -d ".venv" ]; then
    run sudo -u $USER_NAME python3 -m venv .venv
fi

# Upgrade pip
run sudo -u $USER_NAME .venv/bin/pip install --upgrade pip

echo "============================================"
printf " ${YELLOW}PYTHON DEPENDENCIES${NC}\n"
echo "============================================"
run sudo -u $USER_NAME .venv/bin/pip install \
    obd \
    RPLCD \
    pigpio \
    flask \
    smbus2               # // CHANGED: added smbus2 manually

# Flask if using web UI
if [ ! -z "$(grep -R \"from flask\" -n src 2>/dev/null)" ]; then
    printf "${YELLOW}Detected Flask usage — installing Flask${NC}\n"   # // CHANGED
    run sudo -u $USER_NAME .venv/bin/pip install flask
fi

# Install requirements if file exists
printf " ${YELLOW}Install requirements if file exists${NC}\n "
if [ -f "requirements.txt" ]; then
    run sudo -u $USER_NAME .venv/bin/pip install -r requirements.txt
fi

echo "============================================"
printf " ${YELLOW}COPY SYSTEMD SERVICES${NC}\n"
echo "============================================"
run sudo cp systemd/${SERVICE_NAME}.service /etc/systemd/system/
run sudo cp systemd/update-repo.service /etc/systemd/system/
run sudo cp systemd/update-repo.timer /etc/systemd/system/

run sudo systemctl daemon-reload

# Enable services
printf " ${YELLOW}Enable services${NC}\n "
run sudo systemctl enable --now ${SERVICE_NAME}.service
run sudo systemctl enable --now update-repo.timer

printf "=== ${YELLOW}INSTALL COMPLETE${NC}\n ===" 
echo " "


# FINAL CHECKLIST
echo "============================================"
printf "=== ${YELLOW}FINAL CHECKLIST${NC} ==="
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
printf "${YELLOW}Installation finished. Check above for errors.${NC}"
echo " "
