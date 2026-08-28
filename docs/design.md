# Experimental Design

## Research design

The audit uses counterfactual resume variants: hold all qualification evidence
fixed, change only the displayed applicant name, and compare the resulting score
against the same JD. The design borrows controlled attribute substitution from
resume audit studies while measuring algorithmic score sensitivity rather than
employer callbacks.

## Name sets

The confirmatory name sets are copied from Table 2A of Philip Oreopoulos's 2011
Canadian resume audit. They are not generated from intuition or selected after
observing model output.

### English-name group

1. Greg Johnson
2. John Martin
3. Matthew Wilson
4. Michael Smith
5. Alison Johnson
6. Carrie Martin
7. Emily Brown
8. Jill Wilson

### Chinese-name group

1. Dong Liu
2. Lei Li
3. Tao Wang
4. Yong Zhang
5. Fang Wang
6. Min Liu
7. Na Li
8. Xiuying Zhang

These labels describe how the names were operationalized in the cited study;
they do not establish an individual's ethnicity. Sex balance is four names per
sex in each group, following the source table. The main analysis averages names
within group for each JD so individual names are not treated as independent
samples.

## Power calculation

Parameters fixed before score generation:

- design: paired, two-sided;
- minimum detectable standardized paired effect: `d_z = 0.20`;
- alpha: `0.05`;
- power: `0.80`;
- independent unit: JD.

R command:

```r
power.t.test(
  delta = 0.2,
  sd = 1,
  sig.level = 0.05,
  power = 0.8,
  type = "paired",
  alternative = "two.sided"
)
```

The result is `n = 198.1513`, rounded up to **199 retained JDs**. Eight names in
each group improve the estimate of each JD's group mean but do not increase the
number of independent JD pairs.

The earlier planning target of 100 JDs is insufficient for the preregistered
minimum effect under this calculation.

## JD corpus

The corpus comes from the user's real ApplyPilot captures. Cleaning, exclusions,
deduplication, source-date lineage, and privacy rules are defined in
`data/README.md` and implemented in `scripts/export_jds.py`.

The pooled confirmatory analysis includes `unclassified` titles. Category-level
analyses are exploratory and are only displayed for categories with at least 20
retained JDs; this threshold is a reporting floor, not a claim of adequate power.

## Base resume

One engineering-oriented resume will be normalized to plain text and frozen.
Before scoring, its path-independent SHA-256 hash will be added to a design-only
amendment. Apart from the named manipulation, every byte of the base text must
remain identical across confirmatory variants.

Contact information other than the displayed name will use inert placeholders.
No real phone number, email address, street address, or application identifier is
included in committed fixtures or model inputs.

## Models

1. TF-IDF baseline.
2. Rank-100 SVD text embedding using the same truncation-and-cosine method as
   MATH 308, fitted to the frozen audit corpus because the original
   co-occurrence matrix was not recovered.
3. Frozen `sentence-transformers/all-MiniLM-L6-v2` revision recorded in
   `docs/pre-score-freeze.md`.

Exact package and model revisions are locked in the pre-score amendment. A model
cannot be silently upgraded during the experiment.

## Sources

- Bertrand, M., and Mullainathan, S. (2004). "Are Emily and Greg More
  Employable Than Lakisha and Jamal?" *American Economic Review*, 94(4),
  991-1013. https://doi.org/10.1257/0002828042002561
- Oreopoulos, P. (2011). "Why Do Skilled Immigrants Struggle in the Labor
  Market? A Field Experiment with Thirteen Thousand Resumes." *American
  Economic Journal: Economic Policy*, 3(4), 148-171.
  https://doi.org/10.1257/pol.3.4.148
- Statsmodels `TTestPower` documentation for one-sample and paired-sample power
  calculations: https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestPower.html
