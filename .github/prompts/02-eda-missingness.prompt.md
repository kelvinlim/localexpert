---
description: Exploratory data analysis of distributions plus missingness diagnostics.
agent: agent
---

**When to use this:** Immediately after loading raw data, before any cleaning or testing.

You are performing a **eda-missingness** analysis (Phase 2) in the open Jupyter notebook. Work incrementally: add and run one cell at a time and inspect each output before continuing. Load the dataset the user names (ask which file if unclear). Follow the procedure below and satisfy every check, then write a short markdown summary as the final cell.

## Objective
Examine the shape and integrity of the raw data. Characterise distributions and
quantify missingness so the Phase 3 cleaning strategy is evidence-based.

## Procedure
1. Load the dataset with pandas and print `df.shape`, `df.dtypes`, and `df.head()`.
2. For each continuous variable compute descriptive metrics with pandas/scipy:
   mean, median, standard deviation, `scipy.stats.skew`, and `scipy.stats.kurtosis`.
3. Assess normality visually: histogram + KDE (`seaborn.histplot(..., kde=True)`)
   and a Q-Q plot (`scipy.stats.probplot`). Biobehavioral metrics (reaction times,
   hormone levels) are frequently right-skewed — expect and report it.
4. Quantify missingness:
   - Percent missing **per variable**: `df.isna().mean().sort_values(ascending=False)`.
   - Percent missing **per participant/row**: `df.isna().mean(axis=1)`.
5. Reason about the missingness mechanism and state your best judgement with evidence:
   - **MCAR** — missingness unrelated to any variable (e.g. random battery failure).
   - **MAR** — missingness depends on an *observed* variable (e.g. older participants
     miss more sensor data). Probe by comparing observed covariates between rows that
     are missing vs. present on the target column.
   - **MNAR** — missingness depends on the *unobserved* value itself (e.g. skipping a
     mood survey because symptoms are severe). Cannot be proven from data alone; flag it.

## Checks
- Skewness/kurtosis reported for every continuous variable.
- Missingness percentages reported both per variable and per row.
- A stated mechanism (MCAR/MAR/MNAR) per incomplete variable, with reasoning.

## Output
A markdown findings summary plus the generated plots. Do not impute or drop data
in this phase — only describe and diagnose.
