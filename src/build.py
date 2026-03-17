#!/usr/bin/env python3
"""
Build script: downloads the latest Tesouro Direto CSV and writes
docs/data/tesouro.json, which is consumed by the GitHub Pages site.

Run from the repo root:
    python src/build.py
"""

import json
import datetime
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import pandas as pd

URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)

CSV_PATH  = Path("data/PrecoTaxaTesouroDireto.csv")
JSON_PATH = Path("docs/data/tesouro.json")


def download():
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CSV_PATH.exists():
        mtime = datetime.date.fromtimestamp(CSV_PATH.stat().st_mtime)
        if mtime >= datetime.date.today():
            print(f"CSV already up to date ({mtime}) — skipping download.")
            return
    print("Downloading CSV …")
    urlretrieve(URL, CSV_PATH)
    print(f"Saved to {CSV_PATH}")


def build():
    print("Loading CSV …")
    df = pd.read_csv(CSV_PATH, encoding="latin-1", sep=";", decimal=",")
    df["Data Vencimento"]   = pd.to_datetime(df["Data Vencimento"],   format="%d/%m/%Y")
    df["Data Base"]         = pd.to_datetime(df["Data Base"],         format="%d/%m/%Y")
    df["Taxa Compra Manha"] = pd.to_numeric(df["Taxa Compra Manha"],  errors="coerce")
    df["PU Compra Manha"]   = pd.to_numeric(df["PU Compra Manha"],    errors="coerce")
    print(f"Loaded {len(df):,} records.")

    out = {"updated": str(datetime.date.today()), "titulos": {}}

    for titulo, group in df.groupby("Tipo Titulo"):
        out["titulos"][titulo] = {}
        for ano, sub in group.groupby(group["Data Vencimento"].dt.year):
            sub = (
                sub.dropna(subset=["PU Compra Manha", "Taxa Compra Manha"])
                .sort_values("Data Base")
                .reset_index(drop=True)
            )
            if sub.empty:
                continue
            # YoY: PU_t / PU_{t-365d} - 1, null when less than a year of history
            dates_ns = sub["Data Base"].values
            pu_vals  = sub["PU Compra Manha"].values
            target   = dates_ns - np.timedelta64(365, "D")
            idxs     = np.searchsorted(dates_ns, target, side="left").clip(0, len(dates_ns) - 1)
            gap_days = (np.abs(dates_ns - np.timedelta64(365, "D") - dates_ns[idxs])
                        .astype("timedelta64[D]").astype(float))
            valid    = (gap_days <= 30) & (idxs < np.arange(len(dates_ns)))
            pu_ref   = np.where(valid, pu_vals[idxs], 1.0)  # safe denominator
            yoy_raw  = np.where(valid, (pu_vals / pu_ref - 1) * 100, np.nan)
            # np.isfinite guards against both NaN and Inf (Infinity is not valid JSON)
            yoy      = [None if not np.isfinite(v) else round(float(v), 2) for v in yoy_raw]

            def finite_or_none(v):
                f = float(v)
                return None if not np.isfinite(f) else round(f, 2)

            out["titulos"][titulo][str(ano)] = {
                "dates": sub["Data Base"].dt.strftime("%Y-%m-%d").tolist(),
                "pu":    [finite_or_none(v) for v in sub["PU Compra Manha"]],
                "taxa":  [finite_or_none(v) for v in sub["Taxa Compra Manha"]],
                "yoy":   yoy,
            }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    size_kb = JSON_PATH.stat().st_size / 1024
    print(f"Written {JSON_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    download()
    build()
