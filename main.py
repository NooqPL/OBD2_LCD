import threading

# --- OBD (tymczasowo wyłączony) -------------------------
def start_obd_loop():
    print("[OBD] OBD disabled (no hardware connected)")


# --- LCD -------------------------------------------------
try:
    from src.lcd_display import start_lcd_loop
    lcd_available = True
except Exception as e:
    print("[LCD] Failed to load LCD module:", e)
    start_lcd_loop = None
    lcd_available = False


# --- OLED ------------------------------------------------
try:
    from src.oled_display import start_oled_loop
    oled_available = True
except Exception as e:
    print("[OLED] Failed to load OLED module:", e)
    start_oled_loop = None
    oled_available = False


# --- WEB SERVER -----------------------------------------
from src.web.server import start_web


# --- MAIN ------------------------------------------------
if __name__ == "__main__":
    print("=== Starting MX5 OBD Display System ===")

    # OBD
    threading.Thread(target=start_obd_loop, daemon=True).start()

    # LCD
    if lcd_available:
        print("[LCD] Starting LCD thread...")
        threading.Thread(target=start_lcd_loop, daemon=True).start()
    else:
        print("[LCD] LCD thread NOT started")

    # OLED
    if oled_available:
        print("[OLED] Starting OLED thread...")
        threading.Thread(target=start_oled_loop, daemon=True).start()
    else:
        print("[OLED] OLED thread NOT started")

    # Web server (główny wątek)
    print("[WEB] Starting web server...")
    start_web()
