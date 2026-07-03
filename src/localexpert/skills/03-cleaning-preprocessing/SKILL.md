---
name: cleaning-preprocessing
description: Turn raw data into an analysis-ready state without introducing bias.
phase: 3
when_to_use: After EDA/missingness diagnostics, before statistical testing.
---
## Objective
Transform messy raw data into an analysis-ready dataset, choosing each mitigation
from the Phase 2 diagnostics rather than by default, and documenting every decision.

## Procedure
1. **Handle missingness** using the mechanism identified in Phase 2:
   - MCAR/MAR and minimal (<5% on the variable): listwise deletion (`df.dropna()`)
     is acceptable.
   - Widespread missingness: multiple imputation to preserve statistical power via
     `sklearn.experimental.enable_iterative_imputer` then
     `sklearn.impute.IterativeImputer` (the scikit-learn analogue of MICE).
2. **Mitigate outliers**: detect with the IQR rule (values outside
   `Q1 - 1.5*IQR` .. `Q3 + 1.5*IQR`) or z-scores (`scipy.stats.zscore`, |z| > 3).
   Decide *a priori* whether to remove, winsorize (`scipy.stats.mstats.winsorize`),
   or transform — do not silently drop.
3. **Transform** variables that violate normality: log, square-root, or Box-Cox
   (`scipy.stats.boxcox`, requires strictly positive values). Re-check skewness after.
4. **Scale** features when combining diverse streams (e.g. millisecond reaction times
   with microvolt skin conductance): z-score standardisation (`StandardScaler`) or
   min-max (`MinMaxScaler`).

## Checks
- Every missing value is either imputed or its row removed — no silent NaNs remain
  in the analysis columns.
- The outlier policy (remove/winsorize/transform) is stated before it is applied.
- Post-transformation skewness is reported so the effect is visible.
- Row count before vs. after cleaning is reported.

## Output
A cleaned DataFrame plus a markdown changelog: what was imputed, what was
dropped/winsorized/transformed, and the resulting row count and skewness.
