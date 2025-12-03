"""
src/oled_display.py

OLED driver for SSD1306 128x64 using luma.oled + PIL.
Provides:
 - global `obd_data` dict (other modules can import and update it)
 - start_oled_loop() entrypoint (main.py starts this in a thread)

Behavior:
 - shows a boot message for 2s
 - then shows a status screen ("OBD Connecting..." / "CONNECTED")
 - when obd_data["connected"] == True it switches to the drive screen
 - drive screen shows speed (km/h), RPM and coolant temp (°C)
"""

import time
from threading import Event
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import os

# Public data structure — other modules (e.g. src.obd_loop) should update this
obd_data = {
    "connected": False,
    "speed": 0,   # km/h
    "rpm": 0,     # RPM
    "temp": 0     # °C
}

# Internal stop event (not used by main.py by default, but handy for tests)
stop_event = Event()

# OLED config
I2C_PORT = 1
I2C_ADDRESS = 0x3C  # you said 0x3C
WIDTH = 128
HEIGHT = 64

# Fonts: try to load a TTF for bigger text, otherwise use the default bitmap font
def _load_fonts():
    try:
        # DejaVuSans is usually present on Raspbian; size tuned for 128x64
        big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        return big, med, small
    except Exception:
        # fallback to builtin fonts
        return ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default()

FONT_BIG, FONT_MED, FONT_SMALL = _load_fonts()

def _init_device():
    """Initialize and return the luma ssd1306 device or raise."""
    serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
    device = ssd1306(serial, width=WIDTH, height=HEIGHT)
    # ensure display is cleared on start
    try:
        device.clear()
    except Exception:
        # some luma versions use device.display(Image) instead of clear()
        img = Image.new("1", (WIDTH, HEIGHT))
        device.display(img)
    return device

# helper draw functions
from PIL import Image  # placed after _init_device reference for readability

def _show_boot(device):
    """Show a simple boot/title screen (2 seconds)."""
    img = Image.new("1", (WIDTH, HEIGHT), color=0)
    draw = ImageDraw.Draw(img)
    text = "MX-5 OBD"
    w, h = draw.textsize(text, font=FONT_BIG)
    draw.text(((WIDTH - w) // 2, 8), text, font=FONT_BIG, fill=255)

    subtitle = "Starting..."
    w2, h2 = draw.textsize(subtitle, font=FONT_MED)
    draw.text(((WIDTH - w2) // 2, 40), subtitle, font=FONT_MED, fill=255)

    device.display(img)
    time.sleep(2)

def _show_status(device):
    """Show OBD connection status screen."""
    img = Image.new("1", (WIDTH, HEIGHT), color=0)
    draw = ImageDraw.Draw(img)

    header = "OBD STATUS"
    w, _ = draw.textsize(header, font=FONT_MED)
    draw.text(((WIDTH - w) // 2, 6), header, font=FONT_MED, fill=255)

    if obd_data.get("connected"):
        status = "CONNECTED"
    else:
        status = "CONNECTING..."

    w2, _ = draw.textsize(status, font=FONT_BIG)
    draw.text(((WIDTH - w2) // 2, 26), status, font=FONT_BIG, fill=255)

    # small hints / ip or instructions (optional)
    hint = "Waiting for vehicle..." if not obd_data.get("connected") else "Receiving data"
    w3, _ = draw.textsize(hint, font=FONT_SMALL)
    draw.text(((WIDTH - w3) // 2, 56), hint, font=FONT_SMALL, fill=255)

    device.display(img)

def _show_drive(device):
    """Show main driving dashboard: speed, rpm, temp."""
    img = Image.new("1", (WIDTH, HEIGHT), color=0)
    draw = ImageDraw.Draw(img)

    # Speed large on top-left
    speed = int(obd_data.get("speed") or 0)
    speed_text = f"{speed:3d}"
    w_s, h_s = draw.textsize(speed_text, font=FONT_BIG)
    draw.text((2, 0), speed_text, font=FONT_BIG, fill=255)
    draw.text((2 + w_s + 2, 8), "km/h", font=FONT_SMALL, fill=255)

    # RPM on top-right / middle
    rpm = int(obd_data.get("rpm") or 0)
    rpm_text = f"{rpm} RPM"
    w_r, _ = draw.textsize(rpm_text, font=FONT_MED)
    draw.text((WIDTH - w_r - 2, 4), rpm_text, font=FONT_MED, fill=255)

    # Temp bottom-left
    temp = int(obd_data.get("temp") or 0)
    temp_text = f"Temp: {temp} C"
    draw.text((2, HEIGHT - 12), temp_text, font=FONT_SMALL, fill=255)

    device.display(img)

def start_oled_loop(poll_interval=0.12):
    """
    Entrypoint to run in a separate thread.
    poll_interval: seconds between screen updates in drive mode.
    """
    print("[OLED] Initializing...")
    try:
        device = _init_device()
    except Exception as e:
        print("[OLED] Failed to initialize display:", e)
        return

    print("[OLED] Display initialized (0x{:#x})".format(I2C_ADDRESS))

    # Boot splash
    try:
        _show_boot(device)
    except Exception as e:
        print("[OLED] Boot screen error:", e)

    # Show status for a little while or until connected
    status_phase_timeout = 6.0  # seconds
    start_t = time.time()
    while (time.time() - start_t) < status_phase_timeout and not obd_data.get("connected") and not stop_event.is_set():
        try:
            _show_status(device)
        except Exception as e:
            print("[OLED] Status screen error:", e)
        time.sleep(0.5)

    print("[OLED] Entering main loop")
    # Main loop: if connected show drive screen, otherwise show status
    while not stop_event.is_set():
        try:
            if obd_data.get("connected"):
                _show_drive(device)
            else:
                _show_status(device)
        except Exception as e:
            print("[OLED] Error updating screen:", e)
        time.sleep(poll_interval)

# Allow graceful shutdown if needed
def stop_oled():
    stop_event.set()
