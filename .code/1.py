import sqlite3
from scapy.all import ARP, Ether, srp
from matrix_client.api import MatrixHttpApi
import time


subnet = "192.168.1.0/24"


homeserver_url = "https://matrix.example.com"
access_token = "YOUR_ACCESS_TOKEN"
room_id = "!your_room_id:example.com"
matrix = MatrixHttpApi(homeserver_url, token=access_token)


conn = sqlite3.connect('devices.db')

def add_device_to_database(device):

    conn.execute("INSERT INTO devices (ip, mac) VALUES (?, ?)", (device['ip'], device['mac']))
    conn.commit()

def device_exists_in_database(device):

    cursor = conn.execute("SELECT COUNT(*) FROM devices WHERE ip = ? AND mac = ?", (device['ip'], device['mac']))
    count = cursor.fetchone()[0]
    return count > 0


conn.execute("CREATE TABLE IF NOT EXISTS devices (ip TEXT, mac TEXT)")

while True:

    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp


    result = srp(packet, timeout=3, verbose=0)[0]


    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})


    for device in devices:

        if not device_exists_in_database(device):

            message = f"New device on the network: IP {device['ip']}, MAC {device['mac']}"
            matrix.send_message(room_id, message)

            add_device_to_database(device)


    time.sleep(180)



conn.close()
