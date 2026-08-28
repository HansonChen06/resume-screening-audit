# Design Amendment 01: Public ATS Corpus Extension

Date: 2026-08-28

Status: to be committed before any embedding, score-generation, or outcome-analysis code.

## Reason

The preregistered target is 199 retained, independent job descriptions. The
user's ApplyPilot store contained two retained descriptions, and the currently
available authenticated McGill myFuture search exposed fewer than 199 postings.
Stopping there would make the confirmatory analysis materially underpowered.

## Amendment

The corpus may additionally include live public postings obtained from the
documented Greenhouse Job Board API and Lever Postings API. These endpoints are
the same public posting feeds used by employers' career sites and require no
applicant data or authentication.

The collector records employer, title, canonical posting URL, location,
retrieval timestamp, ATS provider, and full public description. The existing
pre-score exclusions remain unchanged: fewer than 80 cleaned words, duplicate
URL, exact duplicate content, or 5-token-shingle Jaccard similarity of at least
0.90. No record is selected using a model score.

Collection stops after the deterministic quality gate retains at least 199
records. To support exploratory stratification, deterministic title rules seek
at least 20 records in each of SWE, data, consulting, and product when the live
feeds contain enough eligible postings. Category is never used as a pooled
confirmatory exclusion.

## Consequences

- The pooled confirmatory estimand and independent unit remain unchanged.
- Source composition becomes a limitation because public ATS employers are not
  representative of all employers or all applicant experiences.
- Live feeds are time-varying. The frozen, provenance-bearing raw snapshot is
  the reproducibility input; re-fetching later is not expected to reproduce the
  same vacancies.

