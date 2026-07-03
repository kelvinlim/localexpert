There are often situations where assistance with an LLM is desired but the data may be sensitive and not appropriate to utilize a cloud based LLM.

The purpose of this project is to examine how to use a local LLM on a laptop such as a Apple Silicon MacBookPro with 16gb or 32 gb running a local model such as Gemma4 or Qwen3.6.

Since these smaller models are limited in terms of knowledge, I'd like to explore the use of defined set of skills - for example, creating a set of skills that describe how to do a set of  standard tasks.

Another option could be fine tuning an existing open weights model on the set of tasks.

The preference is to use Python >= 3.12 using standard packages.

The use of jupyter notebooks to support transparency of documentation and code.

Two projects of interest:

1. A statistical analysis assistant that is familiar with a set of standard analyses.  This could be provided with skills that cover a different stages of common statistical analyses. See DataAnalysisPipeline.md for a potential pipeline.

2. A UMN finanace assistant that is familiar with UMN analytics and can assist in obtaining needed data.
