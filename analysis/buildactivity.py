"""
Generate activity CSVs expected by join_metro_geohash.

Current input schema (urbanactivityatlas_2025_2026.csv):
- GEOHASH6
- UNIQUE_STOPS
- TOTAL_STOPS

Current output schema (activity_2025_04_01_2026_03_31.csv):
- geohash6
- total_stops

Legacy FY input/output logic is kept below as commented references.
"""
import pandas as pd

# Current source file and output for FY 2025-2026.
INPUT_CSV = "data/urbanactivityatlas_2025_2026.csv"
OUTPUT_CSV = "activity_2025_04_01_2026_03_31.csv"

# Legacy source and windows (kept for reference):
# LEGACY_INPUT_CSV = "data/urbanactivityatlas_3_13_fy.csv"
# LEGACY_WINDOW_1 = 2019
# LEGACY_WINDOW_2 = 2024


def build_activity_csv(data):
    activity = data[["GEOHASH6", "TOTAL_STOPS"]].rename(
        columns={"GEOHASH6": "geohash6", "TOTAL_STOPS": "total_stops"}
    )
    activity.to_csv(OUTPUT_CSV, index=False)

## Adding metro region to each geohash -> done in join_metro_geohash.ipynb
# def add_metro_col(data, metro_geohash):
#     data = pd.merge()

## Get totals per metro -> -> done in join_metro_geohash.ipynb
# def get_totals_per_metro(data):
#     data.groupby('metro')['TOTALSTOPS']


def __main__():
    data = pd.read_csv(INPUT_CSV)
    build_activity_csv(data)

if __name__ == "__main__":
    __main__()