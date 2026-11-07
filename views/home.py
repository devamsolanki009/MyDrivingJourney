"""Home: animated hero, Cork centre status, EDT tracker and test structure."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from content import EDT_FACTS, EDT_LESSONS, FAULT_GRADES, LINKS, TEST_STRUCTURE
from data_loader import FOCUS_COUNTY, NATIONAL_COUNTY
from ui import (
    CORK_COLOR,
    FULL_WIDTH,
    NATIONAL_COLOR,
    WILTON_CENTRE,
    base_layout,
    cached_centre_activity,
    cached_waiting_times,
    cork_centre_status,
    format_month,
    safe_load,
    section,
)
from widgets import edt_tracker, hero

waiting = safe_load(cached_waiting_times, "Waiting times (ROA37)")
activity = safe_load(cached_centre_activity, "Centre activity (ROA32)")


def latest_two(frame: pd.DataFrame, county: str) -> tuple[pd.Series | None, pd.Series | None]:
    series = frame[frame["county"] == county].dropna(subset=["weeks"]).sort_values("period")
    if series.empty:
        return None, None
    previous = series.iloc[-2] if len(series) > 1 else None
    return series.iloc[-1], previous


def tone(delta: float | None) -> str:
    """A longer wait is bad news, so 'up' is styled as a warning."""
    if delta is None or abs(delta) < 0.05:
        return "neutral"
    return "up" if delta > 0 else "down"


# --------------------------------------------------------------------------- #
# Hero with live numbers
# --------------------------------------------------------------------------- #
stats: list[dict] = []
national = cork = None
if waiting is not None:
    national, national_prev = latest_two(waiting, NATIONAL_COUNTY)
    cork, _ = latest_two(waiting, FOCUS_COUNTY)
    if national is not None:
        delta = None if national_prev is None else float(national["weeks"] - national_prev["weeks"])
        stats.append({
            "label": "National wait for a car test", "value": round(float(national["weeks"]), 1), "decimals": 1,
            "suffix": "weeks", "tone": tone(delta),
            "note": "" if delta is None else f"{delta:+.1f} wks vs previous month",
        })
    if cork is not None:
        gap = None if national is None else float(cork["weeks"] - national["weeks"])
        stats.append({
            "label": "Co. Cork wait", "value": round(float(cork["weeks"]), 1), "decimals": 1, "suffix": "weeks",
            "tone": tone(gap), "note": "" if gap is None else f"{abs(gap):.1f} wks {'longer' if gap > 0 else 'shorter'} than national",
        })

status = None
if activity is not None:
    status = cork_centre_status(activity)
    wilton = status[status["centre"] == WILTON_CENTRE]
    if not wilton.empty:
        row = wilton.iloc[0]
        stats.append({
            "label": "Cork (Wilton) centre", "value": row["status"], "tone": "down" if row["reporting"] else "up",
            "note": f"Figures for {format_month(row['last_month'])}",
        })
        if pd.notna(row["waiting"]):
            stats.append({
                "label": "Waiting at Wilton (car)", "value": float(row["waiting"]), "decimals": 0, "suffix": "people",
                "tone": "neutral",
                "note": f"{row['applications']:,.0f} new applications" if pd.notna(row["applications"]) else "",
            })

latest = national["period"] if national is not None else None
hero(
    title="Irish Driving Test & EDT Master Hub",
    subtitle="Study the Wilton test routes and manoeuvres, find an instructor in County Cork, "
    "and see how long you are likely to wait for a test, using the latest RSA figures.",
    tag="Cork & National · Live RSA data",
    stats=stats,
    footnote=f"Data to {format_month(latest)}" if latest is not None else "",
)

# --------------------------------------------------------------------------- #
# Quick links
# --------------------------------------------------------------------------- #
link_cols = st.columns(3)
link_cols[0].page_link("views/routes.py", label="Test routes & simulator", icon=":material/route:")
link_cols[1].page_link("views/instructors.py", label="Find a Cork instructor (ADI)", icon=":material/school:")
link_cols[2].page_link("views/analytics.py", label="Waiting-time analytics", icon=":material/monitoring:")

# --------------------------------------------------------------------------- #
# Cork wait sparkline + centre table
# --------------------------------------------------------------------------- #
if waiting is not None and national is not None and cork is not None:
    section("At a glance", "Cork vs national: the last 24 months")
    recent_start = national["period"] - pd.DateOffset(months=23)
    fig = go.Figure()
    for county, color, name, dash in [
        (NATIONAL_COUNTY, NATIONAL_COLOR, "National", "dot"),
        (FOCUS_COUNTY, CORK_COLOR, "Co. Cork", "solid"),
    ]:
        series = waiting[(waiting["county"] == county) & (waiting["period"] >= recent_start)].sort_values("period")
        fig.add_trace(go.Scatter(
            x=series["period"], y=series["weeks"], name=name, mode="lines",
            line=dict(color=color, width=3, dash=dash, shape="spline"),
            fill="tozeroy" if county == FOCUS_COUNTY else None,
            fillcolor="rgba(11,110,79,0.08)",
            hovertemplate="%{y:.1f} weeks<extra>" + name + "</extra>",
        ))
    layout = base_layout("", "Weeks")
    layout["margin"] = dict(l=10, r=10, t=30, b=10)
    fig.update_layout(**layout, height=280)
    fig.update_xaxes(tickformat="%b\n%Y")
    st.plotly_chart(fig, **FULL_WIDTH, config={"displayModeBar": False})

if status is not None and not status.empty:
    section("Test centres", "Co. Cork centres right now")
    st.caption(
        "Car-test (Category B) figures for the latest month each centre appears in ROA32. "
        "Temporary venues stop reporting when they close."
    )
    max_waiting = float(status["waiting"].max()) if status["waiting"].notna().any() else 1.0
    table = status.assign(last_month=status["last_month"].map(format_month))[
        ["centre", "status", "last_month", "applications", "waiting", "scheduled"]
    ]
    st.dataframe(
        table,
        hide_index=True,
        **FULL_WIDTH,
        column_config={
            "centre": "Centre",
            "status": "Status",
            "last_month": "Latest month",
            "applications": st.column_config.NumberColumn("Applications", format="%d"),
            "waiting": st.column_config.ProgressColumn("Waiting", format="%d", min_value=0, max_value=max_waiting),
            "scheduled": st.column_config.NumberColumn("Scheduled", format="%d"),
        },
    )

# --------------------------------------------------------------------------- #
# EDT programme
# --------------------------------------------------------------------------- #
section("Essential Driver Training", "Track your 12 EDT lessons")
with st.expander("What you need to know about EDT", expanded=False):
    for fact in EDT_FACTS:
        st.markdown(f"- {fact}")
    st.caption("Check the current syllabus and rules at rsa.ie before you book.")
edt_tracker(EDT_LESSONS)

# --------------------------------------------------------------------------- #
# RSA test
# --------------------------------------------------------------------------- #
section("On the day", "How the RSA car test works")
steps, grades = st.columns([1.5, 1], gap="large")
with steps:
    st.markdown(
        '<div class="steps">'
        + "".join(
            f'<div class="step" data-n="{i}" style="animation-delay:{i * 0.06:.2f}s"><b>{title}</b><br><span>{detail}</span></div>'
            for i, (title, detail) in enumerate(TEST_STRUCTURE, start=1)
        )
        + "</div>",
        unsafe_allow_html=True,
    )
with grades:
    st.markdown("**How faults are graded**")
    for grade, label, rule, color in FAULT_GRADES:
        st.markdown(
            f'<div class="grade" style="border-color:{color}"><b>{grade} · {label}</b><br>'
            f'<span class="note">{rule}</span></div>',
            unsafe_allow_html=True,
        )
    st.page_link("views/routes.py", label="See the full fault guidelines", icon=":material/arrow_forward:")

section("Official services", "Book, apply and check")
ext_cols = st.columns(len(LINKS))
for column, (label, url) in zip(ext_cols, LINKS.items()):
    column.link_button(label, url, **FULL_WIDTH)
