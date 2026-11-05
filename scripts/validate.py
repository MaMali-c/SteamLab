"""Generate reference results without changing any reference values."""

import csv
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from steamlab.validation_report import official_report, pdf_report

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    output = ROOT / "docs/validation"
    output.mkdir(parents=True, exist_ok=True)
    official = official_report(ROOT / "data/verified/official_checks.json")
    pdf = pdf_report(ROOT / "data/verified/steam_table_sample.csv")
    write_csv(output / "official-results.csv", official)
    write_csv(output / "pdf-comparison.csv", pdf)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "iapws": importlib.metadata.version("iapws"),
        "streamlit": importlib.metadata.version("streamlit"),
        "official_checks": len(official),
        "official_passed": sum(r["passed"] for r in official),
        "pdf_property_comparisons": len(pdf),
        "max_pdf_relative_difference_percent": max(r["relative_percent"] or 0 for r in pdf),
        "pdf_note": "Comparison only. The PDF source formulation is unknown; no universal pass threshold is asserted.",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if all(r["passed"] for r in official) else 1


if __name__ == "__main__":
    sys.exit(main())
