"""Prepare the Beat the Blues (BtheB) dataset in long format — Segment 1.

A real RCT of computer-delivered CBT for depression vs. treatment as usual. 100
patients had their Beck Depression Inventory (BDI) measured at baseline and again
at 2, 4, 6, and 8 months. Reshapes the wide source table to one row per
patient-visit so a linear mixed-effects model can account for the repeated
measures within each patient.

Mirrors the "Data-prep cell" in RetreatExercise.md, Segment 1.

    python scripts/make_btheb_data.py

Needs network on first run (fetches from the R `HSAUR` package mirror); the
resulting CSV is local and every analysis run afterwards is fully offline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "data" / "btheb_long.csv"


def main() -> None:
    wide = sm.datasets.get_rdataset("BtheB", "HSAUR").data
    wide = wide.reset_index().rename(columns={"index": "patient"})

    # reshape wide -> long (one row per patient-visit)
    long = pd.melt(
        wide,
        id_vars=["patient", "drug", "length", "treatment", "bdi.pre"],
        value_vars=["bdi.2m", "bdi.4m", "bdi.6m", "bdi.8m"],
        var_name="visit",
        value_name="bdi",
    )
    long["month"] = long["visit"].map(
        {"bdi.2m": 2, "bdi.4m": 4, "bdi.6m": 6, "bdi.8m": 8}
    )
    long = long.rename(columns={"bdi.pre": "bdi_pre"}).dropna(subset=["bdi"])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(long)} rows ({long['patient'].nunique()} patients) to {OUT_PATH}")
    print("Key columns: patient, month (2/4/6/8), bdi (outcome), treatment, bdi_pre")


if __name__ == "__main__":
    main()
