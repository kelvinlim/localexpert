---
name: statistical-testing
description: Check assumptions, run the right test, correct for multiplicity, report effect sizes.
phase: 4
when_to_use: On a cleaned dataset, to perform the hypothesis test framed in Phase 1.
---
## Objective
Execute the formal hypothesis test specified in Phase 1 on the cleaned data,
validating assumptions first and reporting practical significance, not just p-values.

## Procedure
1. **Check assumptions** on the clean data before choosing a test:
   - Homoscedasticity: Levene's test (`scipy.stats.levene`).
   - Normality of residuals: Shapiro-Wilk (`scipy.stats.shapiro`) or Q-Q inspection.
   - Multicollinearity (regression): Variance Inflation Factors via
     `statsmodels.stats.outliers_influence.variance_inflation_factor` (flag VIF > 5).
2. **Select and run the model**:
   - Parametric (assumptions hold): independent t-test (`scipy.stats.ttest_ind`),
     ANOVA (`scipy.stats.f_oneway`), or OLS regression (`statsmodels.formula.api.ols`).
   - Non-parametric (assumptions violated): Mann-Whitney U (`scipy.stats.mannwhitneyu`)
     in place of a t-test, Kruskal-Wallis (`scipy.stats.kruskal`) in place of ANOVA.
   - Repeated measures / clustered data (e.g. wearable streams per participant over
     time): linear mixed-effects model (`statsmodels.formula.api.mixedlm`) with random
     intercepts/slopes.
3. **Correct for multiple comparisons** when running several tests: Bonferroni or FDR
   via `statsmodels.stats.multitest.multipletests`.
4. **Report effect sizes**, not just significance: Cohen's d for mean differences,
   partial eta-squared for ANOVA, or R^2 for regression.

## Checks
- Every assumption relevant to the chosen test was checked and the result stated.
- The parametric-vs-nonparametric choice is justified by the assumption results.
- A p-value is always accompanied by an effect size and its interpretation.
- If multiple tests were run, a correction was applied and named.

## Output
A markdown results summary: assumptions checked, test chosen and why, the test
statistic and (corrected) p-value, the effect size, and a plain-language conclusion
about H0/H1 from Phase 1.
