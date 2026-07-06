---
description: Statistical power analysis — sample size, minimum detectable effect, achieved power, and power curves for the standard test families.
agent: agent
---

**When to use this:** When planning a study (how many subjects?), or asking what an existing or fixed sample can detect. Often has NO dataset.

You are performing a **power-analysis** analysis (Phase 7) in the open Jupyter notebook. Work incrementally: add and run one cell at a time and inspect each output before continuing. Load the dataset the user names (ask which file if unclear). Follow the procedure below and satisfy every check, then write a short markdown summary as the final cell.

## Objective
Answer a power question quantitatively for the appropriate test family. The four
quantities — **effect size, sample size (N), alpha, power** — are linked; fix any
three and solve for the fourth. This skill is usually a *study-planning* task with
no dataset: the parameters come from the request, not a CSV.

Everything here uses `statsmodels.stats.power` (already installed) — no other
package is needed.

## Procedure
1. **Frame the calculation.** State (a) the test family implied by the design, (b)
   which of the four quantities is the **unknown to solve for**, and (c) the values
   given for the other three. Every power class exposes
   `.solve_power(effect_size=None, nobs=None, alpha=None, power=None, ...)` and
   solves for whichever argument you leave as `None`.
2. **Pick the tool and effect-size metric for the design:**
   - Independent two-sample / paired / one-sample **t-test** →
     `statsmodels.stats.power.TTestIndPower` (two-sample) or `TTestPower`
     (one-sample/paired); effect size = Cohen's **d**. `TTestIndPower` takes
     `nobs1` (per-group base n) and `ratio` (n2/n1).
   - One-way **ANOVA** → `FTestAnovaPower`; effect size = Cohen's **f**; pass
     `k_groups`. Note it takes `nobs` = **total** N, not per-group.
   - **Two proportions** → `NormalIndPower`; convert the two rates with
     `statsmodels.stats.proportion.proportion_effectsize(p1, p2)` (Cohen's **h**).
   - **Correlation** → normal approximation on Fisher's z:
     `z = arctanh(r)`, required `n ≈ ((z_{1-alpha/2} + z_{power}) / z)**2 + 3`
     (use `scipy.stats.norm.ppf` for the quantiles); state it is an approximation.
   - **Chi-square** goodness-of-fit / independence → `GofChisquarePower`; effect
     size = Cohen's **w**; pass `n_bins` (number of cells).
   - **Linear / multiple regression** (F-test for R² or added predictors) →
     `FTestPower`; effect size = Cohen's **f²**; set `df_num` (predictors tested)
     and express `df_denom` in terms of N.
3. **Run the requested mode(s):**
   - **A-priori (sample size):** leave `nobs`/`nobs1=None`; supply effect, alpha,
     power. Report the N and **round UP** (`math.ceil`) to whole subjects — and to a
     whole number per group where groups apply.
   - **Sensitivity / MDES:** leave `effect_size=None`; supply N, alpha, power. Report
     the **minimum detectable effect** and interpret whether it is realistic.
   - **Post-hoc achieved power:** leave `power=None`; supply the observed N and
     effect. **Caveat, state it:** power computed from the *observed* effect is a
     deterministic restatement of the p-value and is not evidence — prefer reporting
     sensitivity/MDES instead.
   - **Power curve:** sweep N (or effect size) and plot power, e.g.
     `TTestIndPower().plot_power(dep_var='nobs', nobs=np.arange(...), effect_size=[...])`,
     or a manual loop with matplotlib; mark the N that reaches the target power.
4. **Report** the numbers with their assumptions and a one-line plain-language
   conclusion ("~64 participants per group are needed to detect d=0.5 at 80% power").

## Checks
- The test family matches the stated design, and the effect-size metric is the right
  one for that family (d / f / h / w / f²) — never mix them up.
- The correct sample-size argument is used: `nobs1` (per group) for `TTestIndPower`
  vs `nobs` (total) for `FTestAnovaPower`; a-priori Ns are rounded up.
- One- vs two-sided is stated (`alternative`), and alpha is adjusted when several
  tests are planned (Bonferroni/FDR).
- The effect size is justified (a domain-motivated value, or an explicitly named
  Cohen small/medium/large convention — 0.2/0.5/0.8 for d), not left implicit.
- Any post-hoc power on an observed effect carries the circularity caveat.

## Output
A markdown summary: the design and test family, the mode(s) run, the input
assumptions (effect size and its justification, alpha, power, allocation), the
solved quantity, and a plain-language conclusion. Include the power curve when one
was requested.
