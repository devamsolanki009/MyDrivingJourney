"""Load and tidy the RSA / CSO driving-test extracts used by the app.

The published files are PxStat CSV downloads. Column titles can arrive with a
BOM, wrapped quotes, or a blank VALUE cell where a figure was not published.
This module normalises those quirks and raises DataLoadError with the column
names it actually found when a required field is missing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

# Prefer the extracts shipped with the project, then any newer ROA*.csv.
KNOWN_FILES = {
    "ROA37": "ROA37.20261107121327.csv",
    "ROA32": "ROA32.20261107123145.csv",
    "ROA05": "ROA05.20261107131053.csv",
}

NATIONAL_COUNTY = "Ireland"
FOCUS_COUNTY = "Co. Cork"
ALL_CENTRES = "All driving test centres"
ALL_CATEGORIES = "All Test Categories"
APPLICATIONS_STATISTIC = "Driving Test Applications Received"


class DataLoadError(Exception):
    """Raised when a CSV is missing, empty, or does not match the expected layout."""


def resolve_csv(dataset_code: str) -> Path:
    """Return the on-disk CSV for an ROA table code such as 'ROA37'."""
    known_name = KNOWN_FILES.get(dataset_code)
    if known_name:
        known_path = DATA_DIR / known_name
        if known_path.is_file():
            return known_path

    matches = sorted(DATA_DIR.glob(f"{dataset_code}*.csv"))
    if not matches:
        expected = known_name or f"{dataset_code}*.csv"
        raise DataLoadError(
            f"Could not find {dataset_code} data in {DATA_DIR}. "
            f"Place {expected} next to app.py and restart."
        )
    return matches[-1]


def _read_csv(path: Path) -> pd.DataFrame:
    """Read a CSO CSV, stripping a leading BOM from the header if present."""
    try:
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError as exc:
        raise DataLoadError(f"{path.name} is empty.") from exc
    except OSError as exc:
        raise DataLoadError(f"Could not read {path.name}: {exc}") from exc
    except UnicodeError as exc:
        raise DataLoadError(
            f"{path.name} is not valid UTF-8. Re-download the CSO CSV and try again."
        ) from exc

    frame.columns = [_clean_header(column) for column in frame.columns]
    if frame.empty:
        raise DataLoadError(f"{path.name} has a header but no data rows.")
    return frame


def _clean_header(name: str) -> str:
    text = str(name).replace("\ufeff", "").strip().strip('"').strip()
    return re.sub(r"\s+", " ", text)


def _normalise_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _clean_header(name).lower())


def require_column(frame: pd.DataFrame, candidates: list[str], label: str, source: str) -> str:
    """Return the actual column name matching one of `candidates`.

    Matching ignores case, spaces, and punctuation so 'TLIST(M1)' and
    'tlist m1' both resolve. A clear error lists the headers that were found.
    """
    lookup = {_normalise_key(column): column for column in frame.columns}
    for candidate in candidates:
        found = lookup.get(_normalise_key(candidate))
        if found:
            return found

    found_headers = ", ".join(frame.columns.astype(str)) or "(none)"
    expected = ", ".join(candidates)
    raise DataLoadError(
        f"{source} is missing a {label} column. Expected one of: {expected}. "
        f"Columns in the file: {found_headers}."
    )


def to_numeric(series: pd.Series) -> pd.Series:
    """Coerce CSO values to numbers. Blanks and suppression symbols become NaN."""
    text = series.astype(str).str.strip()
    text = text.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            ":": pd.NA,
            "..": pd.NA,
            "-": pd.NA,
            "n/a": pd.NA,
            "N/A": pd.NA,
        }
    )
    return pd.to_numeric(text, errors="coerce")


def _parse_year_month(values: pd.Series) -> pd.Series:
    """Parse YYYYMM codes such as 202109 into month-start timestamps."""
    raw = values.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return pd.to_datetime(raw, format="%Y%m", errors="coerce")


def _parse_month_label(values: pd.Series) -> pd.Series:
    """Parse labels such as '2021 September'."""
    parsed = pd.to_datetime(values.astype(str).str.strip(), format="%Y %B", errors="coerce")
    if parsed.notna().mean() >= 0.5:
        return parsed
    return pd.to_datetime(values.astype(str).str.strip(), errors="coerce")


def parse_monthly_period(frame: pd.DataFrame, source: str) -> pd.Series:
    """Build a monthly timestamp, preferring the numeric TLIST code over the label."""
    tlist_name = None
    for column in frame.columns:
        key = _normalise_key(column)
        if key in {"tlistm1", "tlist"} or key.startswith("tlist"):
            tlist_name = column
            break

    if tlist_name is not None:
        parsed = _parse_year_month(frame[tlist_name])
        if parsed.notna().mean() >= 0.8:
            return parsed

    month_name = None
    try:
        month_name = require_column(frame, ["Month", "month"], "month", source)
    except DataLoadError:
        month_name = None

    if month_name is not None:
        parsed = _parse_month_label(frame[month_name])
        if parsed.notna().any():
            return parsed

    raise DataLoadError(
        f"{source} has no usable month column. Expected TLIST(M1) as YYYYMM "
        f"or Month as '2021 September'."
    )


def load_waiting_times() -> pd.DataFrame:
    """ROA37: estimated weeks to a car-test invite, by county and month.

    Returns columns: period, county, weeks, unit, source_file.
    The published 'Ireland' row is the national figure, not an average computed here.
    """
    path = resolve_csv("ROA37")
    raw = _read_csv(path)
    county_col = require_column(raw, ["County"], "county", path.name)
    value_col = require_column(raw, ["VALUE", "Value"], "value", path.name)
    unit_col = next((c for c in raw.columns if _normalise_key(c) == "unit"), None)

    tidy = pd.DataFrame(
        {
            "period": parse_monthly_period(raw, path.name),
            "county": raw[county_col].astype(str).str.strip(),
            "weeks": to_numeric(raw[value_col]),
            "unit": raw[unit_col].astype(str).str.strip() if unit_col else "Weeks",
        }
    )
    tidy = tidy.dropna(subset=["period"])
    tidy = tidy[tidy["county"].ne("") & tidy["county"].str.lower().ne("nan")]
    if tidy.empty:
        raise DataLoadError(f"{path.name} has no dated county rows after cleaning.")

    # One row per county-month if the extract ever repeats a cell.
    tidy = (
        tidy.groupby(["period", "county"], as_index=False)
        .agg(weeks=("weeks", "mean"), unit=("unit", "first"))
        .sort_values(["county", "period"])
        .reset_index(drop=True)
    )
    tidy["source_file"] = path.name
    return tidy


def load_centre_activity() -> pd.DataFrame:
    """ROA32: monthly counts by statistic, test category, and centre.

    Returns columns: period, statistic, category, centre, value, unit, source_file.
    'All driving test centres' is kept so headline totals can use the official aggregate.
    """
    path = resolve_csv("ROA32")
    raw = _read_csv(path)
    stat_col = require_column(raw, ["Statistic Label", "Statistic"], "statistic", path.name)
    category_col = require_column(
        raw, ["Driving Test Categories", "Category"], "test category", path.name
    )
    centre_col = require_column(
        raw, ["Driving Test Centre", "Centre"], "test centre", path.name
    )
    value_col = require_column(raw, ["VALUE", "Value"], "value", path.name)
    unit_col = next((c for c in raw.columns if _normalise_key(c) == "unit"), None)

    tidy = pd.DataFrame(
        {
            "period": parse_monthly_period(raw, path.name),
            "statistic": raw[stat_col].astype(str).str.strip(),
            "category": raw[category_col].astype(str).str.strip(),
            "centre": raw[centre_col].astype(str).str.strip(),
            "value": to_numeric(raw[value_col]),
            "unit": raw[unit_col].astype(str).str.strip() if unit_col else "Number",
        }
    )
    tidy = tidy.dropna(subset=["period"])
    tidy = tidy[tidy["centre"].ne("") & tidy["category"].ne("") & tidy["statistic"].ne("")]
    if tidy.empty:
        raise DataLoadError(f"{path.name} has no usable centre rows after cleaning.")

    keys = ["period", "statistic", "category", "centre"]
    if tidy.duplicated(keys).any():
        # Vectorised sum; min_count=1 keeps an all-blank group as missing instead of 0.
        grouped = tidy.groupby(keys, sort=False)
        tidy = pd.concat(
            [grouped["value"].sum(min_count=1), grouped["unit"].first()], axis=1
        ).reset_index()
    tidy = tidy.sort_values(["statistic", "category", "centre", "period"]).reset_index(drop=True)
    # ~460k rows of a few dozen repeated labels: categoricals make filtering and caching cheaper.
    for column in ["statistic", "category", "centre", "unit"]:
        tidy[column] = tidy[column].astype("category")
    tidy["source_file"] = path.name
    return tidy


def load_annual_series() -> pd.DataFrame:
    """ROA05: national annual series from 2005 onwards.

    Returns columns: year, statistic, value, unit, source_file.
    """
    path = resolve_csv("ROA05")
    raw = _read_csv(path)
    stat_col = require_column(raw, ["Statistic Label", "Statistic"], "statistic", path.name)
    value_col = require_column(raw, ["VALUE", "Value"], "value", path.name)
    unit_col = next((c for c in raw.columns if _normalise_key(c) == "unit"), None)

    year_col = None
    for column in raw.columns:
        if _normalise_key(column) in {"year", "tlista1"} or _normalise_key(column).startswith("tlist"):
            year_col = column
            break
    if year_col is None:
        try:
            year_col = require_column(raw, ["Year", "YEAR"], "year", path.name)
        except DataLoadError as exc:
            raise DataLoadError(
                f"{path.name} is missing a year column (Year or TLIST(A1))."
            ) from exc

    years = pd.to_numeric(
        raw[year_col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True),
        errors="coerce",
    )
    tidy = pd.DataFrame(
        {
            "year": years,
            "statistic": raw[stat_col].astype(str).str.strip(),
            "value": to_numeric(raw[value_col]),
            "unit": raw[unit_col].astype(str).str.strip() if unit_col else "",
        }
    )
    tidy = tidy.dropna(subset=["year"])
    tidy["year"] = tidy["year"].astype(int)
    tidy = tidy[tidy["year"] >= 2005]
    tidy = tidy[tidy["statistic"].ne("")]
    if tidy.empty:
        raise DataLoadError(f"{path.name} has no annual rows from 2005 onwards.")

    tidy = (
        tidy.groupby(["year", "statistic"], as_index=False)
        .agg(value=("value", "mean"), unit=("unit", "first"))
        .sort_values(["statistic", "year"])
        .reset_index(drop=True)
    )
    tidy["source_file"] = path.name
    return tidy


def series_summary(values: pd.Series, periods: pd.Series) -> dict | None:
    """Mean, median, min, max, and latest non-missing observation for a series."""
    frame = pd.DataFrame({"period": periods, "value": values}).dropna(subset=["value"])
    frame = frame.sort_values("period").reset_index(drop=True)
    if frame.empty:
        return None
    latest = frame.iloc[-1]
    peak = frame.loc[frame["value"].idxmax()]
    low = frame.loc[frame["value"].idxmin()]
    return {
        "mean": float(frame["value"].mean()),
        "median": float(frame["value"].median()),
        "min": float(low["value"]),
        "min_period": low["period"],
        "max": float(peak["value"]),
        "max_period": peak["period"],
        "current": float(latest["value"]),
        "current_period": latest["period"],
        "observations": int(len(frame)),
    }
