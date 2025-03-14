"""Configuration file for Rain on Snow Climatology Paper"""

from pathlib import Path


# Path to database
DATABASE_PATH = Path.home() / "Data/AROSS/database/observations/surface/version_2.0.0"
STATION_METADATA = DATABASE_PATH / "metadata" / "aross.asos_stations.metadata.csv"
