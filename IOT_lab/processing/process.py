from influxdb_client import InfluxDBClient
import pandas as pd


# =========================
# INFLUXDB CONFIG
# =========================

TOKEN = "11K60xHoFS6apnLhYGlhROFV5QchxOCfokDTiPx_AHZNBUzvImmOWlZFOWBl1a9H3uEY5NpHWI7KVWMO5w62uQ=="

ORG = "iot"

BUCKET = "sensor"

URL = "http://localhost:8086"


# =========================
# CONNECT INFLUXDB
# =========================

client = InfluxDBClient(
    url=URL,
    token=TOKEN,
    org=ORG
)

query_api = client.query_api()


# =========================
# QUERY DATA
# =========================

query = f'''
from(bucket: "{BUCKET}")
|> range(start: -1h)
|> filter(fn: (r) => r._measurement == "sensor_data")
|> filter(fn: (r) =>
    r._field == "temperature" or
    r._field == "humidity" or
    r._field == "distance_cm" or
    r._field == "rssi"
)
'''


tables = query_api.query(query)


# =========================
# CONVERT DATAFRAME
# =========================

data = []


for table in tables:
    for record in table.records:

        data.append({
            "time": record.get_time(),
            "field": record.get_field(),
            "value": record.get_value()
        })


df = pd.DataFrame(data)


if df.empty:
    print("Khong co du lieu!")
    exit()


# chuyển field thành cột

df = df.pivot_table(
    index="time",
    columns="field",
    values="value",
    aggfunc="first"
)


df = df.reset_index()


print("\n===== DU LIEU TU INFLUXDB =====")
print(df.head())


# =========================
# XU LY DU LIEU THIEU
# =========================

print("\n===== SAU KHI XU LY THIEU =====")

df = df.ffill()

print(df.head())


# =========================
# PHAT HIEN OUTLIER IQR
# =========================

for col in ["temperature", "humidity", "distance_cm"]:

    if col in df.columns:

        Q1 = df[col].quantile(0.25)

        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1


        df = df[
            (df[col] >= Q1 - 1.5*IQR)
            &
            (df[col] <= Q3 + 1.5*IQR)
        ]


print("\n===== SAU KHI LOC OUTLIER =====")
print(df.head())


# =========================
# RESAMPLING
# =========================

df["time"] = pd.to_datetime(df["time"])

df = df.set_index("time")


df_resample = df.resample("1min").mean()


print("\n===== RESAMPLING 1 PHUT =====")
print(df_resample.head())


# =========================
# TAO DAC TRUNG
# =========================

if "temperature" in df_resample.columns:

    df_resample["temperature_rolling"] = (
        df_resample["temperature"]
        .rolling(5)
        .mean()
    )


print("\n===== DU LIEU CUOI =====")

print(df_resample.tail())


# LUU FILE KET QUA

df_resample.to_csv(
    "processed_sensor.csv"
)


print("\nDa luu file processed_sensor.csv")