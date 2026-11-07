"""Shared look, chart defaults, and cached data access for every page."""

from __future__ import annotations

import re
from datetime import date

import pandas as pd
import streamlit as st

from data_loader import (
    ALL_CENTRES,
    DataLoadError,
    load_annual_series,
    load_centre_activity,
    load_waiting_times,
)

CORK_COLOR = "#0B6E4F"
NATIONAL_COLOR = "#C45C26"
ACCENT = "#1F4E79"
MUTED = "#5C6770"
SERIES_COLORS = ["#1F4E79", "#5C4B8A", "#2A6F97", "#9A3412", "#3F6212", "#9F1239", "#0F766E", "#854D0E"]

# Full-width elements: Streamlit 1.50+ takes width="stretch"; older releases
# (e.g. 1.45) only accept use_container_width=True and crash on the string.
_ST_VERSION = tuple(int(part) for part in re.findall(r"\d+", st.__version__)[:2])
FULL_WIDTH: dict = {"width": "stretch"} if _ST_VERSION >= (1, 50) else {"use_container_width": True}

CAR_CATEGORY = "Category B (Car or light van)"
WAITING_STATISTIC = "Driving Test Applicants Waiting at Month End"
SCHEDULED_STATISTIC = "Driving Test Applicants Scheduled at Month End"
WILTON_CENTRE = "Cork (Wilton), Co. Cork"


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Loading county waiting times…")
def cached_waiting_times() -> pd.DataFrame:
    return load_waiting_times()


@st.cache_data(show_spinner="Loading test-centre activity…")
def cached_centre_activity() -> pd.DataFrame:
    return load_centre_activity()


@st.cache_data(show_spinner="Loading annual history…")
def cached_annual_series() -> pd.DataFrame:
    return load_annual_series()


def safe_load(loader, label: str) -> pd.DataFrame | None:
    """Run a cached loader and show a readable error instead of a traceback."""
    try:
        return loader()
    except DataLoadError as exc:
        st.error(f"{label}: {exc}")
    except Exception as exc:  # noqa: BLE001 - last line of defence for odd CSV layouts
        st.error(f"{label}: unexpected problem reading the file ({type(exc).__name__}: {exc}).")
    return None


def cork_centre_status(activity: pd.DataFrame) -> pd.DataFrame:
    """Latest published car-test figures for every Co. Cork centre in ROA32.

    A centre is 'Reporting' when it has figures for the newest month in the file.
    Otherwise the status names the last month it appeared.
    """
    latest_month = activity["period"].max()
    car = activity[
        (activity["category"] == CAR_CATEGORY)
        & activity["centre"].str.contains("Co. Cork", regex=False)
        & (activity["centre"] != ALL_CENTRES)
    ].dropna(subset=["value"])

    rows = []
    for centre, frame in car.groupby("centre", observed=True):
        last = frame["period"].max()
        at_last = frame[frame["period"] == last].set_index("statistic")["value"]
        rows.append(
            {
                "centre": centre,
                "status": "Reporting" if last == latest_month else f"No figures since {last:%b %Y}",
                "reporting": last == latest_month,
                "last_month": last,
                "applications": at_last.get("Driving Test Applications Received"),
                "waiting": at_last.get(WAITING_STATISTIC),
                "scheduled": at_last.get(SCHEDULED_STATISTIC),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["centre", "status", "reporting", "last_month", "applications", "waiting", "scheduled"])
    return pd.DataFrame(rows).sort_values(["reporting", "waiting"], ascending=[False, False]).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Look and feel
# --------------------------------------------------------------------------- #
def apply_theme() -> None:
    """Inject the global stylesheet (static/theme.css)."""
    from widgets import inject_theme

    inject_theme()


def section(kicker: str, title: str) -> None:
    """Small kicker label plus a heading with an accent bar."""
    st.markdown(
        f'<p class="kicker" style="margin-top:1.6rem">{kicker}</p>'
        f'<div class="section-title"><span class="bar"></span><h3 style="margin:0">{title}</h3></div>',
        unsafe_allow_html=True,
    )


def page_header(kicker: str, title: str, intro: str | None = None) -> None:
    st.markdown(f'<p class="kicker">{kicker}</p>', unsafe_allow_html=True)
    st.title(title)
    if intro:
        st.markdown(f'<p class="note">{intro}</p>', unsafe_allow_html=True)


def base_layout(title: str, y_title: str) -> dict:
    return dict(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=17, color="#1A2332")),
        template="plotly_white",
        font=dict(family="Segoe UI, Inter, sans-serif", color="#1A2332", size=13),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=16, r=16, t=72, b=16),
        yaxis=dict(title=y_title, gridcolor="#eeeae4", zeroline=False),
        xaxis=dict(title="", showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def format_month(value) -> str:
    return pd.Timestamp(value).strftime("%b %Y")


def fmt_number(value, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.0f}{suffix}"


def month_options(periods: pd.Series) -> list[date]:
    """First-of-month dates, in order, for a month slider that cannot land mid-month."""
    unique = sorted(pd.to_datetime(periods).dropna().unique())
    return [pd.Timestamp(value).date().replace(day=1) for value in unique]


def filter_months(frame: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    period = frame["period"]
    mask = (period >= pd.Timestamp(start)) & (period <= pd.Timestamp(end))
    return frame.loc[mask].copy()
