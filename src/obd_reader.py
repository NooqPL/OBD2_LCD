import time
import obd
from .data_model import data

def start_obd_loop():
    connection = obd.OBD()

    while True:
        rpm = connection.query(obd.commands.RPM).value
        speed = connection.query(obd.commands.SPEED).value
        coolant = connection.query(obd.commands.COOLANT_TEMP).value

        data["rpm"] = int(rpm) if rpm else 0
        data["speed"] = int(speed) if speed else 0
        data["coolant"] = int(coolant) if coolant else 0

        time.sleep(0.2)
