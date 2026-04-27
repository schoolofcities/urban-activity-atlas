"""
Export one raw CSV per metro area from GeoJSON feature collections.

Default behavior:
- Read all .geojson files from data/metro_region_geohash_stops_merged_6cols
- Write one .csv per metro to data/metro_region_geohash_stops_merged_6cols_csv
- Preserve all feature property columns from the source GeoJSON
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


PREFERRED_COLUMN_ORDER = [
    "geohash",
    "UNIQUE_STOPS",
    "prop_total_stops",
    "prop_subset_stops",
    "prop_subset_stops_2019_2020",
    "prop_subset_stops_2023_2024",
    "prop_subset_stops_2024_2025",
    "prop_subset_stops_change_2019_2020_to_2023_2024",
    "prop_subset_stops_change_2019_2020_to_2024_2025",
    "prop_subset_stops_change_2023_2024_to_2024_2025",
]


def get_columns(features: list[dict]) -> list[str]:
    keys = set()
    for feature in features:
        properties = feature.get("properties") or {}
        keys.update(properties.keys())

    ordered = [key for key in PREFERRED_COLUMN_ORDER if key in keys]
    remaining = sorted([key for key in keys if key not in set(ordered)])
    return ordered + remaining


def _sanitize_geojson_text(raw_text: str) -> str:
    # Some generated GeoJSON files may contain non-standard tokens or trailing commas.
    sanitized = raw_text
    sanitized = re.sub(r"\b(?:NaN|nan|Infinity|inf|-Infinity|-inf)\b", "null", sanitized)
    sanitized = re.sub(r",(?=\s*[}\]])", "", sanitized)
    return sanitized


def _has_balanced_braces(text: str) -> bool:
    in_string = False
    escape = False
    brace_depth = 0

    for ch in text:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1

    return brace_depth == 0 and not in_string and not escape


def _repair_truncated_feature_collection(raw_text: str) -> str:
    # If the file was cut mid-feature, remove the trailing incomplete feature
    # and close the features array/root object.
    feature_start_marker = '\n    {\n      "type": "Feature"'
    last_feature_start = raw_text.rfind(feature_start_marker)
    if last_feature_start == -1:
        return raw_text

    last_feature_text = raw_text[last_feature_start:]
    if _has_balanced_braces(last_feature_text):
        return raw_text

    repaired_prefix = raw_text[:last_feature_start].rstrip()
    if repaired_prefix.endswith(","):
        repaired_prefix = repaired_prefix[:-1].rstrip()

    return repaired_prefix + "\n  ]\n}\n"


def load_geojson(geojson_path: Path) -> tuple[dict, bool]:
    try:
        with geojson_path.open("r", encoding="utf-8") as infile:
            return json.load(infile), False
    except json.JSONDecodeError:
        with geojson_path.open("r", encoding="utf-8") as infile:
            raw_text = infile.read()

        sanitized_text = _sanitize_geojson_text(raw_text)
        try:
            return json.loads(sanitized_text), True
        except json.JSONDecodeError:
            repaired_text = _repair_truncated_feature_collection(sanitized_text)
            return json.loads(repaired_text), True


def export_geojson_to_csv(geojson_path: Path, output_dir: Path) -> tuple[int, str]:
    data, used_sanitizer = load_geojson(geojson_path)

    features = data.get("features") or []
    columns = get_columns(features)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{geojson_path.stem}.csv"

    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for feature in features:
            row = feature.get("properties") or {}
            writer.writerow({column: row.get(column, "") for column in columns})

    if used_sanitizer:
        print(f"Warning: used sanitized JSON parsing for {geojson_path.name}")

    return len(features), output_path.name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export one raw CSV per metro from merged GeoJSON files."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/metro_region_geohash_stops_merged_6cols"),
        help="Directory containing per-metro .geojson files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/metro_region_geohash_stops_merged_6cols_csv"),
        help="Directory where per-metro .csv files will be written.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {args.input_dir}")

    geojson_files = sorted(args.input_dir.glob("*.geojson"))
    if not geojson_files:
        raise FileNotFoundError(f"No .geojson files found in: {args.input_dir}")

    total_rows = 0
    total_files = 0
    failed_files: list[tuple[str, str]] = []

    for geojson_file in geojson_files:
        try:
            row_count, output_name = export_geojson_to_csv(geojson_file, args.output_dir)
            print(f"Wrote {output_name} ({row_count} rows)")
            total_rows += row_count
            total_files += 1
        except Exception as exc:  # noqa: BLE001
            failed_files.append((geojson_file.name, str(exc)))
            print(f"Error: failed to export {geojson_file.name}: {exc}")

    print(f"Done. Exported {total_files} CSV files with {total_rows} rows total.")

    if failed_files:
        print(f"Skipped {len(failed_files)} files due to parsing errors:")
        for file_name, reason in failed_files:
            print(f"- {file_name}: {reason}")


if __name__ == "__main__":
    main()
