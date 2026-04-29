"""
Merge a newly generated yearly metro GeoJSON folder into the existing merged per-metro folder.

Typical use in this repo:
- Base input:  data/metro_region_geohash_stops_merged_6cols
- New year:    data/metro_region_geohash_stops_2025_2026
- Output:      data/metro_region_geohash_stops_merged_10cols

What this script adds per feature (by geohash):
- prop_subset_stops_<new_year_label>
- prop_subset_stops_change_<prior_label>_to_<new_year_label> (for each prior label)

It also updates:
- prop_subset_stops := latest year's value

This lets the frontend use the new year as the default single-period metric while
keeping historical fields and prior change fields intact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_geojson(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_geojson(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def build_feature_map(features: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for feature in features:
        props = feature.get("properties", {})
        geohash = props.get("geohash")
        if geohash:
            out[str(geohash)] = feature
    return out


def to_float_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def merge_metro_file(
    base_file: Path,
    latest_file: Path,
    output_file: Path,
    new_year_label: str,
    prior_labels: list[str],
) -> tuple[int, int]:
    base_fc = load_geojson(base_file)
    latest_fc = load_geojson(latest_file)

    base_features = base_fc.get("features", [])
    latest_by_geohash = build_feature_map(latest_fc.get("features", []))

    latest_col = f"prop_subset_stops_{new_year_label}"

    updated = 0
    missing_latest = 0

    for feature in base_features:
        props = feature.setdefault("properties", {})
        geohash = str(props.get("geohash", "")).strip()
        if not geohash:
            continue

        latest_feature = latest_by_geohash.get(geohash)
        latest_props = latest_feature.get("properties", {}) if latest_feature else {}
        latest_value = to_float_or_none(latest_props.get("prop_subset_stops"))

        props[latest_col] = latest_value
        if latest_value is None:
            missing_latest += 1
        else:
            updated += 1

        # Make latest year the generic single-period key used by map fallback.
        props["prop_subset_stops"] = latest_value

        # Add new change columns vs each requested prior year.
        for prior in prior_labels:
            prior_col = f"prop_subset_stops_{prior}"
            change_col = f"prop_subset_stops_change_{prior}_to_{new_year_label}"

            prior_value = to_float_or_none(props.get(prior_col))
            if prior_value is None or latest_value is None:
                props[change_col] = None
            else:
                props[change_col] = latest_value - prior_value

    out_fc = {
        "type": base_fc.get("type", "FeatureCollection"),
        "name": base_fc.get("name", base_file.stem),
        "features": base_features,
    }
    write_geojson(output_file, out_fc)
    return updated, missing_latest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a new year into existing merged per-metro GeoJSON files."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/metro_region_geohash_stops_merged_6cols"),
        help="Directory containing existing merged metro GeoJSON files.",
    )
    parser.add_argument(
        "--latest-dir",
        type=Path,
        default=Path("data/metro_region_geohash_stops_2025_2026"),
        help="Directory containing newly generated per-metro GeoJSON for the latest year.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/metro_region_geohash_stops_merged_10cols"),
        help="Directory to write merged output files.",
    )
    parser.add_argument(
        "--new-year-label",
        default="2025_2026",
        help="Suffix label for latest year column, e.g. 2025_2026.",
    )
    parser.add_argument(
        "--prior-labels",
        nargs="+",
        default=["2019_2020", "2024_2025", "2025_2026"],
        help="Prior year labels used to create change columns.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.base_dir.exists():
        raise FileNotFoundError(f"Base directory does not exist: {args.base_dir}")
    if not args.latest_dir.exists():
        raise FileNotFoundError(f"Latest year directory does not exist: {args.latest_dir}")

    base_files = sorted(args.base_dir.glob("*.geojson"))
    if not base_files:
        raise FileNotFoundError(f"No .geojson files found in base directory: {args.base_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_updated = 0
    total_missing = 0
    skipped_missing_latest_file = 0

    for base_file in base_files:
        latest_file = args.latest_dir / base_file.name
        if not latest_file.exists():
            skipped_missing_latest_file += 1
            continue

        output_file = args.output_dir / base_file.name
        updated, missing = merge_metro_file(
            base_file=base_file,
            latest_file=latest_file,
            output_file=output_file,
            new_year_label=args.new_year_label,
            prior_labels=args.prior_labels,
        )

        total_files += 1
        total_updated += updated
        total_missing += missing

    print(f"Wrote {total_files} merged files to {args.output_dir}")
    print(f"Updated geohashes with latest values: {total_updated}")
    print(f"Geohashes missing latest values (set to null): {total_missing}")
    print(f"Skipped metros missing latest file: {skipped_missing_latest_file}")


if __name__ == "__main__":
    main()
