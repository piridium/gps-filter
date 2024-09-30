# Filter GPX

This script filters .gpx files. It removes leading and trailing noise, classifies and skips files with no significant movement (parked) and writes clean files to the output directory.
I use this script together with my custom made gps logger: https://github.com/piridium/gps-logger

## Installation

```sh
  python3 -m venv venv
  source venv/bin/activate.fish
  pip install gpxpy
  pip install tqdm
```

## Usage

- Paste all new gpx-files into `INPUT`.
- Run Script
- Find processed files in `OUTPUT`.

```sh
  source venv/bin/activate.fish
  python filter_gpx.py
```
