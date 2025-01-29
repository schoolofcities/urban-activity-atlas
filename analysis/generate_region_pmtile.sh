#!/bin/bash

# Generate PMTiles file from GeoJSON with metro region boundaries

# Input and output file paths
INPUT="data/metro_regions_full.geojson"
OUTPUT="static/metro_regions_full.pmtiles"

# Auto-determine max zoom based on data
# Remove feature and tile size limits
# Name the vector tile layer
tippecanoe \
  -o "${OUTPUT}" \
  -zg \
  --no-feature-limit \
  --no-tile-size-limit \
  --force \
  -l metro_region_full \
  "${INPUT}"