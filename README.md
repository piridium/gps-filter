# GPX - Tools

## Installation

```sh
  python3 -m venv venv
  source venv/bin/activate.fish
  pip install -r requirements.txt
```

## GPX Filter

This script filters .gpx files. It removes leading and trailing noise, classifies and skips files with no significant movement (parked) and writes clean files to the output directory.
I use this script together with my custom made gps logger: https://github.com/piridium/gps-logger

### Usage

- Paste all new gpx-files into `gpxFilter/INPUT`.
- Run Script
- Find processed files in `gpxFilter/OUTPUT`.

```sh
  source venv/bin/activate.fish
  cd gpxFilter
  python filter_gpx.py
  # ...
  deactivate
```

## VWsFriendImport

This script generates an sql file from .gpx sources ready for importing into VWsFriend.
- Copy .gpx-Files into `VWsFriendImport/INPUT``
- Determine start mileage for this trip block.
- Run script

```sh
  source venv/bin/activate.fish
  cd VWsFriendImport
  python prepare_import.py
```

- Review `OUTPUT/trackImport.sql`
- Copy `OUTPUT/trackImport.sql` to docker host
- **Make Backup of VWsFriend DB (UI)**
- Import data into postgres

```sh
  docker exec -i vwsfriend-postgresdb psql -U admin -d vwsfriend < trackImport.sql
```
