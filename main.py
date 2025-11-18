import threading
from src.obd_reader import start_obd_loop

try:
    from src.lcd_display import start_lcd_loop
except Exception as e:
    print("[LCD] Failed to load LCD module:", e)
    start_lcd_loop = None

from src.web.server import start_web

if __name__ == "__main__":
    # OBD zawsze startuje
    threading.Thread(target=start_obd_loop, daemon=True).start()

    # LCD tylko jeśli działa
    if start_lcd_loop:
        threading.Thread(target=start_lcd_loop, daemon=True).start()
    else:
        print("[LCD] LCD thread not started because LCD module failed.")

    # Uruchom serwer WWW
    start_web()
