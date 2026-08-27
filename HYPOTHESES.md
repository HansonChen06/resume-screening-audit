# Preregistered Hypotheses

Status: locked before implementation of embedding, scoring, variant-generation,
or outcome-analysis code.

## Scope

This experiment audits a simplified cosine-similarity instrument. It does not
test a commercial applicant-tracking system, employer behavior, callbacks, or
hiring discrimination. The confirmatory estimand is sensitivity of a model score
to a controlled name substitution when qualification evidence is unchanged.

## Experimental unit

The independent experimental unit is a retained job description (JD). Multiple
names and models evaluated against the same JD are repeated measurements, not
independent observations.

The audit will not begin until all of the following are recorded in a design-only
amendment committed before any model score is computed:

- SHA-256 of the frozen base-resume text;
- SHA-256 of the retained `jds.csv`;
- final retained JD count and exclusion counts;
- versions and immutable identifiers of all embedding models; and
- the random seed used for any ordered or sampled operation.

## Confirmatory hypothesis

For each retained JD and embedding model, compute the mean resume-to-JD cosine
score across eight English-name variants and across eight Chinese-name variants.
Let the paired difference be:

`difference_jd = mean(English-name scores) - mean(Chinese-name scores)`.

- **H0:** The population mean paired difference is zero.
- **H1:** The population mean paired difference is not zero.

The hypothesis is two-sided. No direction is preregistered.

## Outcomes

### Primary outcome

Mean paired score difference by JD for the frozen modern sentence-embedding
model.

### Secondary outcomes

- The same paired difference for TF-IDF.
- The same paired difference for the reconstructed MATH 308 SVD embedding.
- Absolute raw score change by JD.
- Fraction of JDs whose absolute difference exceeds 0.01 cosine-score units.
- Name-level dispersion within each name group.

### Exploratory outcomes

- Differences by JD category.
- Sensitivity to institution and graduation-year substitutions.
- Sensitivity to wording and document-length variants.
- Interaction between document length and absolute name-group difference.

Institution, year, wording, and length analyses will not be described as tests
of discrimination because those manipulations may alter relevant information or
the amount of qualification evidence.

## Sample size and stopping rule

A two-sided paired t-test power calculation with paired standardized effect
`d_z = 0.20`, alpha `0.05`, and power `0.80` requires 198.1513 pairs; therefore
the collection target is **199 retained JDs**.

Collection stops at the first quality-gated export containing at least 199
retained JDs. All records in that frozen export are analyzed; records are not
removed based on scores or significance. If 199 retained JDs are infeasible,
the study will be reported as underpowered and the minimum detectable effect for
the achieved sample will be reported. The target effect will not be changed to
justify a smaller sample after scoring begins.

## Exclusions

JD exclusions are determined before scoring:

- missing description;
- fewer than 80 words after documented cleaning;
- duplicate normalized source URL;
- exact duplicate cleaned content;
- 5-token-shingle Jaccard similarity of at least 0.90 to an earlier retained JD;
- non-job pages or descriptions where responsibilities/qualifications cannot be
  recovered on manual review.

Ambiguous categories remain `unclassified`; category ambiguity is not grounds
for exclusion from the pooled confirmatory test.

## Statistical analysis

- Primary test: two-sided paired t-test over the 199 or more JD-level group-mean
  differences.
- Raw effect: mean paired cosine-score difference.
- Standardized effect: paired Cohen's `d_z = mean(difference) / sd(difference)`.
- Uncertainty: 95% confidence intervals for both raw difference and `d_z`, with
  JD as the resampling unit for bootstrap intervals.
- Multiplicity: Benjamini-Hochberg correction across the three prespecified
  model-level name comparisons. Both raw and corrected p-values are reported.
- Sensitivity analysis: paired permutation/sign-flip test and Wilcoxon signed-rank
  result, reported alongside rather than substituted for the primary test.

Normality tests will not be used to choose a more favorable confirmatory test.
No test will be replaced after results are observed.

## Positive and negative controls

Before interpreting the main experiment, each matcher must pass documented
controls:

- engineering resume scores above an unrelated nursing resume on SWE JDs;
- a resume scores higher against a faithful paraphrase of a relevant JD than
  against an unrelated JD;
- repeated embedding of identical input is exactly deterministic within the
  declared numeric tolerance; and
- identity-only changes leave the guarded matcher unchanged when identity fields
  are explicitly excluded.

A matcher that fails controls is marked invalid and excluded from substantive
interpretation. Its failure remains reported.

## Reporting discipline

- Null results remain null results.
- No new exclusions are introduced after scoring.
- Exploratory analyses are labeled exploratory.
- Score sensitivity is not described as employer discrimination or real hiring
  impact.
- Every confirmatory claim includes raw effect, `d_z`, 95% CI, raw p-value, and
  corrected p-value.

