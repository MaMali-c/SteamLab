# SteamLab — Thermodynamic Properties & Analysis Platform

**SteamLab** یک داشبورد تعاملی برای محاسبه و بررسی خواص ترمودینامیکی آب و بخار است. رابط دوزبانهٔ فارسی و انگلیسی دارد و برای تمرین ترمودینامیک و بررسی مثال‌های درسی طراحی شده است.

- با وارد کردن فشار و دما، یا ترکیب فشار یا دما با کیفیت بخار، فاز سیال، آنتالپی، آنتروپی، انرژی داخلی، حجم ویژه و چگالی را محاسبه کنید.
- در بخش «فشار بخار»، تغییرات فشار اشباع با دما را روی نمودار تعاملی ببینید.
- خروجی مدل صنعتی **IAPWS-IF97** را با ۱۹ ردیف نمونه از جدول بخار مقایسه کنید. نمونه‌های جدولی همراه پروژه هستند و فایل PDF مرجع برای اجرای برنامه اختیاری است.

**Example:** At 300 °C and 500 kPa absolute, SteamLab identifies superheated steam and calculates a specific enthalpy of approximately 3,064.6 kJ/kg.

**English overview:** SteamLab is a bilingual Streamlit dashboard for water and steam properties. It supports pressure–temperature and saturation calculations, an interactive vapor-pressure curve, and comparisons against a documented sample of steam-table values.

**راهنمای فارسی:** [START_HERE_FA.md](START_HERE_FA.md)

## Quick start (شروع سریع)

