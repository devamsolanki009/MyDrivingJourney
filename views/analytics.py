"""Waiting times (ROA37), centre applications (ROA32) and the annual series (ROA05)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import (
    ALL_CATEGORIES,
    ALL_CENTRES,
    APPLICATIONS_STATISTIC,
    FOCUS_COUNTY,
    NATIONAL_COUNTY,
    series_summary,
)
from ui import (
    FULL_WIDTH,
    ACCENT,
    CAR_CATEGORY,
    CORK_COLOR,
    NATIONAL_COLOR,
    SERIES_COLORS,
    base_layout,
    cached_annual_series,
    cached_centre_activity,
    cached_waiting_times,
    filter_months,
    format_month,
    month_options,
    page_header,
    safe_load,
)

page_header(
    "RSA open data",
    "Waiting Times & Analytics",
    "How long learners wait for a car test in Co. Cork compared with the national figure, "
    "and how many applications each test centre receives. Blank cells in the source files are "
    "unpublished and are left out of averages and totals.",
)


# --------------------------------------------------------------------------- #
# ROA37 waiting times
# --------------------------------------------------------------------------- #
def stat_cards(label: str, stats: dict | None) -> None:
    """Mean / Median / Min / Max cards for one series."""
    st.markdown(f"**{label}**")
    cards = st.columns(4)
    if stats is None:
        for column, name in zip(cards, ["Mean", "Median", "Min", "Max"]):
            column.metric(name, "—")
        return
    cards[0].metric("Mean (wks)", f"{stats['mean']:.1f}")
    cards[1].metric("Median (wks)", f"{stats['median']:.1f}")
    cards[2].metric("Min (wks)", f"{stats['min']:.1f}", help=f"Lowest in {format_month(stats['min_period'])}")
    cards[3].metric("Max (wks)", f"{stats['max']:.1f}", help=f"Highest in {format_month(stats['max_period'])}")


def render_waiting(waiting: pd.DataFrame) -> None:
    counties = sorted(c for c in waiting["county"].unique() if c != NATIONAL_COUNTY)
    if FOCUS_COUNTY not in counties:
        st.warning(f"{FOCUS_COUNTY} is not in this ROA37 extract. Pick counties to compare instead.")
    other_counties = [c for c in counties if c != FOCUS_COUNTY]

    controls = st.columns([2, 1.2])
    with controls[0]:
        selected_extra = st.multiselect(
            "Add counties to compare",
            options=other_counties,
            default=[],
            placeholder="Co. Cork and the national figure are always shown",
        )
    months = month_options(waiting["period"])
    with controls[1]:
        start, end = st.select_slider(
            "Month range",
            options=months,
            value=(months[0], months[-1]),
            format_func=format_month,
            key="roa37_months",
        )

    window = filter_months(waiting, start, end)
    if window.empty:
        st.info("No waiting-time rows fall inside that month range.")
        return

    national = window[window["county"] == NATIONAL_COUNTY].sort_values("period")
    cork = window[window["county"] == FOCUS_COUNTY].sort_values("period")

    fig = go.Figure()
    if not national.empty:
        fig.add_trace(
            go.Scatter(
                x=national["period"],
                y=national["weeks"],
                name="National (Ireland)",
                mode="lines",
                line=dict(color=NATIONAL_COLOR, width=2.5, dash="dash"),
                hovertemplate="%{y:.1f} weeks<extra>Ireland</extra>",
            )
        )
    else:
        st.warning("This extract has no Ireland row, so the national line is omitted.")
    if not cork.empty:
        fig.add_trace(
            go.Scatter(
                x=cork["period"],
                y=cork["weeks"],
                name=FOCUS_COUNTY,
                mode="lines",
                line=dict(color=CORK_COLOR, width=3.2),
                hovertemplate="%{y:.1f} weeks<extra>Co. Cork</extra>",
            )
        )
    for index, county in enumerate(selected_extra):
        subset = window[window["county"] == county].sort_values("period")
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["period"],
                y=subset["weeks"],
                name=county,
                mode="lines",
                line=dict(color=SERIES_COLORS[index % len(SERIES_COLORS)], width=1.8),
                hovertemplate="%{y:.1f} weeks<extra>" + county + "</extra>",
            )
        )
    if not fig.data:
        st.info("No series have data in this range.")
        return

    fig.update_layout(**base_layout("Estimated weeks to a car-test invite", "Weeks"))
    fig.update_xaxes(dtick="M3", tickformat="%b\n%Y")
    st.plotly_chart(fig, **FULL_WIDTH)

    cork_stats = series_summary(cork["weeks"], cork["period"]) if not cork.empty else None
    national_stats = series_summary(national["weeks"], national["period"]) if not national.empty else None
    left, right = st.columns(2, gap="large")
    with left:
        stat_cards(f"Co. Cork, {format_month(start)} – {format_month(end)}", cork_stats)
    with right:
        stat_cards(f"National, {format_month(start)} – {format_month(end)}", national_stats)

    # Gap: positive means Cork waits longer than the national figure.
    if not cork.empty and not national.empty:
        gap = cork[["period", "weeks"]].merge(
            national[["period", "weeks"]], on="period", suffixes=("_cork", "_national")
        ).dropna()
        if not gap.empty:
            gap["gap"] = gap["weeks_cork"] - gap["weeks_national"]
            shorter = int((gap["gap"] < 0).sum())
            st.markdown(
                f"Co. Cork's wait was shorter than the national figure in **{shorter} of {len(gap)}** months "
                "in this range."
            )
            gap_fig = go.Figure(
                go.Bar(
                    x=gap["period"],
                    y=gap["gap"],
                    marker_color=[CORK_COLOR if v < 0 else NATIONAL_COLOR for v in gap["gap"]],
                    hovertemplate="%{x|%b %Y}<br>%{y:+.1f} weeks<extra></extra>",
                )
            )
            gap_layout = base_layout("Co. Cork minus national (weeks)", "Weeks")
            gap_layout["hovermode"] = "closest"
            gap_fig.update_layout(**gap_layout, height=300, showlegend=False)
            gap_fig.update_xaxes(dtick="M3", tickformat="%b\n%Y")
            gap_fig.add_hline(y=0, line_color="#9aa3ab", line_width=1)
            st.plotly_chart(gap_fig, **FULL_WIDTH)
            st.caption("Green bars: Cork waits less than the national figure. Orange bars: Cork waits more.")

    rows = []
    for county in [FOCUS_COUNTY, NATIONAL_COUNTY, *selected_extra]:
        subset = window[window["county"] == county]
        stats = series_summary(subset["weeks"], subset["period"])
        if stats is None:
            continue
        rows.append(
            {
                "County": "Ireland (national)" if county == NATIONAL_COUNTY else county,
                "Mean": round(stats["mean"], 1),
                "Median": round(stats["median"], 1),
                "Min": round(stats["min"], 1),
                "Max": round(stats["max"], 1),
                f"Latest ({format_month(stats['current_period'])})": round(stats["current"], 1),
            }
        )
    if len(rows) > 2:
        st.markdown("**All selected series (weeks)**")
        st.dataframe(pd.DataFrame(rows), **FULL_WIDTH, hide_index=True)


def render_gauges(waiting: pd.DataFrame) -> None:
    """Latest Co. Cork and national waits as gauges, with change since a year earlier."""
    fig = go.Figure()
    peak = float(waiting["weeks"].max()) if waiting["weeks"].notna().any() else 40.0
    for i, (county, name, color) in enumerate(
        [(FOCUS_COUNTY, "Co. Cork", CORK_COLOR), (NATIONAL_COUNTY, "National", NATIONAL_COLOR)]
    ):
        series = waiting[waiting["county"] == county].dropna(subset=["weeks"]).sort_values("period")
        if series.empty:
            continue
        latest = series.iloc[-1]
        year_ago = series[series["period"] <= latest["period"] - pd.DateOffset(months=12)]
        reference = float(year_ago["weeks"].iloc[-1]) if not year_ago.empty else None
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta" if reference is not None else "gauge+number",
                value=float(latest["weeks"]),
                number=dict(suffix=" wks", font=dict(size=34, color="#1A2332")),
                delta=dict(reference=reference, increasing=dict(color="#C2410C"), decreasing=dict(color=CORK_COLOR), valueformat=".1f")
                if reference is not None
                else None,
                title=dict(
                    text=f"<b>{name}</b><br><span style='font-size:12px;color:#5C6770'>{format_month(latest['period'])} · vs 12 months earlier</span>",
                    font=dict(size=17, color="#1A2332"),
                ),
                gauge=dict(
                    axis=dict(range=[0, peak * 1.05], tickcolor="#9aa3ab"),
                    bar=dict(color=color, thickness=0.3),
                    bgcolor="#F6F4F0",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 10], color="#E3F1EC"),
                        dict(range=[10, 20], color="#FBF1DD"),
                        dict(range=[20, peak * 1.05], color="#FBE3D7"),
                    ],
                ),
                domain=dict(x=[0.0, 0.46] if i == 0 else [0.54, 1.0], y=[0, 1]),
            )
        )
    if not fig.data:
        return
    fig.update_layout(
        height=270, margin=dict(l=30, r=30, t=80, b=10), paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#1A2332"),
    )
    st.plotly_chart(fig, **FULL_WIDTH, config={"displayModeBar": False})
    st.caption("Gauge bands: green under 10 weeks, amber 10–20 weeks, red over 20 weeks.")


def render_visual_explorer(waiting: pd.DataFrame) -> None:
    """Heatmap of every county by month, and an animated ranking you can play."""
    st.markdown("#### Visual explorer")
    heat_tab, race_tab = st.tabs(["Heatmap: every county, every month", "Animated ranking"])

    wide = waiting.pivot_table(index="county", columns="period", values="weeks")
    if wide.empty:
        st.info("No waiting-time data to plot.")
        return
    latest_col = wide.columns.max()
    wide = wide.sort_values(latest_col, ascending=True)
    labels = [f"<b>{c}</b>" if c in (FOCUS_COUNTY, NATIONAL_COUNTY) else c for c in wide.index]

    with heat_tab:
        heat = go.Figure(
            go.Heatmap(
                z=wide.values,
                x=wide.columns,
                y=labels,
                colorscale=[[0, "#E3F1EC"], [0.25, "#9AD9BF"], [0.5, "#F4D58D"], [0.75, "#E8946A"], [1, "#9A3412"]],
                colorbar=dict(title="Weeks", thickness=12, outlinewidth=0),
                hovertemplate="%{y}<br>%{x|%b %Y}: %{z:.1f} weeks<extra></extra>",
                xgap=1,
                ygap=1,
            )
        )
        layout = base_layout("Estimated weeks to a car-test invite (sorted by latest month)", "")
        layout["hovermode"] = "closest"
        heat.update_layout(**layout, height=max(520, 20 * len(wide) + 120))
        heat.update_xaxes(tickformat="%b<br>%Y", dtick="M6")
        heat.update_yaxes(tickfont=dict(size=11))
        st.plotly_chart(heat, **FULL_WIDTH)
        st.caption("Each row is a county, each column a month. Darker means a longer wait. Co. Cork and Ireland are in bold.")

    with race_tab:
        frame = waiting.dropna(subset=["weeks"]).copy()
        frame = frame[frame["period"].dt.month.isin([1, 4, 7, 10]) | (frame["period"] == frame["period"].max())]
        frame["month"] = frame["period"].dt.strftime("%b %Y")
        frame["group"] = frame["county"].map(
            lambda c: "Co. Cork" if c == FOCUS_COUNTY else "National" if c == NATIONAL_COUNTY else "Other counties"
        )
        order = wide.index.tolist()  # same order as the heatmap: shortest wait at the bottom
        frame["county"] = pd.Categorical(frame["county"], categories=order, ordered=True)
        frame = frame.sort_values(["period", "county"])
        race = px.bar(
            frame,
            x="weeks",
            y="county",
            color="group",
            orientation="h",
            animation_frame="month",
            range_x=[0, float(frame["weeks"].max()) * 1.08],
            color_discrete_map={"Co. Cork": CORK_COLOR, "National": NATIONAL_COLOR, "Other counties": "#9FB4C7"},
            category_orders={"county": order[::-1], "group": ["Co. Cork", "National", "Other counties"]},
            labels={"weeks": "Weeks", "county": "", "group": ""},
            hover_data={"weeks": ":.1f", "month": False, "group": False},
        )
        layout = base_layout("Waiting time by county, quarter by quarter (press ▶)", "")
        layout["hovermode"] = "closest"
        layout.pop("yaxis")
        layout.pop("xaxis")
        race.update_layout(**layout, height=max(560, 20 * len(order) + 160))
        race.update_xaxes(gridcolor="#eeeae4", title="Weeks")
        race.update_yaxes(tickfont=dict(size=11))
        if race.layout.updatemenus:
            race.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 650
            race.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 450
        if race.layout.sliders:
            race.layout.sliders[0].currentvalue.prefix = ""
            race.layout.sliders[0].active = len(race.frames) - 1
            # Show the latest month first; pressing play restarts from the beginning.
            last = race.frames[-1]
            for trace, data in zip(race.data, last.data):
                trace.x, trace.y = data.x, data.y
        st.plotly_chart(race, **FULL_WIDTH)
        st.caption("Press ▶ to watch waiting times change from Sep 2021 to the latest month. Order is fixed by the latest month.")


# --------------------------------------------------------------------------- #
# ROA32 centres
# --------------------------------------------------------------------------- #
def render_centres(activity: pd.DataFrame) -> None:
    statistics = sorted(activity["statistic"].unique())
    categories = sorted(activity["category"].unique())
    real_centres = sorted(c for c in activity["centre"].unique() if c != ALL_CENTRES)
    cork_centres = [c for c in real_centres if c.endswith(", Co. Cork")]

    filters = st.columns([1.3, 1.3, 1])
    with filters[0]:
        default_stat = APPLICATIONS_STATISTIC if APPLICATIONS_STATISTIC in statistics else statistics[0]
        statistic = st.selectbox("Measure", statistics, index=statistics.index(default_stat))
    with filters[1]:
        default_cat = CAR_CATEGORY if CAR_CATEGORY in categories else categories[0]
        category = st.selectbox("Test category", categories, index=categories.index(default_cat))
    with filters[2]:
        scope = st.radio("Centres", ["Co. Cork", "All centres", "Choose…"], horizontal=True)

    if scope == "Co. Cork":
        centres = cork_centres or real_centres
    elif scope == "All centres":
        centres = real_centres
    else:
        centres = st.multiselect(
            "Driving test centres",
            options=real_centres,
            default=cork_centres,
            placeholder="Choose one or more centres",
        )

    months = month_options(activity["period"])
    default_start = months[max(0, len(months) - 12)]
    start, end = st.select_slider(
        "Month range",
        options=months,
        value=(default_start, months[-1]),
        format_func=format_month,
        key="roa32_months",
    )

    if not centres:
        st.info("Choose at least one driving test centre.")
        return

    scoped = activity[(activity["statistic"] == statistic) & (activity["category"] == category)]
    scoped = filter_months(scoped, start, end)
    centre_frame = scoped[scoped["centre"].isin(centres)].dropna(subset=["value"])
    if centre_frame.empty:
        st.warning(
            "Every matching cell is blank in the source file, so there is nothing to chart. "
            "Try another category or a wider month range."
        )
        return

    history = centre_frame  # full month-by-month series for the line chart
    is_stock = "month end" in statistic.lower()
    if is_stock:
        # Stocks (waiting, scheduled…) are snapshots: summing months double-counts people.
        # Use one common month so closed venues don't contribute stale figures.
        snapshot = centre_frame["period"].max()
        centre_frame = centre_frame[centre_frame["period"] == snapshot]
        totals = centre_frame[["centre", "value"]]
        value_label = f"End of {format_month(snapshot)}"
    else:
        totals = centre_frame.groupby("centre", as_index=False, observed=True)["value"].sum()
        value_label = "Total in range"
    totals = totals.sort_values("value", ascending=False).reset_index(drop=True)

    unit = centre_frame["unit"].iloc[0] or "Number"
    official = scoped[scoped["centre"] == ALL_CENTRES].dropna(subset=["value"])
    if is_stock:
        official = official[official["period"] == snapshot]
        national_total = float(official["value"].iloc[0]) if not official.empty else None
    elif not official.empty:
        national_total = float(official["value"].sum())
    else:
        national_total = None

    selection_total = float(totals["value"].sum())
    cards = st.columns(4)
    cards[0].metric(f"{value_label}, selected", f"{selection_total:,.0f}")
    cards[1].metric(
        "Share of national",
        "—" if not national_total else f"{selection_total / national_total:.1%}",
        help="Against the published all-centres figure for the same measure and category.",
    )
    cards[2].metric("Busiest centre", totals.iloc[0]["centre"].split(",")[0], help=f"{totals.iloc[0]['value']:,.0f}")
    cards[3].metric("Centres with data", f"{len(totals)}")

    colors = [CORK_COLOR if c.endswith(", Co. Cork") else ACCENT for c in totals["centre"]]
    bar = go.Figure(
        go.Bar(
            x=totals["value"],
            y=totals["centre"],
            orientation="h",
            marker=dict(color=colors),
            hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>",
        )
    )
    bar_layout = base_layout(f"{statistic} · {category}", "")
    bar_layout["hovermode"] = "closest"
    bar.update_layout(**bar_layout, height=max(360, 26 * len(totals) + 140), showlegend=False)
    bar.update_xaxes(title=f"{value_label} ({unit})", showgrid=True, gridcolor="#eeeae4")
    bar.update_yaxes(autorange="reversed", title="")
    st.plotly_chart(bar, **FULL_WIDTH)
    if scope != "Co. Cork":
        st.caption("Green bars are Co. Cork centres.")

    if len(totals) <= 12:
        line = go.Figure()
        for index, centre in enumerate(totals["centre"]):
            subset = history[history["centre"] == centre].sort_values("period")
            line.add_trace(
                go.Scatter(
                    x=subset["period"],
                    y=subset["value"],
                    name=centre.replace(", Co. Cork", ""),
                    mode="lines+markers",
                    marker=dict(size=4),
                    line=dict(width=2.2, color=SERIES_COLORS[index % len(SERIES_COLORS)]),
                    hovertemplate="%{y:,.0f}<extra>" + centre + "</extra>",
                )
            )
        line.update_layout(**base_layout("Month by month", unit))
        line.update_xaxes(tickformat="%b\n%Y")
        st.plotly_chart(line, **FULL_WIDTH)
    else:
        st.caption("The month-by-month chart appears when 12 or fewer centres are selected.")

    if category == ALL_CATEGORIES:
        st.caption(
            "“All Test Categories” is the published aggregate. It is not the sum of the "
            "category rows, which can contain blank cells."
        )

    display = totals.rename(columns={"centre": "Driving test centre", "value": f"{value_label} ({unit})"})
    with st.expander("Table and download"):
        st.dataframe(display, **FULL_WIDTH, hide_index=True)
        st.download_button(
            "Download as CSV",
            data=display.to_csv(index=False).encode("utf-8"),
            file_name="roa32_centre_summary.csv",
            mime="text/csv",
        )


# --------------------------------------------------------------------------- #
# ROA05 history
# --------------------------------------------------------------------------- #
def render_history(annual: pd.DataFrame) -> None:
    statistics = list(dict.fromkeys(annual["statistic"].tolist()))
    chosen = st.selectbox(
        "Statistic",
        statistics,
        index=next((i for i, s in enumerate(statistics) if "applications" in s.lower()), 0),
    )
    series = annual[annual["statistic"] == chosen].dropna(subset=["value"]).sort_values("year")
    if series.empty:
        st.info(f"“{chosen}” has no published numbers in this extract.")
        return

    unit = str(series["unit"].iloc[0] or "")
    is_count = unit.lower() == "number"
    value_fmt = ",.0f" if is_count else ",.1f"
    latest = series.iloc[-1]
    peak = series.loc[series["value"].idxmax()]
    low = series.loc[series["value"].idxmin()]

    cards = st.columns(4)
    previous = series.iloc[-2] if len(series) > 1 else None
    cards[0].metric(
        f"{int(latest['year'])}",
        format(latest["value"], value_fmt),
        delta=None if previous is None else format(latest["value"] - previous["value"], "+" + value_fmt),
        delta_color="off",
    )
    cards[1].metric(f"Peak ({int(peak['year'])})", format(peak["value"], value_fmt))
    cards[2].metric(f"Low ({int(low['year'])})", format(low["value"], value_fmt))
    cards[3].metric("Median", format(series["value"].median(), value_fmt))

    fig = go.Figure(
        go.Bar(
            x=series["year"],
            y=series["value"],
            marker=dict(color=CORK_COLOR if is_count else ACCENT),
            hovertemplate="%{x}<br>%{y:" + value_fmt + "}<extra></extra>",
        )
    )
    layout = base_layout(f"{chosen} (national)", unit or "Value")
    layout["hovermode"] = "closest"
    fig.update_layout(**layout, showlegend=False)
    fig.update_xaxes(dtick=1, title="")
    st.plotly_chart(fig, **FULL_WIDTH)

    with st.expander("All annual figures"):
        table = annual.pivot(index="year", columns="statistic", values="value").sort_index()
        st.dataframe(table, **FULL_WIDTH)


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #
wait_tab, centre_tab, history_tab = st.tabs(
    ["Waiting times · ROA37", "Applications by centre · ROA32", "Historical trend · ROA05"]
)

with wait_tab:
    waiting = safe_load(cached_waiting_times, "Waiting times (ROA37)")
    if waiting is not None:
        render_gauges(waiting)
        render_waiting(waiting)
        st.divider()
        render_visual_explorer(waiting)

with centre_tab:
    activity = safe_load(cached_centre_activity, "Centre activity (ROA32)")
    if activity is not None:
        render_centres(activity)

with history_tab:
    annual = safe_load(cached_annual_series, "Annual series (ROA05)")
    if annual is not None:
        render_history(annual)

with st.sidebar:
    st.caption("Files loaded")
    for frame in (waiting, activity, annual):
        if frame is not None and not frame.empty:
            st.code(frame["source_file"].iloc[0], language=None)
