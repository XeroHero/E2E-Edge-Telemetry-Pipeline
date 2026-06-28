import can

bus = can.interface.Bus(channel='vcan0', interface='socketcan')
print("Listening...")

try:
    for msg in bus:
        print("Received fame -> ArbOD: {hex{msg.arbitration_id} | DLC: {msg.dlc} | Data:{msg.data.hex().upper()}")

except KeyboardInterrupt:
    print("Stopped")
    bus.shutdown();