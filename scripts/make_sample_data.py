"""Generate a synthetic biobehavioral dataset for the demo.

Models a daily-diary + wearable study: self-reported psychological stress
predicting heart-rate variability (RMSSD), with covariates. Deliberately
injects right-skew, outliers, and missingness so the EDA/cleaning skills have
something real to find. Deterministic via a fixed seed.

    python scripts/make_sample_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "data" / "sample_biobehavioral.csv"

N = 300
SEED = 20260703


def main() -> None:
    rng = np.random.default_rng(SEED)

    participant_id = np.arange(1, N + 1)
    age = rng.normal(38, 12, N).clip(18, 75).round().astype(int)
    sex = rng.choice(["F", "M"], size=N, p=[0.55, 0.45])
    # Caffeine intake (mg/day): right-skewed, as real intake tends to be.
    caffeine_mg = rng.gamma(shape=2.0, scale=90.0, size=N).round(1)

    # Daily stress score (0-10), mildly right-skewed.
    stress = (rng.beta(2.0, 4.0, N) * 10).round(1)

    # True model: higher stress and caffeine lower RMSSD; older age lowers it too.
    noise = rng.normal(0, 8, N)
    rmssd = (
        70.0
        - 3.2 * stress
        - 0.02 * caffeine_mg
        - 0.35 * (age - 38)
        + np.where(sex == "F", 3.0, 0.0)
        + noise
    )
    # RMSSD is strictly positive and right-skewed -> exponentiate a scaled version.
    rmssd = np.clip(rmssd, 5, None)

    df = pd.DataFrame(
        {
            "participant_id": participant_id,
            "age": age,
            "sex": sex,
            "caffeine_mg": caffeine_mg,
            "stress_score": stress,
            "rmssd": rmssd.round(2),
        }
    )

    # --- Inject outliers: a few implausible RMSSD spikes (sensor artefacts). ---
    outlier_idx = rng.choice(N, size=6, replace=False)
    df.loc[outlier_idx, "rmssd"] = rng.uniform(180, 260, size=6).round(2)

    # --- Inject missingness ---
    # MCAR: random caffeine values missing (~7%, e.g. forgot to log).
    mcar_idx = rng.choice(N, size=int(0.07 * N), replace=False)
    df.loc[mcar_idx, "caffeine_mg"] = np.nan

    # MAR: older participants more likely to miss rmssd (technical unfamiliarity).
    miss_prob = np.clip((df["age"] - 40) / 120, 0, 0.5)
    mar_mask = rng.random(N) < miss_prob
    df.loc[mar_mask, "rmssd"] = np.nan

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(df)} rows to {OUT_PATH}")
    print(f"Missing per column:\n{df.isna().sum()}")
    print(f"Injected {len(outlier_idx)} RMSSD outliers.")


if __name__ == "__main__":
    main()
