import time

try:
    from RPLCD.i2c import CharLCD
except Exception as e:
    print("[LCD] LCD unavailable:", e)
    CharLCD = None

def start_lcd_loop():
    if CharLCD is None:
        print("[LCD] Skipping LCD loop – no LCD connected.")
        return

    # Tu dodasz kod gdy podłączysz LCD
    while True:
        time.sleep(1)
