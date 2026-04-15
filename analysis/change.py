"""
Generate % change csvs for the difference of normalized stops between 2 years for each geohash:

Input:
- Folder of geohashes containing the total_stops normalized values (2 folders for each year)
- pmtiles? geojson?

Output:
- Folder containing the difference of the normalized total stops values between the two windows (ex. change_2019_2020_to_2024_2025)
"""

import json
from pathlib import Path

# window1 = 2019
# window2 = 2023

window1 = 2019
window2 = 2024

# window1 = 2023
# window2 = 2024

# folder1 = "data/metro_region_geohash_stops_2019_2020"
# folder2 = "data/metro_region_geohash_stops"

folder1 = "data/metro_region_geohash_stops_2019_2020"
folder2 = "data/metro_region_geohash_stops_2024_2025"

# folder1 = "data/metro_region_geohash_stops"
# folder2 = "data/metro_region_geohash_stops_2024_2025"


def read_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_geojson(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def get_metric(feature, metric_name):
    props = feature.get("properties", {})
    value = props.get(metric_name, 0)
    if value is None:
        return 0.0
    return float(value)


def build_geohash_map(features):
    output = {}
    for feature in features:
        geohash = feature.get("properties", {}).get("geohash")
        if geohash:
            output[geohash] = feature
    return output


def change(folder1, folder2):
    # look in each folder where you'll find geojson files for each metro

    input1 = Path(folder1)
    input2 = Path(folder2)
    output = Path(f"data/metro_region_geohash_stops_change_{window1}_{window1 + 1}_to_{window2}_{window2 + 1}")
    output.mkdir(parents=True, exist_ok=True)

    files1 = {p.name: p for p in input1.glob("*.geojson")}
    files2 = {p.name: p for p in input2.glob("*.geojson")}
    common_files = sorted(set(files1.keys()) & set(files2.keys()))

    for file_name in common_files:
        metro_1 = read_geojson(files1[file_name])
        metro_2 = read_geojson(files2[file_name])

        features_1 = metro_1.get("features", [])
        features_2 = metro_2.get("features", [])

        by_geohash_1 = build_geohash_map(features_1)
        by_geohash_2 = build_geohash_map(features_2)

        # Only keep geohashes present in both windows (so we can compute percent change)
        all_geohashes = sorted(set(by_geohash_1.keys()) & set(by_geohash_2.keys()))

        out_features = []

    # in each metro, there are geohashes (level 6)

    # if there's a match in geohash between the two folders within each metro, then
    # grab the prop_subset_stops property and take the difference between the two
        metric_name = "prop_subset_stops"
        for geohash in all_geohashes:
            f1 = by_geohash_1.get(geohash)
            f2 = by_geohash_2.get(geohash)

            base_feature = json.loads(json.dumps(f2 if f2 is not None else f1))
            props = base_feature.setdefault("properties", {})

            value_1 = get_metric(f1, metric_name) if f1 is not None else 0.0
            value_2 = get_metric(f2, metric_name) if f2 is not None else 0.0
            diff = value_2 - value_1
            pct_change = (diff / value_1) if value_1 != 0 else None

            props[f"{metric_name}_{window1}_{window1 + 1}"] = value_1
            props[f"{metric_name}_{window2}_{window2 + 1}"] = value_2
            props[f"{metric_name}_change"] = diff
            props[f"{metric_name}_pct_change"] = pct_change

            out_features.append(base_feature)

        write_geojson(
            output / file_name,
            {
                "type": "FeatureCollection",
                "name": Path(file_name).stem,
                "features": out_features,
            },
        )

        print(f"Wrote change geojson for {Path(file_name).stem}")

    print(f"Done. Output folder: {output}")


def __main__():
    

    change(folder1, folder2)


if __name__ == "__main__":
    __main__()