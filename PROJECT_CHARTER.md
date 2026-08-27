# Project Charter

## Research question

How sensitive is a simplified resume-to-job semantic similarity score to
controlled changes in identity cues, institution, graduation year, wording,
and document length when qualification evidence is otherwise held fixed?

## Why this project exists

The work extends a MATH 308 exercise on low-rank word embeddings, cosine
similarity, analogy evaluation, and gender-direction projections into a
controlled audit over real job descriptions collected during an actual job
search. The contribution is the experimental design and its limits, not a
claim that the matcher is production hiring software.

## Definition of done

1. The original MATH 308 metrics cited on current resumes are reproduced or
   corrected with an auditable record.
2. The JD corpus has documented provenance, cleaning, exclusions,
   deduplication, and category counts.
3. Confirmatory hypotheses and statistical choices are committed before audit
   model scores or outcome analysis are inspected.
4. Positive controls establish that each retained matcher measures job-domain
   relevance; negative controls establish deterministic execution.
5. Confirmatory results report paired raw effects, paired standardized effects,
   95% confidence intervals, and corrected p-values.
6. Robustness checks show which conclusions survive alternative models,
   similarities, aggregation choices, subsamples, and outlier rules.
7. `make clean && make all` reproduces the final figures and PDF report.

## Stop conditions

- If the JD corpus cannot meet the preregistered sample-size or category rules,
  reduce the claim or redesign before scoring variants.
- If a matcher fails its positive control, exclude or revise it before the main
  experiment; do not interpret its bias results.
- If the original resume metrics cannot be reproduced, remove or correct them
  before continuing the new audit.
- If a result is not significant, report it under the preregistered method; do
  not switch tests to search for significance.

## Non-goals

The project will not include UI work, service APIs, accounts, databases,
orchestration, automated hiring decisions, or product/platform language.

