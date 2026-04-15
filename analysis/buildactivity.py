"""
Generate activity CSVs for fiscal windows expected by join_metro_geohash.

Input schema (urbanactivityatlas_3_13_fy.csv):
- FISCAL_YEAR (int): fiscal year start year (e.g., 2019 => 2019-04-01 to 2020-03-31)
- GEOHASH_ID
- TOTALSTOPS
- UNIQUESTOPS

Output schema (activity_YYYY-04-01_YYYY+1-03-31.csv):
- geohash6
- total_stops
"""
import pandas as pd

window1 = 2019
window2 = 2024

data_2019 = []
data_2024 = []

def separate_years(data):
    data_2019 = data[data["FISCAL_YEAR"] == window1].copy()
    data_2024 = data[data["FISCAL_YEAR"] == window2].copy()
    
    data_2019 = data_2019[["GEOHASH_ID", "TOTALSTOPS"]].rename(
        columns={"GEOHASH_ID": "geohash6", "TOTALSTOPS": "total_stops"}
    )
    data_2024 = data_2024[["GEOHASH_ID", "TOTALSTOPS"]].rename(
        columns={"GEOHASH_ID": "geohash6", "TOTALSTOPS": "total_stops"}
    )
    
    data_2019.to_csv("activity_2019_04_01_2020_03_31.csv", index=False)
    data_2024.to_csv("activity_2024_04_01_2025_03_31.csv", index=False)
    
    return

## Adding metro region to each geohash -> done in join_metro_geohash.ipynb
# def add_metro_col(data, metro_geohash):
#     data = pd.merge()

## Get totals per metro -> -> done in join_metro_geohash.ipynb
# def get_totals_per_metro(data):
#     data.groupby('metro')['TOTALSTOPS']


def __main__():
    data = pd.read_csv("data/urbanactivityatlas_3_13_fy.csv")
    separate_years(data)

if __name__ == "__main__":
    __main__()