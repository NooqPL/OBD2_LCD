import subprocess
import time

def setup_bluetooth(elm_mac: str):
    """
    Odblokowuje Bluetooth, podnosi interfejs hci0, paruje ELM327 i tworzy /dev/rfcomm0
    :param elm_mac: MAC adres ELM327
    """
    def run(cmd):
        """Uruchamia komendę w systemie i drukuje output"""
        print(f"[BLUETOOTH] Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    print("[BLUETOOTH] Starting setup...")

    # 1️⃣ Odblokowanie Bluetooth
    run("sudo rfkill unblock bluetooth")
    time.sleep(1)

    # 2️⃣ Podniesienie interfejsu hci0
    run("sudo hciconfig hci0 up")
    time.sleep(1)

    # 3️⃣ Sparowanie i ufanie ELM327
    print(f"[BLUETOOTH] Pairing with ELM327 {elm_mac}")
    run(f"echo -e 'pair {elm_mac}\ntrust {elm_mac}\nconnect {elm_mac}\nquit' | bluetoothctl")
    time.sleep(2)

    # 4️⃣ Tworzenie portu RFCOMM
    print("[BLUETOOTH] Binding RFCOMM to /dev/rfcomm0")
    run(f"sudo rfcomm bind 0 {elm_mac} 1")

    print("[BLUETOOTH] Setup complete! /dev/rfcomm0 ready to use.")
