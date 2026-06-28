import struct
import time

import can

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

engine_id = 1
rpm = 6900
temperature = 90

payload = struct.pack('>BHhx', engine_id, rpm, temperature) #>BHhx = big endian, unsigned char (id), unsigned short (Rpm), short (temp), pad byte

try:
    while True:
        msg = can.Message(
            arbitration_id=0x123,
            data=payload,
            is_extended_id = False
        )
        bus.send(msg)
        print("sent")
        time.sleep(1.0)

except KeyboardInterrupt:
    print("Stopped")
    bus.shutdown