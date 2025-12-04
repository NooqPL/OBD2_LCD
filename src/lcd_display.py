import time
from src.i2c_lock import lock as i2c_lock
try:
    from RPLCD.i2c import CharLCD
except Exception as e:
    print("[LCD] LCD unavailable:", e)
    CharLCD = None


def start_lcd_loop():
    if CharLCD is None:
        print("[LCD] Skipping LCD loop – no LCD connected.")
        return

    # --- KONFIGURACJA LCD (DOSTOSUJ ADRES!) ---
    lcd = CharLCD(
        i2c_expander='PCF8574',
        address=0x27,           # <-- zmień jeśli masz inny adres
        port=1,
        cols=16,
        rows=4,
        dotsize=8,
        charmap='A02',
        auto_linebreaks=True
    )
    time.sleep(0.2)
    print("[LCD] LCD started. Loop running...")

 

   # try:
    #while True:
    with i2c_lock:
        lcd.clear()
        lcd.write_string("Test")
        time.sleep(1)

    #except KeyboardInterrupt:
     #   lcd.clear()
     #   lcd.write_string("Exiting...")
     #   time.sleep(0.5)
     #   lcd.clear()
     #   print("[LCD] Stopped.")
