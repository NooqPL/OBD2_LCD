# src/oled_display.py
import time
import traceback
import obd


from threading import Thread
from src.i2c_lock import lock as i2c_lock

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

def start_oled_loop():
    print("[OLED] Initializing...")

    try:
        # --- konfiguracja OLED SSD1306 128x64 na I2C 0x3C ---
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial, width=128, height=64)
        print("[OLED] Device initialized successfully")
    except Exception as e:
        print("[OLED] ERROR: Failed to initialize OLED")
        traceback.print_exc()
        return

    # --- przygotowanie czcionki i obrazu ---
    font = ImageFont.load_default()  # prosta domyślna czcionka
    width = device.width
    height = device.height

    # --- Pętla główna OLED ---
    counter = 0 
    while True:
        try:
            # nowy obraz
            img = Image.new("1", (width, height))
            draw = ImageDraw.Draw(img)

            draw.text((10, 10), "MX-5 Booting...", font=font, fill=255)


            
            try:
                connection = obd.Async()
            except:
                draw.text((10, 30), "[OBD] ERROR NoAdFo", font=font, fill=255)
                return

            if connection.is_connected():
                draw.text((10, 30), "[OBD] Connected", font=font, fill=255)
                

            else:
                draw.text((10, 30), "[OBD] Not connected", font=font, fill=255)
                return







            draw.text((10, 45), f"Speed: {counter} km/h", font=font, fill=255)



            draw.text((10, 55), f"RPM: {counter+1}", font=font, fill=255)




            with i2c_lock:
                device.display(img)

            counter += 1 
            time.sleep(1)

        except Exception as e:
            print("[OLED] ERROR in loop")
            traceback.print_exc()
            time.sleep(1)
