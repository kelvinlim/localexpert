**Hands-On AI Data Analysis in Google Colab**

Facilitator Guide — Department of Psychiatry Faculty Session

*Gemini Data Science Agent · \~60 minutes · three openly-available datasets*

This guide runs a one-hour hands-on session in which faculty use Colab's Gemini-powered Data Science Agent to perform three analyses that map onto the design families most common in psychiatric research: **longitudinal/repeated-measures**, **psychometric reliability and factor structure**, and **survival / time-to-event**. Every dataset is public and contains no PHI, so the entire session stays safely inside Colab with no Business Associate Agreement concern.

| Why these three datasets They cover the three analysis types psychiatric researchers run most, each dataset has a published “right answer” so the room can verify rather than trust the agent, and all load in one or two lines with no download or credentialing. |
| :---- |

# **Why the Notebook Format Matters**

Before the first analysis, it is worth pausing on the medium itself. A Colab notebook is not just a place to run code — it is a **living record of the analysis**. Unlike a point-and-click statistics package that hands back only a final table, a notebook interleaves the question, the code, the output, the figures, and the written interpretation in a single, top-to-bottom document. For research that has to be defensible, reproducible, and shareable, that property is the whole point — and it is exactly what makes pairing a notebook with an AI agent so powerful, because the agent’s reasoning and every step it takes are captured in front of you rather than hidden.

### **It documents the work, not just the answer**

* **Every step is visible.** Data loading, cleaning decisions, the model specification, and the result all sit in the same file. A colleague — or a reviewer, or you in six months — can read top to bottom and see precisely how a number was produced, not just what it was.

* **Code and prose live together.** Markdown cells let you state the hypothesis, justify a statistical choice, and interpret the output alongside the code that generated it. The notebook becomes the methods section and the results section at once.

* **Reproducibility is built in.** Because the code is preserved with its output, anyone can re-run the notebook and regenerate the identical analysis. That is the difference between “trust me” and “run it yourself.”

### **It captures the iterative process**

Real analysis is never a straight line — you fit a model, inspect the residuals, notice a problem, adjust, and re-fit. The notebook records that journey instead of erasing it:

* **The dead ends are part of the record.** A first model that fit poorly and the corrected one that followed can both remain in the notebook, showing the reasoning that led to the final choice. That trail is often more instructive than the destination.

* **The AI agent’s iteration is on full display.** When the Data Science Agent hits an error, you watch it read the traceback, revise the code, and re-run — each attempt written into the notebook in real time. You are not handed a black-box answer; you see the agent think, stumble, and self-correct, which is exactly what lets you judge whether to trust it.

* **Refinement is cumulative, not destructive.** You can layer on a diagnostic plot, then a covariate, then a sensitivity check — each in its own cell — without losing what came before. The analysis grows as a documented sequence rather than a single overwritten script.

| The throughline for today Each of the three analyses ahead is designed to show this off: you will watch the agent build an analysis cell by cell, narrate its choices, and — especially in the blind-prompt versions — sometimes take a wrong turn you can see and correct. Keep an eye on the notebook as a record: by the end of each segment you should have a document you could hand to a collaborator that explains itself. |
| :---- |

# **Session at a Glance**

| Segment | Dataset & Method | Time |
| :---- | :---- | :---- |
| 1\. Longitudinal | Beat the Blues — linear mixed-effects model (depression over time) | 18 min |
| 2\. Psychometrics | bfi — Cronbach’s alpha \+ exploratory factor analysis | 20 min |
| 3\. Survival | Rossi — Kaplan–Meier, log-rank, Cox regression | 18 min |
| Wrap-up | “Where the agent needs you” — judgment & verification | 4 min |

**Two prompt styles to demonstrate**

For each dataset the guide gives two prompts. The **Directed prompt** names the design and forces the correct method — use it to guarantee a clean result. The **Blind prompt** withholds the design and tests whether the agent recognizes the structure on its own. Running both, side by side, is the most instructive thing you can do: it shows the room exactly where these tools have statistical judgment and where they don’t.

# **Before You Start (Facilitator Setup)**

