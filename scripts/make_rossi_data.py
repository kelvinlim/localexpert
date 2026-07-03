"""Prepare the Rossi recidivism dataset — Segment 3.

432 released prisoners followed for one year; the event is re-arrest. A perfect
analog for time-to-relapse / readmission after an intervention: a time-to-event
outcome with censoring (people never re-arrested during follow-up).

Mirrors the "Data-prep cell" in RetreatExercise.md, Segment 3. Rossi ships inside
lifelines, so this runs fully offline.

    python scripts/make_rossi_data.py
"""

from __future__ import annotations

from pathlib import Path

from lifelines.datasets import load_rossi

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "data" / "rossi.csv"


def main() -> None:
    r = load_rossi()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    r.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(r)} rows to {OUT_PATH}")
    print("week = time to re-arrest; arrest = event (1) vs censored (0)")
    print("fin = financial-aid treatment; plus age, prior offenses (prio), etc.")


if __name__ == "__main__":
    main()
