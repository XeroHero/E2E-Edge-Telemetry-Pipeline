import json

import can
import struct
import paho.mqtt.client as mqtt


# --- CONFIGURATION ---
CAN_CHANNEL = 'vcan0'
CAN_INTERFACE = 'socketcan'
TARGET_ARB_ID =0x123

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "engine/telemetry"

# Byte Unpacking Format: > (Big-Endian), B (1B ID), H (2B RPM), h (2B Temp), x (1B Pad)

DATA_FMT = '<BHhx'

def on_connect(client, userdata, flags, reason_code,properties=None):
    if reason_code==0:
        print(f" [MMQTT] Connection established successfully")
    else:
        print(f' [MQTT] Connection error: {reason_code}')

# initialise MQTT usign protocol v2
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect

print(f' [MQTT] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...')
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# --- CAN Bus Config & Main loop ---
print(f"Connecting to CAN Interface '{CAN_INTERFACE} on {CAN_CHANNEL}")
can_bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)

print(f"SUCCESS: CAN Interface fully functional!")

try:
    for msg in can_bus:
        if msg.arbitration_id == TARGET_ARB_ID:
            try:
                # 1. Unpack the raw binary payload from the CAN frame
                engine_id, rpm, temperature = struct.unpack(DATA_FMT, msg.data)

                # 2. Structure into a clean Python dictionary
                telemetry_payload = {
                    "engine_id": engine_id,
                    "rpm": rpm,
                    "temperature": temperature,
                    "timestamp": msg.timestamp # Capture CAN packet arrival time
                }

                # 3. Convert dictionary to serialized JSON string
                json_data = json.dumps(telemetry_payload)

                mqtt_client.publish(MQTT_TOPIC, json_data, qos=1)

                print(f" [BRIDGE] Ingested CAN 0x123 -> Streamed JSON to '{MQTT_TOPIC}'")
            except struct.error as e:
                print(f" [ERROR] Payload unpacking failed: {e}")

except KeyboardInterrupt:
    print(f"\nHalting Edge GW...")

finally:
    # Resource cleanup
    can_bus.shutdown()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print(f"Shutdown complete!")
