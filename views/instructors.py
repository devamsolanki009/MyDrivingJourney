"""Approved Driving Instructor (ADI) directory for County Cork."""

from __future__ import annotations

from html import escape
from urllib.parse import quote_plus

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from content import ADI_DIRECTORY
from ui import FULL_WIDTH, CORK_COLOR, page_header

page_header(
    "County Cork",
    "Approved Driving Instructors (ADI)",
    "Instructors and teams from the project's ADI directory, sorted by area. "
    "Check that any instructor is on the RSA's ADI register before you book EDT lessons.",
)

directory = pd.DataFrame(ADI_DIRECTORY).sort_values("area").reset_index(drop=True)
directory["search"] = directory.apply(
    lambda r: "https://www.google.com/search?q="
    + quote_plus(f"{r['instructor']} driving instructor {r['area']} Cork"),
    axis=1,
)

# --------------------------------------------------------------------------- #
# Filters
# --------------------------------------------------------------------------- #
f1, f2, f3 = st.columns([1.6, 1.2, 1])
with f1:
    query = st.text_input("Search", placeholder="Name, area or service, e.g. automatic")
with f2:
    transmission = st.selectbox(
        "Lessons in",
        ["Any", "Manual", "Automatic"],
        help="Entries marked 'Not stated' are hidden when you pick Manual or Automatic.",
    )
with f3:
    st.write("")
    edt_only = st.toggle("EDT listed", help="Only show entries that list the 12-lesson EDT programme.")

view = directory.copy()
if query:
    text = (view["area"] + " " + view["instructor"] + " " + view["services"] + " " + view["transmission"]).str.lower()
    view = view[text.str.contains(query.strip().lower(), regex=False)]
if transmission != "Any":
    view = view[view["transmission"].str.contains(transmission, case=False)]
if edt_only:
    view = view[view["edt"]]

st.caption(f"{len(view)} of {len(directory)} entries")

if view.empty:
    st.info("No instructors match those filters.")
else:
    def initials(name: str) -> str:
        parts = [w for w in name.replace("&", " ").split() if w[:1].isalpha()]
        return "".join(w[0] for w in parts[:2]).upper()

    per_row = 3
    records = view.to_dict("records")
    for start in range(0, len(records), per_row):
        cols = st.columns(per_row)
        for column, r in zip(cols, records[start : start + per_row]):
            tags = f'<span>{escape(r["transmission"])}</span>' + ('<span class="edt">EDT</span>' if r["edt"] else "")
            column.markdown(
                f"""<div class="adi-card">
                    <div class="avatar">{escape(initials(r["instructor"]))}</div>
                    <div class="area">{escape(r["area"])}</div>
                    <h4>{escape(r["instructor"])}</h4>
                    <p>{escape(r["services"])}</p>
                    <div class="tags">{tags}</div>
                    <a href="{escape(r["search"])}" target="_blank" rel="noopener">Look up online ↗</a>
                </div>""",
                unsafe_allow_html=True,
            )
        st.write("")

    map_col, table_col = st.columns([1.3, 1], gap="large")
    with map_col:
        fig = go.Figure(
            go.Scattermap(
                lat=view["lat"],
                lon=view["lon"],
                mode="markers+text",
                marker=dict(size=16, color=CORK_COLOR, opacity=0.9),
                text=view["area"],
                textposition="top right",
                textfont=dict(size=12, color="#1A2332"),
                customdata=view[["instructor", "services"]],
                hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
            )
        )
        centre_lat = float(view["lat"].mean()) if len(view) else 51.95
        centre_lon = float(view["lon"].mean()) if len(view) else -8.45
        fig.update_layout(
            map=dict(style="open-street-map", center=dict(lat=centre_lat, lon=centre_lon), zoom=8.3 if len(view) > 1 else 10.5),
            margin=dict(l=0, r=0, t=0, b=0),
            height=420,
        )
        st.plotly_chart(fig, **FULL_WIDTH)
        st.caption("Pins mark the area served, not a business address.")
    with table_col:
        with st.expander("Table view", expanded=True):
            st.dataframe(
                view[["area", "instructor", "transmission", "edt", "search"]],
                hide_index=True,
                **FULL_WIDTH,
                column_config={
                    "area": "Area",
                    "instructor": "Instructor / team",
                    "transmission": "Transmission",
                    "edt": st.column_config.CheckboxColumn("EDT"),
                    "search": st.column_config.LinkColumn("Look up", display_text="Search ↗"),
                },
            )

st.divider()
st.markdown("**Choosing an ADI**")
st.markdown(
    "- Your first car learner permit means you must do EDT. Make sure the instructor is RSA-approved and can record lessons on My EDT.\n"
    "- Ask whether lessons start from your home, college or work, and whether they cover the Wilton test routes.\n"
    "- If you plan to test in an automatic, note that an automatic test leads to an automatic-only licence.\n"
    "- Agree the price of a pre-test lesson and the use of the instructor's car on test day before you book."
)
st.link_button("RSA website: find an Approved Driving Instructor", "https://www.rsa.ie")
