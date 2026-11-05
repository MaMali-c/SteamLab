from pathlib import Path

import pytest

from steamlab.tables.repository import load_rows

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rows():
    return load_rows(ROOT / "data/verified/steam_table_sample.csv")
