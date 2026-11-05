# PDF Data Review (بازبینی داده‌های PDF)

Source: user-supplied `SteamTableSI.pdf`, 19 scanned pages. Page indices below are
1-based positions in the PDF, not inferred book page numbers. The SHA-256 and
review method are recorded in `data/verified/provenance.json`.

## Included sample (نمونه استخراج‌شده)

| PDF page | Table | Included coordinates | Records |
|---|---|---|---:|
| 1 | F.1 saturated steam | 20, 25, 30 °C; liquid and vapor endpoints | 6 |
| 5 | F.2 superheated steam | 100 kPa; 300, 350 °C | 2 |
| 6 | F.2 superheated steam | 500 kPa; 200, 220, 240, 260, 280, 300 °C | 6 |
| 7 | F.2 superheated steam | 500 kPa; 325, 350 °C | 2 |
| 9 | F.2 superheated steam | 750 kPa; 350, 375, 400 °C | 3 |

Total: **19 records**, four properties each. This is not a full OCR extraction.
Text extraction returned no usable table text. Values were visually transcribed
from enlarged page renders and cross-checked visually by the assistant. No
independent human double-entry audit has been performed. The status
`visually_checked` records that specific review level, not laboratory certification.

## Column interpretation (معنای ستون‌ها)

- `sat. liq.`: saturated-liquid property f.
- `sat. vap.`: saturated-vapor property g.
- `evap.`: vapor-minus-liquid difference fg, not the saturated-vapor value.
- V is in **cm³/g**, not m³/kg. Conversion multiplier is **0.001**.
- U and H are in kJ/kg; S is in kJ/(kg K); P is in kPa.
- Dotted/unavailable cells are not numeric and are not entered as zero.
- For F.2, properties appear as V/U/H/S rows within each pressure block;
  temperatures are column headers. The record identity preserves both coordinates.

The loader rejects duplicate coordinates, duplicate IDs, invalid kind/quality,
non-finite numeric cells and nonpositive volume or pressure. Unreviewed rows
are excluded rather than silently trusted.

## Adding records (افزودن رکورد)

1. Retain the source PDF and its hash.
2. Render the desired page at sufficient resolution; inspect units and headers first.
3. Transcribe all four properties, coordinate values, phase branch and page.
4. Compare the entered record visually with the page a second time, preferably by
   another person. Leave uncertain values out; do not estimate unreadable digits.
5. Run comparison against IF97 to flag suspicious values, but never rewrite the
   PDF values merely to force agreement. Reopen the source to resolve discrepancies.
6. Record the actual review level in provenance and update coverage documentation.
7. Run tests and `python scripts/validate.py`.

## Checks versus accuracy (بررسی و دقت)

The separate `pdf-comparison.csv` reports 76 property differences. Saturation
endpoint comparisons use identical T, because the PDF P and T are rounded and
may come from a different formulation. They must not both be submitted as an
exact modern IF97 saturation pair.

The largest observed percentage is reported without defining a pass threshold.
It does not bound interpolation error, unread data, or the remainder of the PDF.
The raw PDF is included only in this personal deliverable and is ignored by Git.
