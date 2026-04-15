"""
Build metro_regions_geohash.csv
For each metro in metro_regions_full.geojson, enumerate all geohash-6 cells
that intersect the region boundary (outer cover), then deduplicate each geohash
to a single region by largest intersection area.

Mirrors the logic in join_metro_geohash.ipynb but runs stand-alone.
"""

import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely import geometry
from polygeohasher import polygeohasher
import geohash

GEOHASH_LEVEL = 6
INPUT_FILE  = "./data/metro_regions_full.geojson"
OUTPUT_FILE = "./data/metro_regions_geohash.csv"

# ── 1. Load regions ───────────────────────────────────────────────────────────
print("Loading metro regions …")
gdf = gpd.read_file(INPUT_FILE)
print(f"  {len(gdf)} regions loaded")

# ── 2. Generate geohash cover (outer = includes partially-covered cells) ──────
print(f"\nGenerating geohash-{GEOHASH_LEVEL} covers (inner=False) …")
pgh = polygeohasher.Polygeohasher(gdf)
df_init = pgh.create_geohash_list(GEOHASH_LEVEL, inner=False)
print(f"  {len(df_init)} (region, geohash) pairs before dedup")

# ── 3. Convert geohash strings → geometries ───────────────────────────────────
print("\nConverting geohashes to geometries …")
gdf_geo = pgh.geohashes_to_geometry(df_init, "geohash_list")

# ── 4. Compute intersection area for each (region, geohash) pair ─────────────
print("\nComputing intersection areas (this takes ~30 min) …")
region_geom = gdf.set_index("name")["geometry"]

def intersect_area(row):
    return row["geometry"].intersection(region_geom[row["name"]]).area

tqdm.pandas(desc="  intersection")
gdf_geo["intersect_area"] = gdf_geo.progress_apply(intersect_area, axis=1)

# ── 5. Keep only the best-matching region for each geohash ────────────────────
print("\nDeduplicating geohashes …")
gdf_geo = (
    gdf_geo
    .sort_values("intersect_area", ascending=False)
    .drop_duplicates(subset=["geohash_list"])
    .sort_values(["name", "geohash_list"])
)

# ── 6. Clean up and save ──────────────────────────────────────────────────────
df_out = (
    pd.DataFrame(gdf_geo.drop(columns="geometry"))
    .drop(columns=["intersect_area", "population"], errors="ignore")
    .rename(columns={"geohash_list": "geohash"})
)

df_out.to_csv(OUTPUT_FILE, index=False)
print(f"\nDone! {len(df_out)} rows written to {OUTPUT_FILE}")
print(df_out.head(10).to_string(index=False))
