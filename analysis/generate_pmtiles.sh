#!/bin/bash

# metro_region_geohash_stops_change_2019_2020_to_2024_2025
# metro_region_geohash_stops_change_2019_2020_to_2023_2024
# metro_region_geohash_stops_change_2023_2024_to_2024_2025

in_dir="data/metro_region_geohash_stops_change_2023_2024_to_2024_2025"
out_dir="static/metro_region_geohash_stops_change_2023_2024_to_2024_2025_pm/"

# Ensure output folder exists
mkdir -p "$out_dir"

for file in "$in_dir"/*; do
  if [ -f "$file" ]; then
    f_base=$(basename "${file%.*}")
    echo "Converting $f_base..."

    # Original version
    tippecanoe -zg -o "$out_dir"/"$f_base".pmtiles --force --coalesce-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson
    
    # Attempt at fixing the clumping    
    #tippecanoe -zg -o "$out_dir"/"$f_base".pmtiles --force "$in_dir"/"$f_base".geojson
  fi
done