Install Python 3.12 from [python.org](https://www.python.org/downloads/macos/)
if you do not already have Python 3.11 or newer. Open Terminal in this folder:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m streamlit run app.py
```

Open **http://localhost:8501**. Stop with **Ctrl+C**. Later launches need only:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

No account or API key is required. Dependencies are downloaded during installation;
normal calculations are local. The reference links require internet access.

## Implemented behavior (رفتار پیاده‌سازی‌شده)

- **Vapor Pressure (نمودار فشار بخار):** interactive saturation-pressure versus
  temperature curve computed with IF97, with a selectable temperature interval
  (0.01–373.946 °C), kPa/MPa/bar units, a logarithmic scale, hover values,
  a selected-temperature marker and a data table. Open it from the sidebar.
- Outputs: `T`, `P`, `v`, `u`, `h`, `s`, density, physical phase, IF97 region and
  quality where defined. English UI labels include Persian translations in parentheses.
- Pressure is absolute. Supported input units: °C/K and kPa/MPa/bar.
- `P–T` states within 0.01 K of the saturation line require a deliberate change
  to `P–x` or `T–x`. Quality has no default and is never inferred from `P,T`.
- Single-phase quality is `None`, even when the underlying library returns 0 or 1.
- Edited inputs mark old results as stale. Failed calculations clear old results.
- Unit changes preserve the physical input value.
- Light/dark appearance and layouts that wrap on narrow screens.
- 19 visually transcribed and checked records from the supplied PDF, with original
  values, units, source page and record identity. This is a **limited teaching sample**.
- Direct lookup or linear interpolation along one available coordinate; saturation
  endpoints are interpolated before mass-weighted mixture calculation. No extrapolation,
  two-dimensional interpolation or compressed-liquid PDF approximation.
- 51 scalar checks against fixed published IF97 reference values, separate from PDF comparison.

## Example (مثال)

At **300 °C and 500 kPa absolute**:

| Property | IF97 result |
|---|---:|
| Phase | Superheated vapor (بخار فوق‌گرم) |
| Region | 2 |
| v | 0.5226027676 m³/kg |
| u | 2803.294836 kJ/kg |
| h | 3064.596220 kJ/kg |
| s | 7.461447777 kJ/(kg·K) |
| x | Undefined (تعریف نمی‌شود) |

The PDF's page 6 reports `h = 3064.8 kJ/kg` and `v = 522.58 cm³/g`.
Those printed values remain unchanged; the interface converts volume by `× 0.001`
and displays the difference. Agreement is not forced.

## Scientific scope (دامنه علمی)

The engine uses `iapws==1.5.5`. Reference: [IAPWS R7-97(2012)](https://iapws.org/technical-guidance/release/IF97-Rev).
It is an implementation of the industrial formulation, not an IAPWS-certified product.

Software limits:

- `273.16 ≤ T ≤ 1073.15 K`, up to `100 MPa`.
- `1073.15 < T ≤ 2273.15 K`, up to `50 MPa`.
- Minimum TP pressure: `0.000611212677444 MPa`, matching the pinned solver.
- The 273.15–273.16 K strip is intentionally excluded to avoid sub-triple-point
  phase-stability ambiguity; this is a software restriction, not the IF97 lower temperature limit.
- Quality input requires a subcritical saturated state. The final `0.01 K` below
  the critical temperature is excluded from quality mode because the endpoints coalesce.
  The exact critical point is supported in TP mode, with quality undefined.
- No ice, saline water, selectable metastable phases or chemical dissociation.
- The PDF's bibliographic origin/formulation is unknown. Its differences are not
  presented as certified IF97 errors. A visually checked record is not an independent human audit.

Full details: [technical design](docs/TECHNICAL.md),
[data protocol](docs/DATA_REVIEW.md), [validation](docs/VALIDATION.md).

## Tests (تست‌ها)

```bash
python -m pytest -q
python -m ruff check .
python scripts/validate.py
```

The validation script writes numerical results to `docs/validation/`.
The supplied `docs/test-results.xml` records the actual local test run.
Tests cover official points, saturation, region 3, critical behavior, invalid inputs,
conversions, interpolation, traceability, missing data and Streamlit interactions.

The GitHub Actions workflow is configured for Linux/macOS and Python 3.11–3.13.
Its presence does **not** mean those remote jobs have run. See `docs/VALIDATION.md`
for the actual environment tested.

## Architecture (معماری)

| Module | Responsibility |
|---|---|
| `core/engine.py` | Isolated, validated IF97 adapter |
| `core/phase.py` | Physical phase labels independent of equation regions |
| `core/validation.py` | Input limits and numerical guard policy |
| `core/units.py` | Explicit conversions without premature rounding |
| `tables/` | Checked source records, interpolation and differences |
| `ui/` | Bilingual Streamlit presentation and session state |
| `validation_report.py` | Fixed reference checks and PDF comparisons |
| `plots/` | IF97 vapor-pressure curve data and interactive Altair chart |

To use the engine separately:

```python
from steamlab.core.engine import solve_pt, solve_px

state = solve_pt(temperature_k=573.15, pressure_mpa=0.5)
print(state.h, state.phase, state.quality)
mixture = solve_px(pressure_mpa=0.5, quality=0.4)
print(mixture.v)
```

The wheel installs the Python package. To run the dashboard, retain the source
folder with `app.py`, `.streamlit/`, `data/` and `docs/`, and start from that folder.
`requirements-tested.txt` records the exact tested environment; it is an environment
snapshot, not a promise of binary-wheel support on every historical macOS version.

## Roadmap (نقشه راه)

- V1.1: P–h/P–s, real Plotly T–s/P–h diagrams, two-dimensional interpolation,
  CSV export and expanded checked source coverage.
- V1.2: multi-state comparison, turbine/pump/boiler/condenser calculations, Rankine cycle.
- V2: PDF/Excel reports.

These are **not implemented** in V1.0. Plotly is intentionally not installed yet.

## Git and source material (گیت و منابع)

The personal ZIP includes the supplied PDF for offline reference. The PDF is excluded
by `.gitignore`; the source extract does not establish redistribution rights.
The software works without the PDF because the checked sample has its own provenance.
The original dashboard artwork is not redistributed as application code.

The project has not been published to GitHub. After checking the files and setting
your Git identity, you can initialize a repository as described in the Persian guide.
See `NOTICE.md` for data and dependency attribution. No open-source license has been
selected on the project owner's behalf.
