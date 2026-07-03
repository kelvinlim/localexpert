---
description: Frame the research question and map variables before touching data.
agent: agent
---

You are performing a **define-question** analysis (Phase 1) in the open Jupyter notebook. Work incrementally: add and run one cell at a time and inspect each output before continuing. Load the dataset the user names (ask which file if unclear). Follow the procedure below and satisfy every check, then write a short markdown summary as the final cell.

## Objective
Bind the analysis to clear operational definitions so later steps cannot drift
into data dredging or p-hacking. Produce a written analysis contract.

## Procedure
1. State the **primary objective** as one biobehavioral relationship in plain
   language (e.g. "Does daily psychological stress predict autonomic reactivity
   measured as heart-rate variability?").
2. Map every column of the dataset into a structural role and record it:
   - **Independent variables / predictors** (e.g. self-reported stress score).
   - **Dependent variables / outcomes** (e.g. RMSSD from a wearable).
   - **Covariates / confounders** (e.g. age, biological sex, caffeine intake).
3. Write the **null (H0)** and **alternative (H1)** hypotheses explicitly.
4. Note the intended statistical test family implied by the roles and data types
   (e.g. OLS regression for a continuous outcome with continuous + categorical
   predictors) — this is a hypothesis to be checked in Phase 4, not a commitment.

## Checks
- Every variable in the dataset has exactly one assigned role or is explicitly
  excluded with a reason.
- H0 and H1 are mutually exclusive and refer to the mapped variables by name.

## Output
A short markdown summary: objective, a variable-role table, H0/H1, and the
tentative test family. Do not run inferential statistics in this phase.