1. Have each participant open a blank notebook at [colab.research.google.com](https://colab.research.google.com) and sign in with their University of Minnesota account.

2. Confirm the Gemini side panel is available (the Gemini icon, upper-right). The Data Science Agent is free for users 18+ on supported accounts.

3. Paste the data-prep cell for each dataset (below) so everyone has the CSV locally before prompting the agent. Uploading a file gives the agent cleaner footing than asking it to fetch from a package.

| PHI guardrail — say this out loud These three datasets are public and contain no protected health information. Do not upload real patient data, identifiable research data, or anything from the Healthcare Component to the consumer Colab agent — Colab is not a BAA-covered service. For PHI work, use a HIPAA-flagged Vertex AI project or a local model, and confirm coverage with UMN IT first. |
| :---- |

# **Segment 1 — Longitudinal: the Beat the Blues Depression Trial**

A real randomized controlled trial of *Beat the Blues*, a computer-delivered cognitive-behavioral therapy for depression, versus treatment as usual. 100 patients had their Beck Depression Inventory (BDI) measured at baseline and again at 2, 4, 6, and 8 months. Each patient is measured repeatedly over time — the defining feature of treatment-response research — so the teaching point is direct: repeated measures within a patient violate independence, OLS is wrong, and a **linear mixed-effects model with a random intercept per patient** is the appropriate tool.

### **Data-prep cell (paste first)**

| import statsmodels.api as sm import pandas as pd   wide \= sm.datasets.get\_rdataset('BtheB', 'HSAUR').data wide \= wide.reset\_index().rename(columns={'index': 'patient'})   \# reshape wide \-\> long (one row per patient-visit) long \= pd.melt(wide,     id\_vars=\['patient','drug','length','treatment','bdi.pre'\],     value\_vars=\['bdi.2m','bdi.4m','bdi.6m','bdi.8m'\],     var\_name='visit', value\_name='bdi') long\['month'\] \= long\['visit'\].map(     {'bdi.2m':2,'bdi.4m':4,'bdi.6m':6,'bdi.8m':8}) long \= long.rename(columns={'bdi.pre':'bdi\_pre'}).dropna(subset=\['bdi'\]) long.to\_csv('btheb\_long.csv', index=False) long.head() |
| :---- |

Then upload btheb\_long.csv to the Gemini panel. Key columns: patient (subject id), month (visit: 2/4/6/8), bdi (depression score, the outcome), treatment (BtheB vs. TAU), bdi\_pre (baseline severity).

Note the deliberate teaching feature: the data thin out from 100 patients at baseline to \~52 by month 8\. That dropout is realistic for a depression trial and is itself worth a comment — mixed models handle this incomplete data far more gracefully than a repeated-measures ANOVA that would discard anyone with a missing visit.

### **Directed prompt (paste into Gemini)**

|  *This is the Beat the Blues dataset in long format: a randomized trial of computer-delivered CBT (treatment \= BtheB) versus treatment as usual (TAU) for depression. Each patient’s Beck Depression Inventory (bdi) is measured repeatedly across months (month \= 2, 4, 6, 8), with baseline severity in bdi\_pre. I want to know whether depression improves over time and whether the BtheB treatment helps, while accounting for the repeated measurements within each patient. Please: (1) explain which statistical approach is appropriate and why OLS would be inadequate; (2) fit a linear mixed-effects model with month, treatment, and bdi\_pre as fixed effects and a random intercept for patient, using statsmodels; (3) report the fixed-effect estimates and the between-patient variance; (4) check assumptions with residual diagnostics; and (5) plot individual patient BDI trajectories with the group-average fits overlaid.* |
| :---- |

### **Blind prompt (for the side-by-side)**

|  *Does this depression treatment work?* |
| :---- |

Watch whether the agent **notices** the repeated-measures structure on its own or naively compares group means / fits OLS while ignoring that the same patients are measured five times. Recognizing the within-patient dependence unprompted is the marker of real statistical judgment.

### **Expected plan**

* Load data → inspect structure (long format, repeated patient ids, dropout over time)

* Note non-independence → select linear mixed-effects model

* Fit MixedLM: bdi \~ month \+ treatment \+ bdi\_pre, random intercept for patient

* Report fixed effects \+ between-patient variance

* Residual diagnostics \+ BDI trajectory plot by treatment group

### **Answer key — verify against these**

| Quantity | Correct value | What it means |
| :---- | :---- | :---- |
| month coefficient | ≈ −0.72 | BDI falls \~0.7 points per month — depression improves over time (p \< 0.001) |
| treatment (TAU vs BtheB) | ≈ \+3.26 | TAU patients score \~3.3 BDI points higher — i.e. BtheB does better (p ≈ 0.045) |
| baseline (bdi\_pre) | ≈ \+0.62 | Higher baseline severity carries forward (p \< 0.001) |
| Between-patient variance | ≈ 52 | Large — patients differ substantially; justifies the random effect |
| Residual variance | ≈ 25 | Within-patient scatter around each trajectory |
| N / groups | 280 obs / 100 patients | Sanity check: \~280 visits remain after dropout |
| **Facilitator note — land these points** The treatment effect is real but modest and only just significant (p ≈ 0.045) — a realistic result that invites discussion of effect size versus significance, exactly the conversation a faculty audience values. Note the direction: because TAU is the reference category, a positive coefficient on TAU means the CBT arm did better. Two markers of a strong analysis: (1) the agent recognizes the within-patient dependence without being told, and (2) it treats the dropout from 100 to \~52 patients thoughtfully rather than silently. If the coefficient on month comes back near −0.7 with a between-patient variance reported, the model is correct; if no random-effect variance appears, it likely fit OLS by mistake and ignored the repeated measures. |  |  |

# **Segment 2 — Psychometrics: the bfi Personality Items**

2,800 respondents answering 25 personality items (five 5-item scales). This is the workflow behind validating any symptom inventory or rating scale: **compute internal-consistency reliability, then examine factor structure**. It also contains a deliberate, highly teachable trap — reverse-keyed items — that punishes naive analysis.

### **Data-prep cell (paste first)**

| import statsmodels.api as sm bfi \= sm.datasets.get\_rdataset('bfi', 'psych').data bfi.to\_csv('bfi.csv', index=False) \# 5 scales: A=Agreeableness, C=Conscientiousness, E=Extraversion, \#           N=Neuroticism, O=Openness (items A1..A5, C1..C5, etc.) bfi.head() |
| :---- |

### **Directed prompt (paste into Gemini)**

|  *This is the bfi dataset: 25 personality items forming five 5-item scales — Agreeableness (A1–A5), Conscientiousness (C1–C5), Extraversion (E1–E5), Neuroticism (N1–N5), Openness (O1–O5). Some items are reverse-keyed. Please: (1) compute Cronbach’s alpha for each scale; (2) identify and correctly recode any reverse-keyed items, then recompute alpha and explain what changed; (3) test factor adequacy with the KMO measure and Bartlett’s test; and (4) run an exploratory factor analysis and report whether the items recover five interpretable factors.* |
| :---- |

### **Blind prompt (for the side-by-side)**

|  *Assess the reliability of these personality scales.* |
| :---- |

The blind version usually misses the reverse-keying. That failure is the lesson — see the answer key.

### **Answer key — the reverse-keying trap**

Cronbach’s alpha **before** vs. **after** correctly recoding reverse-keyed items. The jump is dramatic and is the single most memorable moment of the segment:

| Scale | Alpha (raw) | Alpha (recoded) |
| :---- | :---- | :---- |
| Agreeableness | 0.43 | 0.70 |
| Conscientiousness | −0.29 (\!) | 0.73 |
| Extraversion | −0.62 (\!) | 0.76 |
| Neuroticism | 0.81 | 0.81 (no reverse items) |
| Openness | −0.16 | 0.60 (modest — itself worth discussing) |
| **Facilitator note — land this point** Negative alphas are impossible for a coherent scale — they are a red flag that items are pointing in opposite directions. A clinician who trusted the raw numbers would wrongly conclude their instrument was worthless. Reverse-keyed items in this dataset include A1, C4, C5, E1, E2, O2, and O5. After recoding, four of five scales reach acceptable reliability. Openness stays modest (\~0.60) even when done correctly — a good prompt to discuss what alpha can and cannot tell you. |  |  |

### **Factor adequacy & structure**

| Test | Value | Interpretation |
| :---- | :---- | :---- |
| KMO (overall) | 0.85 | Well above 0.6 — sampling adequacy is good |
| Bartlett’s test | p \< 0.001 | Correlations exist — factor analysis is justified |
| Factors recovered | 5 | Items load onto the five expected trait factors |

# **Segment 3 — Survival: the Rossi Recidivism Data**

432 released prisoners followed for one year; the event is re-arrest. Structurally a perfect analog for **time to relapse or readmission after an intervention**: a time-to-event outcome with censoring (people who are never re-arrested during follow-up). Introduces Kaplan–Meier curves, the log-rank test, and Cox regression — and the concept of censoring, which many clinicians find genuinely useful.

### **Data-prep cell (paste first)**

| from lifelines.datasets import load\_rossi r \= load\_rossi() r.to\_csv('rossi.csv', index=False) \# week \= time to re-arrest; arrest \= event (1) vs censored (0) \# fin \= financial-aid treatment; plus age, prior offenses, etc. r.head() |
| :---- |

### **Directed prompt (paste into Gemini)**

|  *This is the Rossi recidivism dataset: 432 released prisoners followed for one year. ‘week’ is time to re-arrest and ‘arrest’ indicates whether re-arrest occurred (1) or the person was censored (0). ‘fin’ indicates whether they received financial aid. Treat this as a time-to-relapse problem. Please: (1) explain why survival analysis is needed and what censoring means here; (2) plot Kaplan–Meier survival curves comparing the financial-aid groups; (3) run a log-rank test between those groups; and (4) fit a Cox proportional-hazards model with the available covariates and interpret the hazard ratios, noting which predictors are significant.* |
| :---- |

### **Blind prompt (for the side-by-side)**

|  *Does financial aid reduce re-arrest in this dataset?* |
| :---- |

Watch whether the agent treats this as survival data or naively runs logistic regression / a t-test on ‘week’ — ignoring censoring is the classic mistake.

### **Answer key — Cox hazard ratios**

Hazard ratios (exp of coefficient); HR \< 1 means **lower** risk of re-arrest:

| Predictor | Hazard ratio | p | Reading |
| :---- | :---- | :---- | :---- |
| fin (financial aid) | 0.68 | 0.047 | \~32% lower re-arrest risk; just significant |
| age | 0.94 | 0.009 | Older → lower risk per year |
| prio (prior offenses) | 1.10 | 0.001 | Each prior raises risk \~10%; strongest effect |
| race / wexp / mar / paro | n.s. | \> 0.05 | Not significant here |
| **Facilitator note** The log-rank test for financial aid lands right at the edge: p ≈ 0.05. That is a gift for discussion — a borderline result that invites talk about effect size versus significance, the limits of a single trial, and why a hazard ratio (0.68) can be more informative than a p-value. The Cox model agrees (HR 0.68, p ≈ 0.047). Prior offenses are the most robust predictor. 114 of 432 people were re-arrested; the rest are censored — the exact feature that makes naive logistic regression inappropriate. |  |  |  |

# **Wrap-Up — Where the Agent Needs You (4 min)**

Pull the session together with the throughline the three answer keys were designed to demonstrate:

* **It writes and runs real code fast.** The agent handles boilerplate, plotting, and model-fitting end to end, and autocorrects its own errors — a genuine accelerator.

* **It does not supply statistical judgment.** Across the three tasks it can miss the repeated-measures structure, sail past reverse-keyed items, or ignore censoring unless the prompt names the design.

* **Verification is non-negotiable.** Because each dataset has a known answer, the room could check the agent rather than trust it — the habit to carry back to real research.

* **The prompt carries the expertise.** The directed vs. blind contrast shows that the quality of the analysis tracks the quality of the question, which is exactly the part faculty are equipped to supply.

**One-line closing**

*These agents turn a statistically literate researcher into a faster one — they do not turn the absence of statistical judgment into its presence. Keep a human who knows the design in the loop, and keep PHI out of the consumer tool.*