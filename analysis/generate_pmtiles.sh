#!/bin/bash

in_dir="data/metro_region_geohash_stops"
out_dir="static/metro_region_geohash_stops_pm/"

for file in "$in_dir"/*; do
  if [ -f "$file" ]; then
    f_base=$(basename "${file%.*}")
    echo "Converting $f_base..."

    tippecanoe -zg -o "$out_dir"/"$f_base".pmtiles --coalesce-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson
  fi
done
