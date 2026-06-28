import time
import json

import paho.mqtt.client as mqtt

from can_sender import engine_id

# define connection parameters
MQTT_BROKER = ("localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "engine/telemetry"

# Callback when client connects to broker
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connection established ok")
    else:
        print(f"Error code {rc}")

# nitialise client

client = mqtt.Client()
client.on_connect = on_connect

# connect to local broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start background net loop to handle connection lifecycle
client.loop_start()

print("Start MQTT broadcast.")

try:
    while True:
        telemetry_data = {
            "engine_id" : 1,
            "rpm": 6900,
            "temperature": 90.5
        }

        # serialise dictionary to JSON string
        json_payload = json.dumps(telemetry_data);

        # publish payload to MQTT
        client.publish(MQTT_TOPIC, json_payload, qos=1)

        print(f"Published to '{MQTT_TOPIC}':{json_payload}")
        time.sleep(1.0)
except KeyboardInterrupt:
    print("\nDisconnecting from MQTT...")
    client.loop_stop()
    client.disconnect(0)