import os
import json
import time
import argparse

import requests
from osm2geojson import json2geojson
import geopandas as gpd
from tqdm import tqdm
import geojson

QUERY_TRANSIT_POINT = """[out:json];
(
way["railway"~"^(subway|light_rail|tram)$"]
    ["service"!~"yard|spur|sliding|siding|crossover"]
    ["usage"!~"industrial"]
    ["railway:traffic_mode"!~"freight"]
    (around:50000.00,{lat},{lon});
);
out geom;
"""

QUERY_TRANSIT_BBOX = """[out:json];
(
way["railway"~"^(subway|light_rail|tram)$"]
    ["service"!~"yard|spur|sliding|siding|crossover"]
    ["usage"!~"industrial"]
    ["railway:traffic_mode"!~"freight"]
    ({south},{west},{north},{east});
);
out geom;
"""

OVERPASS_URLS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
]


def run_query(query, retries=4, **query_params):
    """Query Overpass and return parsed GeoJSON with retry/fallback behavior."""
    query_text = query.format(**query_params)
    headers = {
        'User-Agent': 'urban-activity-atlas/1.0 (transit-extraction)',
        'Accept': 'application/json',
    }

    last_error = None
    for url in OVERPASS_URLS:
        for attempt in range(retries):
            try:
                response = requests.post(
                    url,
                    data={'data': query_text},
                    headers=headers,
                    timeout=(15, 45),
                )

                # Retry aggressively on common Overpass transient failures.
                if response.status_code in (429, 500, 502, 503, 504):
                    wait_s = min(2 ** attempt, 20)
                    time.sleep(wait_s)
                    continue

                response.raise_for_status()

                try:
                    payload = response.json()
                except ValueError as exc:
                    snippet = response.text[:300].replace('\n', ' ')
                    raise RuntimeError(f'Non-JSON Overpass response: {snippet}') from exc

                return json2geojson(payload)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                last_error = exc
                wait_s = min(2 ** attempt, 20)
                time.sleep(wait_s)

    raise RuntimeError(f'Overpass query failed after retries: {last_error}')

def find_city_list_path():
    if os.path.exists('./data/city_list.gpkg'):
        return './data/city_list.gpkg'
    if os.path.exists('./data/city_list.geojson'):
        return './data/city_list.geojson'
    if os.path.exists('./data/metro_regions_full.geojson'):
        return './data/metro_regions_full.geojson'
    raise FileNotFoundError(
        'Missing city list file. Add ./data/city_list.gpkg or ./data/city_list.geojson, '
        'or use ./data/metro_regions_full.geojson.'
    )


def sanitize_city_name(name):
    return name.lower().replace(' ', '_').replace('/', '_').replace(',', '').replace('(', '').replace(')', '')


def keep_line_features(geojson_obj):
    features = geojson_obj.get('features', [])
    filtered_features = []
    for feature in features:
        geometry = feature.get('geometry')
        if not geometry:
            continue
        if geometry.get('type') in ('LineString', 'MultiLineString'):
            filtered_features.append(feature)
    geojson_obj['features'] = filtered_features
    return geojson_obj


def query_osm(target_metro=None, overwrite=False):
    """ Query each of our cities for transit data and save them as GeoJSONs."""
    city_list_path = find_city_list_path()
    gdf_city_list = gpd.read_file(city_list_path)

    if gdf_city_list.empty:
        raise ValueError(f'City list file {city_list_path} contains no features.')

    if 'NAME' not in gdf_city_list.columns and 'name' in gdf_city_list.columns:
        gdf_city_list['NAME'] = gdf_city_list['name']

    if 'NAME' not in gdf_city_list.columns:
        raise ValueError('City list file must contain a NAME or name field.')

    os.makedirs('./data/osm_data', exist_ok=True)
    request_delay_s = 0.6

    for i, row_i in tqdm(gdf_city_list.iterrows(), total=gdf_city_list.shape[0]):
        if target_metro and row_i['NAME'] != target_metro:
            continue

        city = sanitize_city_name(row_i['NAME'])

        out_transit_path = f'./data/osm_data/{city}_transit_osm.geojson'
        if os.path.exists(out_transit_path) and not overwrite:
            continue

        geometry = row_i['geometry']
        try:
            if geometry.geom_type in ('Point', 'MultiPoint'):
                lon, lat = geometry.x, geometry.y
                res_transit = run_query(QUERY_TRANSIT_POINT, lon=lon, lat=lat)
            else:
                minx, miny, maxx, maxy = geometry.bounds
                res_transit = run_query(
                    QUERY_TRANSIT_BBOX,
                    west=minx,
                    south=miny,
                    east=maxx,
                    north=maxy,
                )
            res_transit = keep_line_features(res_transit)
        except KeyboardInterrupt:
            print('\nInterrupted by user. Stopping early and keeping files already written.')
            break
        except Exception as exc:
            print(f'{city} failed: {exc}')
            time.sleep(request_delay_s)
            continue

        # https://gis.stackexchange.com/a/292255
        # https://gis.stackexchange.com/a/362044
        with open(out_transit_path, 'w') as f:
            geojson.dump(res_transit, f)

        time.sleep(request_delay_s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch local OSM transit lines for metros.')
    parser.add_argument('--metro', type=str, default=None, help='Exact metro name to fetch (matches NAME field).')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files in data/osm_data.')
    args = parser.parse_args()
    query_osm(target_metro=args.metro, overwrite=args.overwrite)