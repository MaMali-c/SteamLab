"""CSV values remain in the original PDF units; conversion is explicit."""

import csv
from dataclasses import dataclass
from pathlib import Path

from steamlab.core.errors import InputError
from steamlab.core.units import finite_number, volume_to_m3kg


@dataclass(frozen=True)
class TableRow:
    row_id: str
    kind: str
    temperature_c: float
    pressure_kpa: float
    quality: float | None
    v_cm3_g: float
    u: float
    h: float
    s: float
    page: int
    table_id: str
    review_status: str

    @property
    def properties(self) -> dict[str, float]:
        return {"v": volume_to_m3kg(self.v_cm3_g, "cm³/g"), "u": self.u, "h": self.h, "s": self.s}


def load_rows(path: Path) -> tuple[TableRow, ...]:
    rows, seen = [], set()
    with path.open(encoding="utf-8", newline="") as file:
        for record in csv.DictReader(file):
            if record["review_status"] != "visually_checked":
                continue
            row = TableRow(
                row_id=record["row_id"],
                kind=record["kind"],
                temperature_c=finite_number(record["temperature_c"], "T"),
                pressure_kpa=finite_number(record["pressure_kpa"], "P"),
                quality=None if record["quality"] == "" else finite_number(record["quality"], "x"),
                v_cm3_g=finite_number(record["v_cm3_g"], "v"),
                u=finite_number(record["u"], "u"),
                h=finite_number(record["h"], "h"),
                s=finite_number(record["s"], "s"),
                page=int(record["page"]),
                table_id=record["table_id"],
                review_status=record["review_status"],
            )
            key = (row.kind, row.temperature_c, row.pressure_kpa, row.quality)
            if key in seen or row.row_id in {r.row_id for r in rows}:
                raise InputError("Duplicate source record.", "رکورد مرجع تکراری است.")
            if row.v_cm3_g <= 0 or row.pressure_kpa <= 0 or row.page < 1:
                raise InputError("Invalid source record.", "رکورد مرجع نامعتبر است.")
            if row.kind not in {"saturation", "superheated"}:
                raise InputError("Unsupported source region.", "نوع جدول پشتیبانی نمی‌شود.")
            if (row.kind == "saturation" and row.quality not in (0, 1)) or (
                row.kind == "superheated" and row.quality is not None
            ):
                raise InputError(
                    "Invalid quality in source record.", "کیفیت رکورد مرجع نامعتبر است."
                )
            seen.add(key)
            rows.append(row)
    return tuple(rows)
