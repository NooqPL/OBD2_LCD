from RPLCD.i2c import CharLCD
import obd
import time

lcd = CharLCD('PCF8574', 0x27)
lcd.clear()
lcd.write_string("Mazda LCD READY")

connection = obd.OBD()

while True:
    rpm = connection.query(obd.commands.RPM).value
    lcd.clear()
    lcd.write_string(f"RPM: {int(rpm) if rpm else 0}")
    time.sleep(0.2)
