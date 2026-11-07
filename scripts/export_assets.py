"""Export the route maps and diagrams used by the app from the reference PDFs.

The app itself only needs the JPEGs in assets/, so PyMuPDF is a one-off
dependency for this script and is not in requirements.txt.

    pip install pymupdf
    python scripts/export_assets.py
"""

from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# (source pdf, zero-based page, output path)
EXPORTS = [
    *[("Test-Route-Pack-New.pdf", page, f"routes/route_{page - 1:02d}.jpg") for page in range(2, 12)],
    ("Test-Route-Pack-New.pdf", 19, "checks/bonnet_locations.jpg"),
    ("Test-Route-Pack-New.pdf", 25, "checks/fault_guidelines_1.jpg"),
    ("Test-Route-Pack-New.pdf", 26, "checks/fault_guidelines_2.jpg"),
    ("Test-Route-Pack-New.pdf", 27, "checks/fault_guidelines_3.jpg"),
    ("Driving test manoeuvres (1) (1)_261107_131652.pdf", 0, "manoeuvres/turn_in_the_road.jpg"),
    ("Driving test manoeuvres (1) (1)_261107_131652.pdf", 1, "manoeuvres/reverse_around_corner.jpg"),
    ("Driving test manoeuvres (1) (1)_261107_131652.pdf", 2, "manoeuvres/roundabouts.jpg"),
    ("Driving test manoeuvres (1) (1)_261107_131652.pdf", 3, "manoeuvres/hand_signals.jpg"),
]


def main() -> None:
    for pdf_name, page, out in EXPORTS:
        target = ASSETS / out
        target.parent.mkdir(parents=True, exist_ok=True)
        with pymupdf.open(ROOT / pdf_name) as doc:
            doc[page].get_pixmap(dpi=110).save(target, jpg_quality=78)
        print(f"{pdf_name} p{page + 1} -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
