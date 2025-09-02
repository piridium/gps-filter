import gpxpy
import os
from tqdm import tqdm

def rename_gpx_file(file_path, processed_dir):
    # Versuche, die GPX-Datei zu laden
    try:
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)
    except Exception as e:
        print(f"Fehler beim Parsen von {file_path}: {e}")
        return

    # Prüfe, ob Tracks existieren
    if not gpx.tracks or not gpx.tracks[0].segments:
        print(f"Keine Tracks in {file_path}, überspringe")
        return

    # Hole die Startzeit des ersten Punktes für den Dateinamen
    start_time = gpx.tracks[0].segments[0].points[0].time
    if start_time is None:
        print(f"Keine Zeit im ersten Punkt von {file_path}, überspringe")
        return

    filename = start_time.strftime('%Y%m%d_%H%M%S') + '.gpx'
    output_file = os.path.join(processed_dir, filename)

    # Speichere die GPX-Datei unter neuem Namen
    with open(output_file, 'w') as f:
        f.write(gpx.to_xml())

def process_gpx_files(import_dir, processed_dir):
    files = [os.path.join(import_dir, f) for f in os.listdir(import_dir) if f.endswith('.gpx')]

    for file_path in tqdm(files, desc="Umbenennen der GPX-Dateien"):
        rename_gpx_file(file_path, processed_dir)

if __name__ == '__main__':
    import_dir = './INPUT'
    processed_dir = './OUTPUT'

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    process_gpx_files(import_dir, processed_dir)
