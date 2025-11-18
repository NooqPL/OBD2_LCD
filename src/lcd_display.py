import time

try:
    from RPLCD.i2c import CharLCD
except Exception as e:
    print("[LCD] LCD unavailable:", e)
    CharLCD = None


from .data_model import data

lcd = CharLCD('PCF8574', 0x27)

def start_lcd_loop():
    if CharLCD is None:
        print("[LCD] Skipping LCD loop because LCD driver failed to load.")
        return
    while True:
        lcd.clear()
        lcd.write_string(f"RPM:{data['rpm']}")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"SPD:{data['speed']} T:{data['coolant']}")
        time.sleep(0.3)
