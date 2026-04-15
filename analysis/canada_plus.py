# Filter everything but Canada & Oregon for 2019-2020 & just Oregon for 2024-2025
## Use them for 2019-2020 & 2024-2025 -> insert into our existing data metro_regions_full_startyear_endyear and the folder of metro_region_geohash_stops_startyear_endyear
import os
import shutil
from pathlib import Path
from typing import Iterable, Set
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

CONCORDANCE_FILE = DATA_DIR / "metro_region_geohashes_no_military.csv"

# New SIERRA extracts (adjust names if needed)
SIERRA_2019_2020 = DATA_DIR / "urbanactivityatlas_sierra_19_20.csv"
SIERRA_2024_2025 = DATA_DIR / "urbanactivityatlas_sierra_24_25.csv"

# Filtered activity outputs (feed these into join_metro_geohash.ipynb activity_file)
FILTERED_2019_2020 = DATA_DIR / "activity_sierra_patch_2019-04-01_2020-03-31.csv"
FILTERED_2024_2025 = DATA_DIR / "activity_sierra_patch_2024-04-01_2025-03-31.csv"

# If you run notebook into these "patch" dirs, this script can append/copy to final dirs
PATCH_DIR_2019_2020 = DATA_DIR / "metro_region_geohash_stops_2019_2020_patch"
PATCH_DIR_2024_2025 = DATA_DIR / "metro_region_geohash_stops_2024_2025_patch"

FINAL_DIR_2019_2020 = DATA_DIR / "metro_region_geohash_stops_2019_2020"
FINAL_DIR_2024_2025 = DATA_DIR / "metro_region_geohash_stops_2024_2025"

CANADA_PROV_CODES = {
    "ON", "QC", "BC", "AB", "MB", "SK", "NS", "NB", "NL", "PE", "YT", "NT", "NU"
}

## renaming cols
def normalize_activity_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()
    if "geohash" not in df.columns:
        if "geohash6" in df.columns:
            df = df.rename(columns={"geohash6": "geohash"})
        else:
            raise ValueError("Expected 'geohash' or 'geohash6' column in activity data.")
    df["geohash"] = df["geohash"].astype(str).str.strip()
    return df

# renaming regions
def region_state_tokens(region_name: str) -> Set[str]:
    """
    Example inputs:
      'Portland-Vancouver-Hillsboro, OR-WA' -> {'OR','WA'}
      'Toronto, ON' -> {'ON'}
      'Ottawa - Gatineau, ON-QC' -> {'ON','QC'}
    """
    if "," not in region_name:
        return set()
    state_part = region_name.split(",", 1)[1].strip()
    tokens = [t.strip() for t in state_part.replace("/", "-").split("-")]
    return {t for t in tokens if t}

# oregon!
def is_oregon_region(region_name: str) -> bool:
    return "OR" in region_state_tokens(region_name)

# is canada!
def is_canada_region(region_name: str) -> bool:
    tokens = region_state_tokens(region_name)
    return len(tokens.intersection(CANADA_PROV_CODES)) > 0

# filter geohashes to oregon / canada (bool to set)
def build_geohash_allowlist(concordance_df: pd.DataFrame, include_oregon: bool, include_canada: bool) -> Set[str]:
    c = concordance_df.copy()
    c.columns = c.columns.str.lower().str.strip()
    if not {"geohash", "name"}.issubset(c.columns):
        raise ValueError("Concordance must have columns: geohash, name")
    c["geohash"] = c["geohash"].astype(str).str.strip()
    c["name"] = c["name"].astype(str).str.strip()

    mask = pd.Series(False, index=c.index)
    if include_oregon:
        mask = mask | c["name"].map(is_oregon_region)
    if include_canada:
        mask = mask | c["name"].map(is_canada_region)

    return set(c.loc[mask, "geohash"].unique())

