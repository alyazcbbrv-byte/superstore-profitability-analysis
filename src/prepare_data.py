"""
Clean the course CSV "SampleSuperstore.csv" into data/superstore.csv.

    python src/prepare_data.py "path/to/SampleSuperstore.csv"

- snake_case column names, drops the constant `country` column
- checks: no missing values, ranges, profit never exceeds sales
- exact duplicate rows are KEPT (the file has no order id, so identical lines can be genuine repeat purchases); the count is reported
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "superstore.csv"


def main(src: str) -> int:
    df = pd.read_csv(src, encoding="latin1")
    df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    assert df.country.nunique() == 1
    df = df.drop(columns="country")
    checks = {
        "no missing values": df.isna().sum().sum() == 0,
        "sales positive": (df.sales > 0).all(),
        "quantity positive": (df.quantity > 0).all(),
        "discount within 0-0.8": df.discount.between(0, 0.8).all(),
        "profit never exceeds sales": (df.profit <= df.sales).all(),
        "each sub_category belongs to one category": df.groupby("sub_category").category.nunique().max() == 1,
    }
    for k, ok in checks.items():
        print(("OK   " if ok else "FAIL ") + k)
    if not all(checks.values()):
        return 1
    print(f"note: {df.duplicated().sum()} exact duplicate rows kept (no order id in the file)")
    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} rows -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
