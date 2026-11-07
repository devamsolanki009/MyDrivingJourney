# Irish Driving Test & EDT Master Hub (Cork & National)

A multi-page Streamlit app for learner drivers preparing for the RSA car test,
with a focus on the Cork (Wilton) test centre.

| Page | What it shows |
| --- | --- |
| **Home** | Current national and Co. Cork wait, Wilton centre status, Cork centre table, the 12-lesson EDT programme, how the test works |
| **Test Routes & Centre (Cork)** | Wilton routes 1–10 with maps and H/T/R manoeuvre spots, centre figures, under-bonnet checks, a rules-of-the-road quiz, manoeuvre guides, fault grading |
| **ADI Directory** | County Cork instructors by area, with filters and a map |
| **Waiting Times & Analytics** | Co. Cork vs national wait (ROA37) with mean/median/min/max, applications by centre (ROA32), national annual trend (ROA05) |

## Setup

From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

## Files

```
app.py                 entry point and navigation
views/                 one file per page
ui.py                  shared styling, chart defaults, cached data loading
data_loader.py         CSV parsing and cleaning for ROA37 / ROA32 / ROA05
content.py             routes, checks, manoeuvres, EDT and ADI content
assets/                route maps and diagrams exported from the PDFs
scripts/export_assets.py   rebuilds assets/ from the PDFs (needs: pip install pymupdf)
main.py                standalone matplotlib chart of Cork vs national waits
```

## Data

Keep the three CSV files next to `app.py`. If a filename changes, any file whose
name starts with `ROA37`, `ROA32`, or `ROA05` is picked up instead.

The loader tolerates common PxStat export variations: a BOM in the header, quoted
or re-cased column names, `TLIST(M1)` or `Month` labels for dates, and blank or
suppressed values (`..`, `:`, `-`). If a required column is missing, the page shows
which columns it found instead of crashing.
