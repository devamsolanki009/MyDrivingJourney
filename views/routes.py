"""Test routes and centre details, focused on the Cork (Wilton) test centre."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from content import (
    BONNET_CHECKS,
    BONNET_IMAGE,
    EXTRA_DIAGRAMS,
    FAULT_GRADES,
    FAULT_GUIDE_IMAGES,
    IN_CAR_CHECKS,
    MANOEUVRES,
    ROUTE_AREAS,
    ROUTES,
    THEORY_QUESTIONS,
    route_image,
)
from widgets import flashcards, manoeuvre_simulator
from ui import (
    FULL_WIDTH,
    CAR_CATEGORY,
    WILTON_CENTRE,
    cached_centre_activity,
    fmt_number,
    format_month,
    page_header,
    safe_load,
)

page_header(
    "Cork focus",
    "Test Routes & Centre Details",
    "Ten practice routes around the Cork (Wilton) test centre, the technical checks the tester "
    "can ask about, and step-by-step guides to the three manoeuvres.",
)


def show_image(path, caption: str | None = None) -> None:
    if path is not None and path.is_file():
        st.image(str(path), caption=caption, **FULL_WIDTH)
    else:
        st.info("Image not found. Run `python scripts/export_assets.py` to rebuild the assets folder.")


routes_tab, centre_tab, checks_tab, manoeuvres_tab, faults_tab = st.tabs(
    ["Test routes 1–10", "Wilton centre", "Technical checks", "Manoeuvres", "Fault grading"]
)

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
with routes_tab:
    st.caption(
        "Maps from the Wilton Test Pack (v3.1). Each route starts and finishes at the test centre. "
        "The letters on each map show where the tester usually asks for a manoeuvre: "
        "**H** hill start, **T** turnabout, **R** reverse around a corner."
    )

    area_filter = st.pills(
        "Show routes through",
        ROUTE_AREAS,
        selection_mode="multi",
        help="Pick one or more areas. Routes that pass through any of them are listed.",
    )
    matching = [
        number
        for number, route in ROUTES.items()
        if not area_filter or set(area_filter) & set(route["areas"])
    ]
    if not matching:
        st.info("No route passes through those areas.")
    else:
        if st.session_state.get("route_choice") not in matching:
            st.session_state["route_choice"] = matching[0]
        choice = st.segmented_control(
            "Route",
            matching,
            format_func=lambda n: f"Route {n}",
            key="route_choice",
        )
        if choice is None:
            choice = matching[0]
        route = ROUTES[choice]

        map_col, info_col = st.columns([1.7, 1], gap="large")
        with map_col:
            show_image(route_image(choice), caption=f"Route {choice}")
        with info_col:
            st.markdown(f"### Route {choice}")
            st.markdown(
                "".join(f'<span class="pill">{area}</span>' for area in route["areas"]),
                unsafe_allow_html=True,
            )
            st.markdown("**Manoeuvre locations**")
            st.markdown(
                f"- **H**ill start: {route['hill']}\n"
                f"- **T**urnabout: {route['turn']}\n"
                f"- **R**everse around a corner: {route['reverse']}"
            )
            st.markdown("**Main roads on the route**")
            st.markdown("\n".join(f"- {road}" for road in route["roads"]))
            st.caption("Road names read from the map. Follow the red line on the map for the exact turns.")

    with st.expander("Which areas does each route cover?"):
        coverage = pd.DataFrame(
            {area: ["●" if area in ROUTES[n]["areas"] else "" for n in ROUTES] for area in ROUTE_AREAS},
            index=[f"Route {n}" for n in ROUTES],
        )
        st.dataframe(coverage, **FULL_WIDTH)

# --------------------------------------------------------------------------- #
# Centre
# --------------------------------------------------------------------------- #
with centre_tab:
    st.subheader("Cork (Wilton) test centre")
    st.markdown(
        "All ten routes leave from the test centre on the Sarsfield Road / Doughcloyne side of Wilton. "
        "They cover Wilton, Bishopstown, Model Farm Road, Glasheen, Togher, Pouladuff and Ballyphehane, "
        "and most use a stretch of the South Ring Road (N40)."
    )
    activity = safe_load(cached_centre_activity, "Centre activity (ROA32)")
    if activity is not None:
        wilton = activity[(activity["centre"] == WILTON_CENTRE) & (activity["category"] == CAR_CATEGORY)]
        wilton = wilton.dropna(subset=["value"])
        if wilton.empty:
            st.info("ROA32 has no car-test figures for Cork (Wilton).")
        else:
            last = wilton["period"].max()
            latest = wilton[wilton["period"] == last].set_index("statistic")["value"]
            st.markdown(f"**Car tests (Category B), {format_month(last)}**")
            cards = st.columns(4)
            for column, (label, stat) in zip(
                cards,
                [
                    ("Applications received", "Driving Test Applications Received"),
                    ("Waiting at month end", "Driving Test Applicants Waiting at Month End"),
                    ("Scheduled at month end", "Driving Test Applicants Scheduled at Month End"),
                    ("Paused at month end", "Driving Test Applicants Paused at Month End"),
                ],
            ):
                column.metric(label, fmt_number(latest.get(stat)))
            st.page_link(
                "views/analytics.py",
                label="Compare Wilton with other centres",
                icon=":material/monitoring:",
            )

    st.markdown("**Tips for test day at Wilton**")
    st.markdown(
        "- Drive the routes at the same time of day as your test, so you see the real traffic.\n"
        "- The N40 slip roads and the Sarsfield Road roundabouts come up on most routes. Practise lane choice there.\n"
        "- Estates such as Greenwood, Woodbrook and Uam Var have parked cars and children. Keep your speed down.\n"
        "- Arrive early and park so you can pull straight out when the tester is ready."
    )

# --------------------------------------------------------------------------- #
# Technical checks
# --------------------------------------------------------------------------- #
with checks_tab:
    st.subheader("Under-bonnet checks")
    st.caption("The tester can ask you to open the bonnet and point to each of these.")
    image_col, list_col = st.columns([1.2, 1], gap="large")
    with image_col:
        show_image(BONNET_IMAGE, caption="Where to find each part (example engine bay)")
    with list_col:
        for name, part, answer in BONNET_CHECKS:
            with st.container(border=True):
                st.markdown(f"**{name}** · {part}")
                st.markdown(f'<span class="note">{answer}</span>', unsafe_allow_html=True)

    st.subheader("In-car and bad-weather questions")
    st.caption("If the weather is poor, these can replace the under-bonnet checks.")
    for question, answer in IN_CAR_CHECKS:
        with st.expander(question):
            st.write(answer)

    st.subheader("Test yourself: rules of the road")
    st.caption("Click the card to flip it. Mark each one so you know what to revise.")
    flashcards(THEORY_QUESTIONS)


# --------------------------------------------------------------------------- #
# Manoeuvres
# --------------------------------------------------------------------------- #
with manoeuvres_tab:
    name = st.radio("Manoeuvre", list(MANOEUVRES), horizontal=True, label_visibility="collapsed")
    guide = MANOEUVRES[name]
    st.subheader(name)
    st.markdown(guide["summary"])
    manoeuvre_simulator(name)
    st.caption("Animated guide: press Play, or click any step to jump to it. Not to scale.")

    st.markdown("#### Step by step")
    text_col, image_col = st.columns([1.2, 1], gap="large") if guide["image"] else (st.container(), None)
    with text_col:
        for stage, points in guide["steps"]:
            st.markdown(f"**{stage}**")
            st.markdown("\n".join(f"{i}. {p}" for i, p in enumerate(points, start=1)))
        st.markdown("**What the tester looks for**")
        st.markdown("\n".join(f"- {p}" for p in guide["key_points"]))
    if image_col is not None:
        with image_col:
            show_image(guide["image"], caption="Diagram from the manoeuvres guide")

    st.caption("P.O.M. = prepare, observe, move. M.S.M. = mirror, signal, manoeuvre.")
    with st.expander("More diagrams: roundabouts and hand signals"):
        cols = st.columns(len(EXTRA_DIAGRAMS))
        for column, (label, path) in zip(cols, EXTRA_DIAGRAMS.items()):
            with column:
                show_image(path, caption=label)

# --------------------------------------------------------------------------- #
# Fault grading
# --------------------------------------------------------------------------- #
with faults_tab:
    st.subheader("How the tester grades faults")
    grade_cols = st.columns(3)
    for column, (grade, label, rule, color) in zip(grade_cols, FAULT_GRADES):
        column.markdown(
            f'<div class="grade" style="border-color:{color}"><b>{grade} · {label}</b><br>'
            f'<span class="note">{rule}</span></div>',
            unsafe_allow_html=True,
        )
    st.caption("The exact pass/fail thresholds are published by the RSA at rsa.ie.")
    page = st.radio(
        "Guideline page",
        [1, 2, 3],
        format_func=lambda n: f"Page {n}",
        horizontal=True,
    )
    show_image(FAULT_GUIDE_IMAGES[page - 1])
