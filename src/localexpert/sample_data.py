"""Synthetic biobehavioral sample dataset — importable so both the CLI script and
``localexpert init`` can generate it.

Models a daily-diary + wearable study: self-reported psychological stress predicting
heart-rate variability (RMSSD), with covariates. Deliberately injects right-skew,
outliers, and missingness so the EDA/cleaning skills have something real to find.
Deterministic via a fixed seed. The true signal is **stress ↓ RMSSD** — the
TUTORIAL cross-checks against this.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

N = 300
SEED = 20260703


def build(n: int = N, seed: int = SEED) -> pd.DataFrame:
    """Return the synthetic dataset as a DataFrame (no file I/O)."""
    rng = np.random.default_rng(seed)

    participant_id = np.arange(1, n + 1)
    age = rng.normal(38, 12, n).clip(18, 75).round().astype(int)
    sex = rng.choice(["F", "M"], size=n, p=[0.55, 0.45])
    # Caffeine intake (mg/day): right-skewed, as real intake tends to be.
    caffeine_mg = rng.gamma(shape=2.0, scale=90.0, size=n).round(1)
    # Daily stress score (0-10), mildly right-skewed.
    stress = (rng.beta(2.0, 4.0, n) * 10).round(1)

    # True model: higher stress and caffeine lower RMSSD; older age lowers it too.
    noise = rng.normal(0, 8, n)
    rmssd = (
        70.0
        - 3.2 * stress
        - 0.02 * caffeine_mg
        - 0.35 * (age - 38)
        + np.where(sex == "F", 3.0, 0.0)
        + noise
    )
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
    outlier_idx = rng.choice(n, size=6, replace=False)
    df.loc[outlier_idx, "rmssd"] = rng.uniform(180, 260, size=6).round(2)

    # --- Inject missingness ---
    # MCAR: random caffeine values missing (~7%, e.g. forgot to log).
    mcar_idx = rng.choice(n, size=int(0.07 * n), replace=False)
    df.loc[mcar_idx, "caffeine_mg"] = np.nan
    # MAR: older participants more likely to miss rmssd (technical unfamiliarity).
    miss_prob = np.clip((df["age"] - 40) / 120, 0, 0.5)
    mar_mask = rng.random(n) < miss_prob
    df.loc[mar_mask, "rmssd"] = np.nan

    return df


def make(out_path: str | Path) -> Path:
    """Build the dataset and write it to ``out_path`` (parents created). Returns the path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    build().to_csv(out_path, index=False)
    return out_path
