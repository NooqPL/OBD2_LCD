import time
import obd

from src.data_model import obd_data

def start_obd_loop():
    print("[OBD] Connecting to OBD...")

    try:
        connection = obd.Async()
    except:
        print("[OBD] ERROR: no adapter found")
        return

    if connection.is_connected():
        print("[OBD] Connected")
        obd_data["connected"] = True

    else:
        print("[OBD] Not connected")
        return

    # Subskrypcje
    connection.watch(obd.commands.SPEED)
    connection.watch(obd.commands.RPM)
    connection.watch(obd.commands.COOLANT_TEMP)
    connection.start()

    while True:
        if connection.is_connected():
            speed = connection.query(obd.commands.SPEED)
            rpm = connection.query(obd.commands.RPM)
            temp = connection.query(obd.commands.COOLANT_TEMP)

            obd_data["speed"] = speed.value.magnitude if speed.value else 0
            obd_data["rpm"] = int(rpm.value.magnitude) if rpm.value else 0
            obd_data["temp"] = int(temp.value.magnitude) if temp.value else 0

        time.sleep(0.1)
