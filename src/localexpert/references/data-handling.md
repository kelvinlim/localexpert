---
description: How to handle data safely and correctly — local-only processing, missingness, and outliers.
---
# Data handling

- **Keep data local.** Never upload the dataset, or suggest uploading it, to any cloud or
  web service. This workflow exists so sensitive data stays on the machine.
- **Report missingness before modelling.** Show missing counts per variable (and per row
  when relevant) and consider the mechanism (MCAR / MAR / MNAR) before deciding how to handle it.
- **Never silently drop rows.** If you exclude cases (listwise deletion, filtering), state
  how many and why, and prefer principled handling (e.g. imputation) when missingness is
  substantial.
- **Inspect outliers, don't quietly delete them.** Flag extreme values, look at them, and
  decide explicitly (cap / transform / exclude / keep) — reporting the choice and its effect.
- **Note the data's shape and provenance** (rows, columns, source) when you load it, so the
  record is self-explanatory.
