import time
from threading import Event
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

# Globalne dane do wyświetlania
obd_data = {
    "connected": False,
    "speed": 0,
    "rpm": 0,
    "temp": 0
}

stop_event = Event()

# Ładowanie czcionki
font_small = ImageFont.load_default()
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

def show_boot_logo(device):
    """
    Pokazuje bitmapę startową (128x64 PNG)
    """
    try:
        img = Image.open("assets/boot_logo.png").convert("1")
        img = img.resize((device.width, device.height))
        device.display(img)
        time.sleep(2)
    except Exception as e:
        print("[OLED] Boot logo error:", e)


def show_obd_status(device):
    """
    Pokazuje status połączenia OBD
    """
    img = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(img)

    draw.text((10, 10), "OBD Connecting...", font=font_small, fill=255)
    if obd_data["connected"]:
        draw.text((10, 30), "Status: CONNECTED", font=font_small, fill=255)
    else:
        draw.text((10, 30), "Status: WAITING", font=font_small, fill=255)

    device.display(img)


def show_drive_screen(device):
    """
    Główny ekran jazdy: speed, rpm, temp
    """
    img = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), f"{obd_data['speed']:>3} km/h", font=font_big, fill=255)
    draw.text((0, 25), f"{obd_data['rpm']:>4} RPM", font=font_small, fill=255)
    draw.text((0, 45), f"{obd_data['temp']} C", font=font_small, fill=255)

    device.display(img)


def start_oled_loop():
    print("[OLED] Initializing OLED...")

    try:
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)
    except Exception as e:
        print("[OLED] FAILED to init OLED:", e)
        return

    print("[OLED] OK")

    # 1) Logo startowe
    show_boot_logo(device)

    # 2) Czekanie na OBD
    for _ in range(5):
        if obd_data["connected"]:
            break
        show_obd_status(device)
        time.sleep(1)

    # 3) Ekran jazdy
    print("[OLED] Start display loop")

    while not stop_event.is_set():
        show_drive_screen(device)
        time.sleep(0.15)
