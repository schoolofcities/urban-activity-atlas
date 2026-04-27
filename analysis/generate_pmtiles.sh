#!/bin/bash

in_dir="data/metro_region_geohash_stops_merged_9cols_v2"
out_dir="static/metro_region_geohash_stops_merged_pm_v9_2/"

# Ensure output folder exists
mkdir -p "$out_dir"

for file in "$in_dir"/*; do
  if [ -f "$file" ]; then
    f_base=$(basename "${file%.*}")
    echo "Converting $f_base..."

    # This one works
    #tippecanoe -Z8 -z14 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --no-simplification-of-shared-nodes --drop-fraction-as-needed --no-feature-limit --no-tile-size-limit "$in_dir"/"$f_base".geojson

    #tippecanoe -Z8 -z14 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --drop-fraction-as-needed --drop-densest-as-needed --coalesce-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson
    #tippecanoe -Z8 -z14 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --no-simplification-of-shared-nodes --drop-fraction-as-needed --drop-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson
    
    # 4/10
    #tippecanoe -Z8 -z13 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --no-simplification-of-shared-nodes --drop-fraction-as-needed --drop-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson

    # attempt 4/13
    #tippecanoe -Z10 -z13 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --no-simplification-of-shared-nodes --no-feature-limit --no-tile-size-limit "$in_dir"/"$f_base".geojson
    tippecanoe -Z8 -z13 -o "$out_dir"/"$f_base".pmtiles --force --detect-shared-borders --no-simplification-of-shared-nodes --no-feature-limit --no-tile-size-limit "$in_dir"/"$f_base".geojson

    # Attempts at fixing the clumping    
    #tippecanoe -zg -o "$out_dir"/"$f_base".pmtiles --force "$in_dir"/"$f_base".geojson
    # Original version
    #tippecanoe -zg -o "$out_dir"/"$f_base".pmtiles --force --coalesce-densest-as-needed --extend-zooms-if-still-dropping "$in_dir"/"$f_base".geojson
    #tippecanoe -Z8 -z14 -o "$out_dir"/"$f_base".pmtiles --force --drop-densest-as-needed --extend-zooms-if-still-dropping --no-simplification-of-shared-nodes "$in_dir"/"$f_base".geojson

  fi
done
