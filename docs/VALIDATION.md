# Validation Record (گزارش اعتبارسنجی)

## Executed environment (محیط اجرای واقعی)

- Date: 2026-11-03.
- Python 3.12.14, Linux x86_64.
- iapws 1.5.5; Streamlit 1.66.1.
- The exact installed package snapshot is `requirements-tested.txt`.
- Tests were executed, not merely written. macOS execution is not claimed.
- GitHub Actions configuration is supplied but has not run remotely.

## Automated checks (بررسی‌های خودکار)

The release test run is captured in `test-results.xml`. Its coverage includes:

**103 tests passed** in the completed local run. The 51 reference comparisons below
are scalar comparisons grouped inside some tests, not 51 additional pytest tests.

| Group | Evidence |
|---|---|
| Official states | 12 fixed states across regions 1, 2, 3 and 5; four properties each |
| Saturation | 3 published Tsat checkpoints, inverse boundaries, endpoints and mixtures |
| Input safety | Domain edges, invalid pressure/temperature/quality, NaN/infinity, missing x |
| Physical semantics | Phase vs equation region, undefined single-phase x, critical-point handling |
| Units | kPa/MPa/bar/Pa consistency and cm³/g conversion |
| Table algorithm | Exact nodes, T interpolation, P interpolation, saturation mixture |
| Data refusal | Unchecked rows, duplicate rows, missing coverage and no extrapolation |
| Streamlit | Empty state, real calculation, stale result, invalid state, unit changes, reset |
| Bilingual interface | Main widget/metric labels include Persian in parentheses |

`python scripts/validate.py` records **51/51 scalar reference checks passed** in
`validation/official-results.csv`. Fixed expected values are stored in
`data/verified/official_checks.json` with the official table number.

Source: IAPWS R7-97(2012), tables **5, 15, 33, 36, 42**.
[Official release](https://iapws.org/technical-guidance/release/IF97-Rev).

Relative tolerance is `1e-8` for regions 1/2/5 and saturation temperature,
with a `1e-10` absolute floor on state properties. Region 3 uses `1e-7` because
the published density-based checkpoint is exercised through TP with rounded
published pressure. These tolerances test reproducibility of published numbers,
not physical uncertainty across the entire IF97 domain.

The independent mixture-identity tests allow `2e-5` relative discrepancy for the
backend's region-3 saturation endpoint implementations. The separate energy
identity remains tight. Quality close to the critical point is conservatively guarded.

## PDF comparison (مقایسه با جدول ارسالی)

`validation/pdf-comparison.csv` contains **76 property comparisons** from 19 checked
source records. Maximum observed relative difference in this sample is approximately
**0.135749%**. This is descriptive, not a pass criterion or a bound for other states.
The dataset's formulation is unknown and source values remain unmodified.

The machine-readable environment and totals are in `validation/summary.json`.

## Reproduce (بازتولید)

```bash
python -m pytest -q --junitxml=docs/test-results.xml
python -m ruff check .
python scripts/validate.py
```

The optional PDF checksum test is skipped when the user-supplied PDF is not present,
as on a public Git checkout. It is checked in the personal ZIP.

## Remaining checks (بررسی‌های باقی‌مانده)

The real app was started locally and inspected in Chromium 134 with Playwright.
Desktop screenshots at 1440×1200 were checked in light and dark appearances, including
the actual comparison and source-row section. A fresh mobile viewport at 390×1000
was checked; its main content width matched the viewport without horizontal overflow.
Calculation and appearance changes worked without browser JavaScript errors.
These checks do not establish compatibility with every browser or device.

Direct installation on the user's Mac, independent human verification of the
transcribed PDF sample, and complete-domain numerical validation remain outside
the completed local test run. No chart or Rankine-cycle capability is being claimed.
