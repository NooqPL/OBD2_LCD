import time
from RPLCD.i2c import CharLCD
from .data_model import data

lcd = CharLCD('PCF8574', 0x27)

def start_lcd_loop():
    while True:
        lcd.clear()
        lcd.write_string(f"RPM:{data['rpm']}")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"SPD:{data['speed']} T:{data['coolant']}")
        time.sleep(0.3)
