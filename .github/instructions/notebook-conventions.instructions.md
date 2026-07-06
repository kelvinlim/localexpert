---
description: How to structure the analysis in the notebook so it stays transparent and reproducible.
applyTo: "**"
---

# Notebook conventions

- **Work one step per cell.** Run a small piece of code, inspect its output, then decide the
  next step — do not write one giant block.
- **Interpret alongside the code.** Add a short markdown note for each step saying what it
  shows and why it matters, so the notebook reads top-to-bottom.
- **End with a plain-language summary** a non-statistician can understand, including the main
  caveats.
- **The notebook is the audit record.** Every decision, output, and figure should be visible
  in it, so anyone can re-run it and see exactly how each number was produced.
