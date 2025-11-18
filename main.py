import threading
from src.obd_reader import start_obd_loop
from src.lcd_display import start_lcd_loop
from src.web.server import start_web

if __name__ == "__main__":
    threading.Thread(target=start_obd_loop, daemon=True).start()
    threading.Thread(target=start_lcd_loop, daemon=True).start()
    start_web()
