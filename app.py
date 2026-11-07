"""Irish Driving Test & EDT Master Hub (Cork & National).

Run from this folder:

    streamlit run app.py

Pages live in views/. Shared styling and cached data loading are in ui.py,
the CSV parsing is in data_loader.py, and the learning content is in content.py.
"""

from __future__ import annotations

import streamlit as st

from content import LINKS
from ui import apply_theme

st.set_page_config(
    page_title="Irish Driving Test & EDT Master Hub",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Start here": [
        st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    ],
    "Prepare": [
        st.Page("views/routes.py", title="Test Routes & Centre (Cork)", icon=":material/route:", url_path="routes"),
        st.Page("views/instructors.py", title="ADI Directory", icon=":material/school:", url_path="instructors"),
    ],
    "Data": [
        st.Page("views/analytics.py", title="Waiting Times & Analytics", icon=":material/monitoring:", url_path="analytics"),
    ],
}


def render_sidebar_footer() -> None:
    with st.sidebar:
        st.divider()
        st.caption("Official services")
        for label, url in LINKS.items():
            st.markdown(f"- [{label}]({url})")
        st.caption(
            "Data: CSO / RSA tables ROA37, ROA32 and ROA05. "
            "Route maps and checks: Wilton Test Pack v3.1."
        )


def main() -> None:
    apply_theme()
    navigation = st.navigation(PAGES)
    render_sidebar_footer()
    navigation.run()


if __name__ == "__main__":
    main()
