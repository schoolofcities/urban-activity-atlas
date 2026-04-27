"""
Build merged per-metro GeoJSON from scratch using raw yearly folders.

Reads from:
  - data/metro_region_geohash_stops_2019_2020
  - data/metro_region_geohash_stops_2024_2025
  - data/metro_region_geohash_stops_2025_2026

Outputs to:
  - data/metro_region_geohash_stops_merged_10cols
"""

from __future__ import annotations
import json
from pathlib import Path
from itertools import combinations

# ── Config ────────────────────────────────────────────────────────────────────

YEAR_LABELS = ["2019_2020", "2024_2025", "2025_2026"]
LATEST_LABEL = "2025_2026"

DATA_DIR = Path("data")
YEAR_DIRS = {label: DATA_DIR / f"metro_region_geohash_stops_{label}" for label in YEAR_LABELS}
OUTPUT_DIR = DATA_DIR / "metro_region_geohash_stops_merged_9cols_v2"

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_geojson(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        raise ValueError(f"Empty file: {path}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Bad JSON in {path}: {e}") from e


def write_geojson(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_geohash_map(fc: dict) -> dict[str, dict]:
    return {
        str(f["properties"]["geohash"]): f["properties"]
        for f in fc.get("features", [])
        if f.get("properties", {}).get("geohash")
    }

# ── Core merge ────────────────────────────────────────────────────────────────

def merge_metro(metro_filename: str) -> tuple[int, int]:
    """
    For one metro file, read each year folder and build a merged FeatureCollection.
    Returns (features_written, files_missing).
    """
    # Load all available year data for this metro
    year_maps: dict[str, dict[str, dict]] = {}   # label -> {geohash -> props}
    reference_fc = None

    for label in YEAR_LABELS:
        path = YEAR_DIRS[label] / metro_filename
        if not path.exists():
            print(f"  [SKIP] {label}: {metro_filename} not found")
            continue
        try:
            fc = load_geojson(path)
        except ValueError as e:
            print(f"  [ERROR] {e}")
            continue
        year_maps[label] = build_geohash_map(fc)
        if reference_fc is None:
            reference_fc = fc   # use first available as geometry source

    if reference_fc is None:
        print(f"  [SKIP] No valid files found for {metro_filename}")
        return 0, len(YEAR_LABELS)

    # Use the latest available year as geometry source if possible
    if LATEST_LABEL in year_maps:
        reference_fc = load_geojson(YEAR_DIRS[LATEST_LABEL] / metro_filename)

    # Collect all geohashes across all years
    all_geohashes: set[str] = set()
    for m in year_maps.values():
        all_geohashes.update(m.keys())

    # Build geometry lookup from reference FC
    geom_by_geohash: dict[str, dict] = {
        str(f["properties"]["geohash"]): f["geometry"]
        for f in reference_fc.get("features", [])
        if f.get("properties", {}).get("geohash")
    }

    output_features = []
    for geohash in sorted(all_geohashes):
        # Base properties
        props: dict = {"geohash": geohash}

        # Add per-year normalized values
        for label in YEAR_LABELS:
            val = to_float(year_maps.get(label, {}).get(geohash, {}).get("prop_subset_stops"))
            props[f"prop_subset_stops_{label}"] = val

        # Latest value as the generic fallback key
        props["prop_subset_stops"] = to_float(
            year_maps.get(LATEST_LABEL, {}).get(geohash, {}).get("prop_subset_stops")
        )

        # Change columns: all ordered pairs of (earlier, later)
        for earlier, later in combinations(YEAR_LABELS, 2):
            col = f"prop_subset_stops_change_{earlier}_to_{later}"
            v_early = props.get(f"prop_subset_stops_{earlier}")
            v_late  = props.get(f"prop_subset_stops_{later}")
            props[col] = (v_late - v_early) if (v_early is not None and v_late is not None) else None

        # Copy any extra base props from latest year (e.g. metro, region names)
        extra_props = year_maps.get(LATEST_LABEL, {}).get(geohash, {})
        for k, v in extra_props.items():
            if k not in props:
                props[k] = v

        geometry = geom_by_geohash.get(geohash)
        output_features.append({"type": "Feature", "geometry": geometry, "properties": props})

    out_fc = {
        "type": "FeatureCollection",
        "name": Path(metro_filename).stem,
        "features": output_features,
    }
    output_path = OUTPUT_DIR / metro_filename
    write_geojson(output_path, out_fc)
    return len(output_features), 0

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all metro filenames across all year folders
    all_metro_files: set[str] = set()
    for label in YEAR_LABELS:
        d = YEAR_DIRS[label]
        if d.exists():
            all_metro_files.update(p.name for p in d.glob("*.geojson"))

    if not all_metro_files:
        raise FileNotFoundError("No .geojson files found in any year directory.")

    print(f"Found {len(all_metro_files)} metro files. Building merged output...\n")

    total_features = 0
    total_files = 0

    for metro_filename in sorted(all_metro_files):
        features_written, _ = merge_metro(metro_filename)
        if features_written > 0:
            total_files += 1
            total_features += features_written

    print(f"\nDone. Wrote {total_files} metro files with {total_features} total features.")
    print(f"Output → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()