import u8g2

oled = u8g2.U8G2_SSD1306_128X64_NONAME_F_HW_I2C(
    u8g2.U8G2_R0, 
    scl=3, 
    sda=2, 
    i2c_bus=1
)

oled.begin()
oled.clearBuffer()
oled.setFont(u8g2.U8G2_FONT_6X12_TR)
oled.drawStr(0, 12, "OLED OK!")
oled.sendBuffer()


def start_oled_loop():
    print("[OLED] Init...")
    oled.begin()

    while True:
        oled.clearBuffer()
        oled.setFont(u8g2.U8G2_FONT_6X12_TR)
        oled.drawStr(0, 12, "MX5 OLED OK!")
        oled.sendBuffer()
        time.sleep(1)

