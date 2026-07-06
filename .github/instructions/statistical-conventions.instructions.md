---
description: Cross-cutting statistical reporting conventions the assistant must always follow, regardless of the specific analysis.
applyTo: "**"
---

# Statistical conventions

- **Always pair a p-value with an effect size** (Cohen's d, R², partial η², hazard ratio,
  etc.) and interpret it in plain language. A p-value alone is not a result.
- **Check assumptions before a parametric test** (normality, homoscedasticity,
  independence, multicollinearity) and state what you checked. If assumptions fail, switch
  to a non-parametric or robust alternative and say why.
- **Correct for multiplicity** when running several tests (Bonferroni or FDR); name the
  correction used.
- **State the test you chose and why** it fits the design and data types.
- **Prefer estimates with confidence intervals** over bare significance; report direction
  and magnitude, not just "significant / not significant".
- **Do not p-hack:** no fishing for significance, no undisclosed multiple comparisons, no
  dropping cases to move a p-value.
