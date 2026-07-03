---
name: psychometrics-reliability
description: Internal-consistency reliability and factor structure for a multi-item scale, including the reverse-keyed-item trap.
phase: 5
when_to_use: When validating a symptom inventory or rating scale — grouped items that should form coherent subscales.
---
## Objective
Assess whether a set of questionnaire items forms reliable, coherent scales, and
whether the items recover the expected factor structure. This is the workflow
behind validating any symptom inventory or rating scale. It contains a deliberate
trap — **reverse-keyed items** — that punishes naive analysis with impossible
(negative) reliabilities.

## Procedure
1. **Load and orient.** Read the CSV, list the item columns, and group them into
   their named scales (e.g. Agreeableness A1–A5, Conscientiousness C1–C5, ...).
   Drop or note non-item columns (ids, demographics). Handle missing item
   responses (listwise per scale is acceptable here; state what you did).
2. **Cronbach's alpha, raw.** For each scale compute alpha directly (no extra
   package needed):
   `k = n_items; var_items = X.var(axis=0, ddof=1).sum(); var_total = X.sum(axis=1).var(ddof=1);`
   `alpha = k/(k-1) * (1 - var_items/var_total)`.
   Report alpha per scale. **A negative alpha is not a valid reliability — it is a
   red flag that items point in opposite directions.** Do not report it as "low
   reliability" and move on.
3. **Detect and recode reverse-keyed items.** Do NOT rely on a single pass of
   corrected item–total correlations — when a scale has several reverse-keyed items
   that heuristic cascades and mis-flags good items. Use the sign of a **single-factor
   loading** instead: fit `FactorAnalyzer(n_factors=1, rotation=None)` on the scale's
   items, orient so the majority of loadings are positive, and treat any item with a
   **negative** loading as reverse-keyed. Recode each flagged item on the response
   scale (for a 1–6 scale, `new = (min + max) - old = 7 - old`; infer min/max from the
   observed range).
4. **Alpha, recoded.** Recompute alpha per scale after recoding and **explain what
   changed** — the jump from a negative/near-zero raw alpha to an acceptable one is
   the whole point. Name which items you flipped.
5. **Factor adequacy.** On the (recoded) item matrix test whether factor analysis
   is even justified:
   - KMO sampling adequacy: `factor_analyzer.factor_analyzer.calculate_kmo`
     (want overall > 0.6; ~0.8+ is good).
   - Bartlett's sphericity: `factor_analyzer.factor_analyzer.calculate_bartlett_sphericity`
     (want p < 0.001).
6. **Exploratory factor analysis.** Fit `factor_analyzer.FactorAnalyzer` (e.g.
   oblique `rotation='oblimin'`), extract the expected number of factors, and
   inspect the loadings: report whether the items load onto the expected
   interpretable factors and flag any that cross-load or land on the wrong factor.

## Checks
- No scale is reported with a negative or near-zero alpha without investigating
  reverse-keyed items — that is the designed trap, not an acceptable result.
- Every reverse-keyed item is named, and raw-vs-recoded alpha is shown side by side
  with a one-line explanation of the change.
- KMO and Bartlett are reported before interpreting the factor solution.
- Factor interpretation references the actual loadings, not just the factor count.

## Output
A markdown summary: a raw-vs-recoded alpha table per scale, the list of items
recoded, KMO and Bartlett results, and whether EFA recovered the expected factors
— with a plain-language note on any scale that stays weak even when done correctly.
