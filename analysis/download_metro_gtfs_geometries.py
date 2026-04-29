"""
Download GTFS feeds for one or more metros from static/GTFSUS.json and
export merged transit route geometries per metro as GeoJSON.

Pipeline:
1) Read Socrata-style GTFSUS.json and map column positions dynamically
2) Match rows to target metro names
3) Download GTFS zip(s) from weblink field
4) Parse shapes.txt + trips.txt + routes.txt
5) Export one merged GeoJSON file per metro

Examples
--------
Download for one metro:
python analysis/download_metro_gtfs_geometries.py --metro "San Francisco-Oakland-Berkeley, CA"

Download for multiple metros:
python analysis/download_metro_gtfs_geometries.py --metro "Seattle-Tacoma-Bellevue, WA" --metro "Boston-Cambridge-Newton, MA-NH"

Dry-run only (no downloads):
python analysis/download_metro_gtfs_geometries.py --metro "Chicago-Naperville-Elgin, IL-IN-WI" --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

GTFS_REGISTRY_PATH = Path("static/GTFSUS.json")
METRO_GEOJSON_PATH = Path("data/metro_regions_full_no_oregon.geojson")
OUTPUT_ROOT = Path("data/transit")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "metro"


def norm_text(value: str) -> str:
    s = (value or "").strip().lower()
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" -- ", "-")
    s = s.replace("--", "-")
    return s


def gtfs_route_type_label(route_type: str) -> str:
    mapping = {
        "0": "tram",
        "1": "subway",
        "2": "rail",
        "3": "bus",
        "4": "ferry",
        "5": "cable_tram",
        "6": "aerial_lift",
        "7": "funicular",
        "11": "trolleybus",
        "12": "monorail",
    }
    return mapping.get(str(route_type), "other")


def load_metro_lookup(path: Path) -> Dict[str, Dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    lookup: Dict[str, Dict] = {}

    for feature in payload.get("features", []):
        name = feature.get("properties", {}).get("name")
        if not name:
            continue
        lookup[norm_text(name)] = feature

    return lookup


def compute_feature_bbox(feature: Dict) -> Optional[Tuple[float, float, float, float]]:
    min_lon, min_lat = float("inf"), float("inf")
    max_lon, max_lat = float("-inf"), float("-inf")

    def walk(coords):
        nonlocal min_lon, min_lat, max_lon, max_lat
        if not isinstance(coords, list) or not coords:
            return
        if isinstance(coords[0], (int, float)) and len(coords) >= 2:
            lon, lat = float(coords[0]), float(coords[1])
            min_lon = min(min_lon, lon)
            min_lat = min(min_lat, lat)
            max_lon = max(max_lon, lon)
            max_lat = max(max_lat, lat)
            return
        for part in coords:
            walk(part)

    walk((feature.get("geometry") or {}).get("coordinates"))

    if min_lon == float("inf"):
        return None
    return min_lon, min_lat, max_lon, max_lat


def point_in_bbox(lon: float, lat: float, bbox: Tuple[float, float, float, float]) -> bool:
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def line_intersects_bbox(coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]) -> bool:
    return any(point_in_bbox(lon, lat, bbox) for lon, lat in coords)


def read_gtfs_registry(path: Path) -> Tuple[List[str], List[List]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    columns = payload["meta"]["view"]["columns"]
    data_rows = payload.get("data", [])
    field_names = [c.get("fieldName", "") for c in columns]
    return field_names, data_rows


def build_row_dict(field_names: List[str], row: List) -> Dict[str, object]:
    mapped = {}
    for i, key in enumerate(field_names):
        if not key:
            continue
        mapped[key] = row[i] if i < len(row) else None

    if not mapped.get("urbanized_area_name") and mapped.get("uza_name"):
        mapped["urbanized_area_name"] = mapped["uza_name"]
    if not mapped.get("uza_name") and mapped.get("urbanized_area_name"):
        mapped["uza_name"] = mapped["urbanized_area_name"]

    return mapped


def extract_weblink(value: object) -> Optional[str]:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, str):
            return first.strip() or None
    return None


def metro_matches_row(target_metro: str, row_metro: str) -> bool:
    # Primary exact-ish normalized match
    if norm_text(target_metro) == norm_text(row_metro):
        return True

    # Fall back to city/state overlap if exact label differs
    # Example target: "Seattle-Tacoma-Bellevue, WA"
    try:
        target_city_part, target_state_part = target_metro.split(",", 1)
        row_city_part, row_state_part = row_metro.split(",", 1)
    except ValueError:
        return False

    target_states = {s.strip() for s in target_state_part.split("-") if s.strip()}
    row_states = {s.strip() for s in row_state_part.split("-") if s.strip()}

    if target_states.isdisjoint(row_states):
        return False

    target_cities = {c.strip().lower() for c in target_city_part.split("-") if c.strip()}
    row_cities = {c.strip().lower() for c in row_city_part.split("-") if c.strip()}

    return len(target_cities.intersection(row_cities)) > 0


def discover_feed_rows_for_metro(rows: List[Dict[str, object]], metro_name: str) -> List[Dict[str, object]]:
    out = []
    for row in rows:
        row_metro = str(row.get("urbanized_area_name") or row.get("uza_name") or "").strip()
        if not row_metro:
            continue

        if not metro_matches_row(metro_name, row_metro):
            continue

        weblink = extract_weblink(row.get("weblink"))
        if not weblink:
            continue

        out.append(row)

    # De-duplicate by URL (many mode-specific rows share the same feed)
    seen = set()
    unique = []
    for row in out:
        url = extract_weblink(row.get("weblink"))
        if url in seen:
            continue
        seen.add(url)
        unique.append(row)

    return unique


def download_file(url: str, out_path: Path, timeout: int = 180) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")

    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    out_path.write_bytes(data)


def read_csv_from_zip(zf: zipfile.ZipFile, filename: str) -> Optional[List[Dict[str, str]]]:
    target = None
    lower_name = filename.lower()

    for name in zf.namelist():
        if name.lower().endswith(lower_name):
            target = name
            break

    if not target:
        return None

    with zf.open(target) as f:
        raw = f.read().decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(raw.splitlines())
    return list(reader)


def build_shape_points(shapes_rows: List[Dict[str, str]]) -> Dict[str, List[Tuple[float, float]]]:
    by_shape: Dict[str, List[Tuple[float, float, float]]] = defaultdict(list)

    for row in shapes_rows:
        shape_id = (row.get("shape_id") or "").strip()
        lat = row.get("shape_pt_lat")
        lon = row.get("shape_pt_lon")
        seq = row.get("shape_pt_sequence")

        if not shape_id or lat is None or lon is None:
            continue

        try:
            lat_f = float(lat)
            lon_f = float(lon)
            seq_f = float(seq) if seq is not None and str(seq).strip() else 0.0
        except ValueError:
            continue

        by_shape[shape_id].append((seq_f, lon_f, lat_f))

    out: Dict[str, List[Tuple[float, float]]] = {}
    for shape_id, pts in by_shape.items():
        pts_sorted = sorted(pts, key=lambda x: x[0])
        coords = [(lon, lat) for _, lon, lat in pts_sorted]
        if len(coords) >= 2:
            out[shape_id] = coords

    return out


def build_route_lookup(routes_rows: Optional[List[Dict[str, str]]]) -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    if not routes_rows:
        return lookup

    for row in routes_rows:
        route_id = (row.get("route_id") or "").strip()
        if not route_id:
            continue
        lookup[route_id] = row

    return lookup


def build_shape_to_route(trips_rows: Optional[List[Dict[str, str]]]) -> Dict[str, str]:
    if not trips_rows:
        return {}

    shape_to_routes: Dict[str, List[str]] = defaultdict(list)
    for row in trips_rows:
        shape_id = (row.get("shape_id") or "").strip()
        route_id = (row.get("route_id") or "").strip()
        if shape_id and route_id:
            shape_to_routes[shape_id].append(route_id)

    resolved: Dict[str, str] = {}
    for shape_id, route_ids in shape_to_routes.items():
        resolved[shape_id] = Counter(route_ids).most_common(1)[0][0]

    return resolved


def features_from_gtfs_zip(
    zip_path: Path,
    metro_name: str,
    metro_bbox: Tuple[float, float, float, float],
    feed_url: str,
    agency_name: str,
    ntd_id: str,
) -> List[Dict]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        shapes_rows = read_csv_from_zip(zf, "shapes.txt")
        trips_rows = read_csv_from_zip(zf, "trips.txt")
        routes_rows = read_csv_from_zip(zf, "routes.txt")

    if not shapes_rows:
        return []

    shape_points = build_shape_points(shapes_rows)
    route_lookup = build_route_lookup(routes_rows)
    shape_to_route = build_shape_to_route(trips_rows)

    features: List[Dict] = []
    for shape_id, coords in shape_points.items():
        if not line_intersects_bbox(coords, metro_bbox):
            continue

        route_id = shape_to_route.get(shape_id, "")
        route = route_lookup.get(route_id, {})

        route_type = str(route.get("route_type", ""))
        mode_label = gtfs_route_type_label(route_type)
        route_color = (route.get("route_color") or "").strip()
        if route_color and not route_color.startswith("#"):
            route_color = f"#{route_color}"

        properties = {
            "metro": metro_name,
            "feed_url": feed_url,
            "agency_name": agency_name,
            "ntd_id": ntd_id,
            "shape_id": shape_id,
            "route_id": route_id,
            "route_type": route_type,
            "mode_label": mode_label,
            "route_short_name": (route.get("route_short_name") or "").strip(),
            "route_long_name": (route.get("route_long_name") or "").strip(),
            "route_color": route_color,
        }

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lon, lat in coords],
                },
                "properties": properties,
            }
        )

    return features


def write_geojson(features: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"type": "FeatureCollection", "features": features}
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_manifest(rows: List[Dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ntd_id",
        "agency_name",
        "city",
        "state",
        "urbanized_area_name",
        "weblink",
        "new_date_validated",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "ntd_id": row.get("ntd_id", ""),
                    "agency_name": row.get("agency_name", ""),
                    "city": row.get("city", ""),
                    "state": row.get("state", ""),
                    "urbanized_area_name": row.get("urbanized_area_name", row.get("uza_name", "")),
                    "weblink": extract_weblink(row.get("weblink")) or "",
                    "new_date_validated": row.get("new_date_validated", ""),
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download GTFS and export per-metro geometries.")
    parser.add_argument("--metro", action="append", help="Exact metro name; repeat for multiple metros.")
    parser.add_argument("--all-metros", action="store_true", help="Process all metros in boundary GeoJSON.")
    parser.add_argument("--registry", default=str(GTFS_REGISTRY_PATH), help="Path to GTFSUS.json")
    parser.add_argument("--metro-geojson", default=str(METRO_GEOJSON_PATH), help="Path to metro regions GeoJSON")
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT), help="Output root directory")
    parser.add_argument("--max-feeds-per-metro", type=int, default=80, help="Max feed URLs per metro")
    parser.add_argument("--download-retries", type=int, default=2, help="Retries per feed download")
    parser.add_argument("--dry-run", action="store_true", help="Do not download; just print matches")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    metro_lookup = load_metro_lookup(Path(args.metro_geojson))

    if args.all_metros:
        target_metros = sorted(feature.get("properties", {}).get("name", "") for feature in metro_lookup.values())
    else:
        target_metros = args.metro or []

    if not target_metros:
        print("Provide --metro (repeatable) or use --all-metros")
        return 2

    field_names, raw_rows = read_gtfs_registry(Path(args.registry))
    rows = [build_row_dict(field_names, r) for r in raw_rows]

    output_root = Path(args.output_root)
    downloads_root = output_root / "gtfs_downloads"
    geojson_root = output_root / "metro_transit_geometries"
    manifests_root = output_root / "feed_manifests"

    total_features = 0

    for metro_name in target_metros:
        key = norm_text(metro_name)
        feature = metro_lookup.get(key)
        if not feature:
            print(f"[skip] metro not found in boundaries: {metro_name}")
            continue

        bbox = compute_feature_bbox(feature)
        if not bbox:
            print(f"[skip] metro missing geometry bbox: {metro_name}")
            continue

        matched_rows = discover_feed_rows_for_metro(rows, metro_name)
        if not matched_rows:
            print(f"[warn] no GTFS feed rows matched metro: {metro_name}")
            continue

        matched_rows = matched_rows[: args.max_feeds_per_metro]
        metro_slug = slugify(metro_name)

        manifest_path = manifests_root / f"feeds_{metro_slug}.csv"
        write_manifest(matched_rows, manifest_path)
        print(f"[metro] {metro_name} -> {len(matched_rows)} feed URLs")
        print(f"        manifest: {manifest_path}")

        if args.dry_run:
            continue

        metro_download_dir = downloads_root / metro_slug
        metro_features: List[Dict] = []

        for idx, row in enumerate(matched_rows, start=1):
            url = extract_weblink(row.get("weblink"))
            if not url:
                continue

            agency_name = str(row.get("agency_name") or "")
            ntd_id = str(row.get("ntd_id") or "")
            feed_slug = slugify(f"{agency_name}-{ntd_id}-{idx}")
            zip_path = metro_download_dir / f"{feed_slug}.zip"

            success = False
            for attempt in range(args.download_retries + 1):
                try:
                    download_file(url, zip_path)
                    success = True
                    break
                except Exception as exc:  # pylint: disable=broad-except
                    if attempt >= args.download_retries:
                        print(f"  [fail] {url} -> {exc}")
                    else:
                        time.sleep(1.0)

            if not success:
                continue

            try:
                features = features_from_gtfs_zip(
                    zip_path=zip_path,
                    metro_name=metro_name,
                    metro_bbox=bbox,
                    feed_url=url,
                    agency_name=agency_name,
                    ntd_id=ntd_id,
                )
                metro_features.extend(features)
                print(f"  [ok] {agency_name} -> {len(features)} shapes")
            except zipfile.BadZipFile:
                print(f"  [skip] invalid zip: {url}")
            except Exception as exc:  # pylint: disable=broad-except
                print(f"  [skip] parse error {url}: {exc}")

        out_geojson = geojson_root / f"{metro_slug}.geojson"
        write_geojson(metro_features, out_geojson)
        total_features += len(metro_features)
        print(f"        geojson: {out_geojson} ({len(metro_features)} features)")

    print(f"Done. Total exported features: {total_features}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
