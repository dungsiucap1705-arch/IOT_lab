import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point


# TOKEN lấy từ InfluxDB
TOKEN = "11K60xHoFS6apnLhYGlhROFV5QchxOCfokDTiPx_AHZNBUzvImmOWlZFOWBl1a9H3uEY5NpHWI7KVWMO5w62uQ=="

ORG = "iot"
BUCKET = "sensor"

# Kết nối InfluxDB
influx = InfluxDBClient(
    url="http://localhost:8086",
    token=TOKEN,
    org=ORG
)

write_api = influx.write_api()


def on_message(client, userdata, msg):

    data = json.loads(msg.payload.decode())

    print("Nhan duoc:")
    print(data)


    point = Point("sensor_data") \
        .tag("device", "ESP32") \
        .field("temperature", data["temperature"]) \
        .field("humidity", data["humidity"]) \
        .field("distance_cm", data["distance_cm"]) \
        .field("rssi", data["rssi"])


    write_api.write(
        bucket=BUCKET,
        org=ORG,
        record=point
    )

    print("Da luu InfluxDB\n")



client = mqtt.Client()

client.connect(
    "localhost",
    1883
)

client.subscribe(
    "iot/sensor"
)

client.on_message = on_message


print("Dang cho du lieu MQTT...")

client.loop_forever()