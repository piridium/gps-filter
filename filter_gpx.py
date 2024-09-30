import gpxpy
import gpxpy.gpx
import os
from datetime import datetime
from tqdm import tqdm  # Für die Fortschrittsanzeige

# Geschwindigkeit in km/h
SPEED_THRESHOLD = 3

# Zähler für die Statistik
stats = {
    "total_files": 0,
    "invalid_files": 0,
    "parse_errors": 0,
    "invalid_tracks": 0,
    "parked_tracks": 0,
    "processed_tracks": 0
}

def get_speed(point1, point2):
    """Berechnet die Geschwindigkeit zwischen zwei GPX-Punkten in km/h"""
    if point1.time and point2.time:
        distance = point1.distance_2d(point2) / 1000  # in km
        time_diff = (point2.time - point1.time).total_seconds() / 3600  # in Stunden
        if time_diff > 0:
            return distance / time_diff
    return 0

def filter_gpx_file(file_path, processed_dir):
    global stats
    # Zähle die Dateien
    stats["total_files"] += 1

    # Prüfe, ob die Datei leer ist
    if os.stat(file_path).st_size == 0:
        stats["invalid_files"] += 1
        return

    # Versuche, die GPX-Datei zu laden
    try:
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)
    except gpxpy.gpx.GPXException as e:
        stats["parse_errors"] += 1
        return

    # Prüfe, ob die Datei überhaupt Tracks enthält
    if not gpx.tracks:
        stats["invalid_files"] += 1
        return

    for track in gpx.tracks:
        for segment in track.segments:
            # Entferne Punkte am Anfang
            while len(segment.points) > 1 and get_speed(segment.points[0], segment.points[1]) < SPEED_THRESHOLD:
                segment.points.pop(0)

            # Entferne Punkte am Ende
            while len(segment.points) > 1 and get_speed(segment.points[-2], segment.points[-1]) < SPEED_THRESHOLD:
                segment.points.pop()

            # Überprüfe, ob der Track parkiert ist (d.h. die Geschwindigkeit ist nie über dem Schwellenwert)
            if all(get_speed(segment.points[i], segment.points[i + 1]) < SPEED_THRESHOLD for i in range(len(segment.points) - 1)):
                stats["parked_tracks"] += 1
                return

    # Lösche leere Tracks
    gpx.tracks = [track for track in gpx.tracks if len(track.segments[0].points) > 0]

    # Wenn kein Track übrig ist oder nur 1 Punkt übrig bleibt, überspringe die Datei
    if not gpx.tracks or len(gpx.tracks[0].segments[0].points) <= 1:
        stats["invalid_tracks"] += 1
        return

    # Hole die Startzeit des gefilterten Tracks für den Dateinamen
    start_time = gpx.tracks[0].segments[0].points[0].time
    filename = start_time.strftime('%Y%m%d_%H%M%S') + '.gpx'

    # Speichere die bearbeitete GPX-Datei
    output_file = os.path.join(processed_dir, filename)
    with open(output_file, 'w') as f:
        f.write(gpx.to_xml())

    stats["processed_tracks"] += 1

def process_gpx_files(import_dir, processed_dir):
    files = []
    for root, _, file_list in os.walk(import_dir):
        for filename in file_list:
            if filename.endswith('.gpx'):
                files.append(os.path.join(root, filename))

    # Benutze tqdm für die Fortschrittsanzeige
    for file_path in tqdm(files, desc="Verarbeite GPX-Dateien", unit="Datei"):
        filter_gpx_file(file_path, processed_dir)

def print_statistics():
    print("\n🔍 **Statistik der Verarbeitung** 🔍")
    print(f"📂 Gesamtzahl der Input-Dateien: {stats['total_files']}")
    print(f"🟡 Ungültige/leere Dateien: {stats['invalid_files']}")
    print(f"🔴 Fehler beim Parsen: {stats['parse_errors']}")
    print(f"⚠️ Ungültige/leere Tracks: {stats['invalid_tracks']}")
    print(f"🚗 Parkiert (Auto wurde nicht bewegt): {stats['parked_tracks']}")
    print(f"🟢 Erfolgreich verarbeitete Tracks: {stats['processed_tracks']}")

if __name__ == '__main__':
    import_dir = './IMPORT'  # Verzeichnis mit den unprocessed GPX-Dateien
    processed_dir = './processed'  # Zielverzeichnis für gefilterte GPX-Dateien

    # Stelle sicher, dass das processed-Verzeichnis existiert
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    process_gpx_files(import_dir, processed_dir)

    # Am Ende die Statistik ausgeben
    print_statistics()
