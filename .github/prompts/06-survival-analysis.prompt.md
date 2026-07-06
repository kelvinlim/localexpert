---
description: Time-to-event analysis with censoring — Kaplan-Meier, log-rank, and Cox proportional hazards.
agent: agent
---

**When to use this:** When the outcome is time-to-event (relapse, readmission, re-arrest) and some subjects never experience the event during follow-up.

You are performing a **survival-analysis** analysis (Phase 6) in the open Jupyter notebook. Work incrementally: add and run one cell at a time and inspect each output before continuing. Load the dataset the user names (ask which file if unclear). Follow the procedure below and satisfy every check, then write a short markdown summary as the final cell.

## Objective
Analyze a time-to-event outcome correctly, accounting for **censoring** — subjects
who are followed but never experience the event within the observation window.
Ignoring censoring (e.g. running logistic regression on the event flag, or a t-test
on the time column) is the classic mistake this skill exists to avoid.

## Procedure
1. **Load and identify the survival columns.** Read the CSV and identify the
   duration column (time to event) and the event-indicator column (1 = event
   occurred, 0 = censored). State how many events vs. censored observations there
   are — the censored fraction is exactly why naive methods fail.
2. **Explain censoring** in one or two sentences in the context of these data
   (e.g. "a person never re-arrested during the one-year follow-up is right-censored;
   we know only that their time-to-event exceeds the follow-up").
3. **Kaplan-Meier curves.** Fit `lifelines.KaplanMeierFitter` overall and separately
   for each level of the grouping/treatment variable of interest; plot the survival
   curves together with a legend.
4. **Log-rank test.** Compare the groups' survival with
   `lifelines.statistics.logrank_test` and report the test statistic and p-value.
   Note when a result sits right at the p ≈ 0.05 boundary — effect size still matters.
5. **Cox proportional-hazards model.** Fit `lifelines.CoxPHFitter` with the available
   covariates. Report **hazard ratios** (`exp(coef)`), their confidence intervals,
   and p-values; interpret each in words (HR < 1 = lower risk of the event per unit
   increase) and name which predictors are significant and which are not.

## Checks
- The event indicator and duration are correctly identified and passed to every
  fitter; the event column is never treated as a plain binary outcome for logistic
  regression.
- The number of events vs. censored observations is reported.
- The log-rank test accompanies the KM plot (a visual difference is not a test).
- Cox results are given as hazard ratios with interpretation, not raw coefficients
  alone.

## Output
A markdown summary: event/censored counts, the KM comparison and what it shows, the
log-rank p-value, and a hazard-ratio table from the Cox model with a plain-language
reading of which covariates raise or lower risk.
