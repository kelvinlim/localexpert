# Tutorial — your first analysis with a local AI

A complete, click-by-click walkthrough of one analysis, written for someone who has
**never programmed**. It assumes you finished [SETUP.md](SETUP.md) (Ollama, uv, VS Code,
and the folder created by `localexpert init`).

We'll use the bundled practice dataset `data/sample_biobehavioral.csv` — a made-up study
of 300 people measuring daily **stress** and a heart-rate-variability measure called
**RMSSD** (higher = more relaxed). It was built with a known pattern — **more stress goes
with lower RMSSD** — so you can check the AI against the right answer.

---

## 1. Open the starter notebook

In VS Code's Explorer (left), open **`notebooks/analysis_starter.ipynb`**.

At the **top-right** of the notebook, click **Select Kernel** and choose the **`.venv`**
for this folder (it may be labelled `Python 3.12 (.venv)`).

> **What you should see:** a document with a title cell and one code cell.
> **If it goes wrong:** if no `.venv` appears, reopen the folder (`File → Open Folder`) so
> VS Code detects it, or pick any Python 3.12 and re-run.

## 2. Run the first cell (load the data)

Click the code cell that reads `pd.read_csv(...)` and press the **▶ Run** button on its
left (or `Shift+Enter`).

> **What you should see:** `(300, 6)` and a small table of the first rows (columns like
> `age`, `sex`, `stress_score`, `rmssd`). That confirms the data loaded.

## 3. Open the AI chat in Agent mode

Open **Copilot Chat** — press **⌃⌘I** (Mac) / **Ctrl+Alt+I** (Windows), or click the
chat/speech-bubble icon in the **top title bar**. It opens on the **right** (not the left
sidebar). At the top of the chat box:

- Set the mode to **Agent**.
- Set the model to your local **`qwen3.5:9b`**. Not listed? Add it via the model dropdown →
  **Manage Models → Add Models → Ollama** (see [SETUP.md](SETUP.md) Step 5).

> **Why Agent mode?** Only Agent mode lets the AI *add and run cells for you*. Plain "Ask"
> mode just talks.

## 4. Ask your question

Type this into the chat and send it:

> **Does stress predict HRV (rmssd) in the loaded data? Do proper exploratory data
> analysis first — check distributions and missing values — then run an appropriate model.
> Work one cell at a time.**

(Or, for a guided version, type **`/eda-missingness`** to run the built-in EDA skill, then
ask the modelling question.)

## 5. Watch it work — and stay in control

The AI will propose cells and ask permission to run them. **Read each step before
approving.** A healthy run looks roughly like:

1. **Summary + missing values** — it reports 300 rows and that a few values are missing
   (about **21** missing `caffeine_mg`, **10** missing `rmssd`). Good — real data has gaps.
2. **Distributions** — histograms of `stress_score` and `rmssd`. It should notice a handful
   of **very high RMSSD outliers** (there are 6 planted sensor-glitch values).
3. **A model** — a regression of `rmssd` on `stress_score` (plus covariates like age/sex).

> **How to read the result:** you're looking for the **direction and size** of the stress
> effect. Expect a **negative** relationship of roughly **−2 to −3 RMSSD per 1 point of
> stress**, statistically significant (**p ≈ 0.01**), but a **small** overall fit
> (R² ≈ 0.05). Plain-language: *higher stress goes with modestly lower HRV.* That matches
> how the data was built.

### When to say "no" or redirect
- **It edited the wrong cell / a cell vanished.** Press **Undo** (`Ctrl/Cmd+Z`) in the
  notebook and tell it: *"Undo that — add a new cell below instead of editing the previous
  one."*
- **It skipped EDA and jumped to a model.** Reply: *"Before modelling, show the missing-value
  counts and the distributions, and handle the outliers."*
- **It ignored the outliers.** Reply: *"There are extreme RMSSD values — inspect and address
  them (e.g. cap or exclude), then refit and tell me what changed."*
- **A cell errored.** Paste nothing — just say *"that cell errored, read the traceback and
  fix it."* The AI can usually read the error and correct itself.

## 6. Interpret and save

Ask for a plain-language wrap-up:

> **Summarise what we found in one paragraph a non-statistician can understand, and note the
> main caveats.**

Then **save the notebook** (`Ctrl/Cmd+S`). Because every step — the code, the output, the
charts, and the AI's reasoning — is right there in the notebook, the file *is* your
auditable record: you (or a colleague) can reopen it and see exactly how each number was
produced, or **Run All** to reproduce it.

---

## Using your own data

Put your CSV in the `data/` folder, open a fresh notebook (or reuse the starter), and ask
the same kind of question naming your file and columns. **Before using sensitive data,
re-read the privacy checklist in [SETUP.md](SETUP.md)** — confirm the model in the chat box
is your local one.

## The built-in skills

For standard analyses you can invoke a skill by typing `/` in the chat:

| Type `/…` | Does |
|---|---|
| `/define-question` | Frame the question and map variables before touching data |
| `/eda-missingness` | Distributions + missing-data diagnostics |
| `/cleaning-preprocessing` | Handle missingness, outliers, transforms |
| `/statistical-testing` | Assumption checks, the right test, effect sizes |
| `/psychometrics-reliability` | Cronbach's alpha + factor analysis for scales |
| `/survival-analysis` | Kaplan–Meier, log-rank, Cox for time-to-event |
| `/power-analysis` | Sample size / power for planning a study |

Each one walks the AI through a rigorous procedure and a checklist for that analysis.
