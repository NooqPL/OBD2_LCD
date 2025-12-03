import threading
import time



i2c_lock = threading.Lock()

print("=== MX5 OBD Display System Boot ===")

# ---------------------------------------------------------
# LOAD MODULES
# ---------------------------------------------------------

# --- OBD -------------------------------------------------
try:
    from src.obd_loop import start_obd_loop
    obd_available = True
except Exception as e:
    print("[OBD] Failed to load module:", e)
    def start_obd_loop():
        print("[OBD] OBD not available")
    obd_available = False


# --- LCD -------------------------------------------------
try:
    from src.lcd_display import start_lcd_loop
    lcd_available = True
except Exception as e:
    print("[LCD] Failed to load module:", e)
    def start_lcd_loop():
        print("[LCD] LCD not available")
    lcd_available = False


# --- OLED ------------------------------------------------
try:
    from src.oled_display import start_oled_loop
    oled_available = True
except Exception as e:
    print("[OLED] Failed to load module:", e)
    def start_oled_loop():
        print("[OLED] OLED not available")
    oled_available = False


# --- WEB SERVER -----------------------------------------
try:
    from src.web.server import start_web
except Exception as e:
    print("[WEB] Cannot load web server:", e)
    raise


# ---------------------------------------------------------
# RUN SYSTEM
# ---------------------------------------------------------

if __name__ == "__main__":
    print("[MAIN] Starting MX5 system...\n")

    # --- OBD THREAD ---
    if obd_available:
        print("[MAIN] Starting OBD thread...")
    threading.Thread(target=start_obd_loop, daemon=True).start()

    # --- LCD THREAD ---
    if lcd_available:
        print("[MAIN] Starting LCD thread...")
        threading.Thread(target=start_lcd_loop, daemon=True).start()
    else:
        print("[MAIN] LCD not available, skipped.")

    # --- OLED THREAD ---
    if oled_available:
        print("[MAIN] Starting OLED thread...")
        threading.Thread(target=start_oled_loop, daemon=True).start()
    else:
        print("[MAIN] OLED not available, skipped.")

    # --- WEB SERVER (MAIN THREAD) ---
    print("\n[MAIN] Starting Web UI...")
    start_web()

    print("[MAIN] Web server stopped. Exiting.")
