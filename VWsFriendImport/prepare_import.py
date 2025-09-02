#!/usr/bin/env python3
import gpxpy
import gpxpy.gpx
import os
import glob
import configparser
from datetime import datetime, timezone
import hashlib

# -------------------------
# Config einlesen
# -------------------------
config = configparser.ConfigParser()
config.read("config.ini")

VIN = config.get("vehicle", "vin")
GPX_FOLDER = config.get("paths", "gpx_folder")
OUTPUT_SQL = config.get("paths", "output_sql", fallback="insert_trips.sql")

# START_MILEAGE aus der CLI abfragen
while True:
    try:
        START_MILEAGE = int(input("Please enter the start mileage (km): "))
        break
    except ValueError:
        print("Invalid input, please enter an integer value.")

# -------------------------
# GPX-Dateien einlesen
# -------------------------
gpx_files = glob.glob(os.path.join(GPX_FOLDER, "*.gpx"))

def track_start_time(gpx_file):
    with open(gpx_file, "r") as f:
        gpx = gpxpy.parse(f)
        # erster Trackpunkt
        return gpx.tracks[0].segments[0].points[0].time

# Dateien nach Startzeit sortieren
gpx_files.sort(key=track_start_time)

# -------------------------
# SQL vorbereiten
# -------------------------
sql_statements = ["BEGIN;"]

current_mileage = START_MILEAGE

for gpx_file in gpx_files:
    with open(gpx_file, "r") as f:
        gpx = gpxpy.parse(f)

    track = gpx.tracks[0].segments[0]
    start_point = track.points[0]
    end_point = track.points[-1]

    start_time = start_point.time.replace(tzinfo=timezone.utc)
    end_time = end_point.time.replace(tzinfo=timezone.utc)

    start_lat = start_point.latitude
    start_lon = start_point.longitude
    end_lat = end_point.latitude
    end_lon = end_point.longitude

    # Mileage berechnen
    distance_m = track.length_3d()
    end_mileage = current_mileage + int(distance_m / 1000)  # km

    # Track-Hash als Kommentar
    track_hash = hashlib.md5(open(gpx_file,'rb').read()).hexdigest()

    insert_stmt = f"""-- {os.path.basename(gpx_file)} {track_hash}
INSERT INTO trips (
    vehicle_vin, "startDate", "endDate",
    start_position_latitude, start_position_longitude,
    start_location_id,
    destination_position_latitude, destination_position_longitude,
    destination_location_id,
    start_mileage_km, end_mileage_km
) VALUES (
    '{VIN}',
    '{start_time.isoformat()}',
    '{end_time.isoformat()}',
    {start_lat}, {start_lon},
    NULL,
    {end_lat}, {end_lon},
    NULL,
    {current_mileage}, {end_mileage}
);
"""
    sql_statements.append(insert_stmt)
    current_mileage = end_mileage  # für nächsten Track

sql_statements.append("COMMIT;")

# -------------------------
# SQL-File schreiben
# -------------------------
with open(OUTPUT_SQL, "w") as f:
    f.write("\n".join(sql_statements))

print(f"{len(gpx_files)} tracks verarbeitet. SQL-File: {OUTPUT_SQL}")
