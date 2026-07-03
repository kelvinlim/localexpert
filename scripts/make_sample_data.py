"""Generate the synthetic biobehavioral demo dataset.

Thin wrapper over ``localexpert.sample_data`` (the generation logic lives in the
package so ``localexpert init`` can call it too).

    python scripts/make_sample_data.py
"""

from __future__ import annotations

from pathlib import Path

from localexpert.sample_data import make

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "data" / "sample_biobehavioral.csv"


def main() -> None:
    path = make(OUT_PATH)
    import pandas as pd

    df = pd.read_csv(path)
    print(f"Wrote {len(df)} rows to {path}")
    print(f"Missing per column:\n{df.isna().sum()}")


if __name__ == "__main__":
    main()