def filter_activity_by_geohash(activity_csv: Path, geohash_allowlist: Set[str], out_csv: Path) -> None:
    if not activity_csv.exists():
        raise FileNotFoundError(f"Missing input file: {activity_csv}")

    df = pd.read_csv(activity_csv)
    df = normalize_activity_columns(df)
    before = len(df)
    df = df[df["geohash"].isin(geohash_allowlist)].copy()
    after = len(df)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"[ok] {activity_csv.name}: {before:,} -> {after:,} rows | wrote {out_csv}")

def append_geojson_files(src_dir: Path, dst_dir: Path, overwrite: bool = False) -> None:
    """
    Appends region files by copying from src patch dir into final dir.
    - If overwrite=False, keeps existing destination files and only adds missing regions.
    """
    if not src_dir.exists():
        print(f"[skip] source dir not found: {src_dir}")
        return

    dst_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    for p in src_dir.glob("*.geojson"):
        dst = dst_dir / p.name
        if dst.exists() and not overwrite:
            skipped += 1
            continue
        shutil.copy2(p, dst)
        copied += 1

    print(f"[ok] appended from {src_dir.name} -> {dst_dir.name} | copied={copied}, skipped={skipped}")

def get_expected_metro_names(concordance_df: pd.DataFrame) -> Set[str]:
    c = concordance_df.copy()
    c.columns = c.columns.str.lower().str.strip()
    if "name" not in c.columns:
        raise ValueError("Concordance must have a 'name' column")
    return set(c["name"].astype(str).str.strip().unique())


def verify_metro_geojson_coverage(output_dir: Path, expected_regions: Set[str], label: str) -> dict:
    if not output_dir.exists():
        print(f"[verify:{label}] missing directory: {output_dir}")
        return {"missing": sorted(expected_regions), "extra": [], "zero_byte_files": []}

    geojson_files = list(output_dir.glob("*.geojson"))
    found_regions = {p.stem.strip() for p in geojson_files}

    missing = sorted(expected_regions - found_regions)
    extra = sorted(found_regions - expected_regions)
    zero_byte_files = sorted([p.name for p in geojson_files if p.stat().st_size == 0])

    print(
        f"[verify:{label}] expected={len(expected_regions)} | "
        f"found={len(found_regions)} | missing={len(missing)} | "
        f"extra={len(extra)} | zero_byte={len(zero_byte_files)}"
    )

    if missing:
        print(f"[verify:{label}] missing sample: {missing[:20]}")
    if extra:
        print(f"[verify:{label}] extra sample: {extra[:20]}")
    if zero_byte_files:
        print(f"[verify:{label}] zero-byte sample: {zero_byte_files[:20]}")

    return {"missing": missing, "extra": extra, "zero_byte_files": zero_byte_files}


def main() -> None:
    if not CONCORDANCE_FILE.exists():
        raise FileNotFoundError(f"Missing concordance file: {CONCORDANCE_FILE}")

    concordance = pd.read_csv(CONCORDANCE_FILE)

    # 2019-2020: Canada + Oregon
    # allow_2019 = build_geohash_allowlist(concordance, include_oregon=True, include_canada=True)
    # filter_activity_by_geohash(SIERRA_2019_2020, allow_2019, FILTERED_2019_2020)

    # # 2024-2025: Oregon only
    # allow_2024 = build_geohash_allowlist(concordance, include_oregon=True, include_canada=False)
    # filter_activity_by_geohash(SIERRA_2024_2025, allow_2024, FILTERED_2024_2025)

    # Optional post-notebook append/copy step:
    # append_geojson_files(PATCH_DIR_2019_2020, FINAL_DIR_2019_2020, overwrite=False)
    # append_geojson_files(PATCH_DIR_2024_2025, FINAL_DIR_2024_2025, overwrite=False)

    # Verification: ensure final folders contain all expected metro files
    expected_metros = get_expected_metro_names(concordance)
    verify_metro_geojson_coverage(FINAL_DIR_2019_2020, expected_metros, "2019_2020")
    verify_metro_geojson_coverage(FINAL_DIR_2024_2025, expected_metros, "2024_2025")


if __name__ == "__main__":
    main()