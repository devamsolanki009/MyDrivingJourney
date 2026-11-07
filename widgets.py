"""Custom HTML / CSS / JavaScript components embedded in the Streamlit pages.

Each widget is a self-contained template in static/. Python fills the
`__DATA__` placeholder with JSON and the shared `/*__BASE_CSS__*/` block with
static/widget_base.css, then renders it in a sandboxed iframe via
streamlit.components.v1.html. Nothing is fetched from the network except
Google Fonts.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _read(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def _to_json(data) -> str:
    # "</" would let data close the <script> tag early.
    return json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")


def _render(template: str, data, height: int) -> None:
    html = (
        _read(template)
        .replace("/*__BASE_CSS__*/", _read("widget_base.css"))
        .replace("__DATA__", _to_json(data))
    )
    # st.iframe replaces components.v1.html in newer Streamlit; keep the old call for 1.4x.
    # The HTML is our own template plus JSON-encoded data, never user input.
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=False)


def inject_theme() -> None:
    """Global page styling and entrance animations."""
    st.markdown(f"<style>{_read('theme.css')}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str, tag: str, stats: list[dict], footnote: str = "") -> None:
    """Animated banner with count-up stats.

    stats: [{"label", "value" (number or None), "decimals", "suffix", "note", "tone"}]
    tone is one of "up", "down", "neutral" and colours the note.
    """
    _render(
        "hero.html",
        {"title": title, "subtitle": subtitle, "tag": tag, "stats": stats, "footnote": footnote},
        height=470,
    )


def edt_tracker(lessons: list[tuple[int, str, str]]) -> None:
    """Clickable 12-lesson tracker with a progress ring (saved in the browser)."""
    data = [{"n": n, "title": title, "focus": focus} for n, title, focus in lessons]
    _render("edt_tracker.html", {"lessons": data}, height=620)


def manoeuvre_simulator(name: str) -> None:
    """Animated top-down simulation of a test manoeuvre."""
    _render("manoeuvre.html", {"name": name}, height=540)


def flashcards(cards: list[tuple[str, str]]) -> None:
    """3D flip cards for rules-of-the-road questions."""
    data = [{"q": q, "a": a} for q, a in cards]
    _render("flashcards.html", {"cards": data}, height=380)
