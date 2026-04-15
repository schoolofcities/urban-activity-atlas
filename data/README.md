Our dataset captures urban activity - measured through mobile data - at the level of depth-6 geohashes. In `metro_region_geohash_stops`, there is a GeoJSON file for each of the approximately 300 metro regions we examined. Each file contains the geometry of all the geohashes (for which data exists) within the respective metro region.

In addition to geometry, each geohash includes two normalized values of urban activity:
 - `prop_total_stops`: Normalized over all stops in the full dataset.
 - `prop_subset_stops` (featured in this project): Normalized over all stops in the specific metro region .

[Click here](https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2Fschoolofcities%2Furban-activity-atlas%2Ftree%2Fadd-map-features%2Fdata%2Fmetro_region_geohash_stops) to download this dataset.

## Export per-metro raw CSVs

If you want one CSV per metro region with normalized stop values, run:

```bash
python analysis/export_metro_csvs.py
```

By default, the script reads GeoJSON files from `data/metro_region_geohash_stops_merged_6cols` and writes CSV files to `data/metro_region_geohash_stops_merged_6cols_csv`.