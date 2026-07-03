"""Prepare the bfi personality-items dataset — Segment 2.

2,800 respondents answering 25 personality items forming five 5-item scales:
Agreeableness (A1-A5), Conscientiousness (C1-C5), Extraversion (E1-E5),
Neuroticism (N1-N5), Openness (O1-O5). Some items are reverse-keyed — the
deliberate, highly teachable trap of this segment.

Mirrors the "Data-prep cell" in RetreatExercise.md, Segment 2.

    python scripts/make_bfi_data.py

Needs network on first run (fetches from the R `psych` package mirror); the
resulting CSV is local and every analysis run afterwards is fully offline.
"""

from __future__ import annotations

from pathlib import Path

import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "data" / "bfi.csv"


def main() -> None:
    bfi = sm.datasets.get_rdataset("bfi", "psych").data

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    bfi.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(bfi)} rows x {bfi.shape[1]} cols to {OUT_PATH}")
    print("5 scales: A=Agreeableness, C=Conscientiousness, E=Extraversion,")
    print("          N=Neuroticism, O=Openness (items A1..A5, C1..C5, etc.)")


if __name__ == "__main__":
    main()
