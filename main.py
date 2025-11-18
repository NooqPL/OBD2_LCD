import threading

# OBD tymczasowo wyłączony – brak sprzętu
def start_obd_loop():
    print("[OBD] OBD disabled (no hardware connected)")

try:
    from src.lcd_display import start_lcd_loop
except Exception as e:
    print("[LCD] Failed to load LCD module:", e)
    start_lcd_loop = None

from src.web.server import start_web

if __name__ == "__main__":
    # OBD stub
    threading.Thread(target=start_obd_loop, daemon=True).start()

    # LCD tylko jeśli działa (na razie nie działa)
    if start_lcd_loop:
        threading.Thread(target=start_lcd_loop, daemon=True).start()
    else:
        print("[LCD] LCD thread not started (no device)")

    # Web server always runs
    start_web()
