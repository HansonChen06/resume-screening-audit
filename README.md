# Resume Screening Semantic-Match Sensitivity Audit

**Question:** How sensitive is cosine-similarity resume screening to variables that should not change evidence of job qualification?

**Main figure:** Pending preregistered analysis; the final README will show the effect-size forest plot here.

**Answer:** Not yet known. No experimental result will be stated until the preregistered pipeline has run.

This repository will contain a controlled, reproducible audit connecting the
SVD word-embedding methods used in MATH 308 with real job descriptions captured
through ApplyPilot. It is a research artifact, not a screening product or a
reproduction of a commercial applicant-tracking system.

## Status

- Stage 0: scope and completion criteria defined
- Stage 1: MATH 308 baseline reconstructed; resume claims corrected
- Stage 2: ApplyPilot export, cleaning, deduplication, and quality checks implemented; real corpus currently empty
- Audit hypotheses: preregistered at commit `8f1e3be565d61676f96caadf14440f17206bf5c1`; implementation has not started
- Audit analysis: not started

## Completion criteria

The project is complete only when:

- the README opens with one question, one main figure, and one evidence-backed answer;
- `make all` rebuilds every processed dataset, result, figure, and the report from documented raw inputs;
- the PDF report contains Abstract, Methods, Results, Limitations, and Conclusion sections;
- every confirmatory conclusion includes an effect size, confidence interval, and the preregistered multiple-comparison correction;
- `HYPOTHESES.md` is committed before any audit analysis code or result inspection; and
- a clean environment reproduces the committed outputs with fixed dependency versions and seeds.

## Explicit non-goals

- No web interface
- No REST API
- No database or user system
- No Docker orchestration
- No "platform" framing
- No claim that cosine similarity reproduces a commercial ATS

> If I am writing UI, I have left the research question.

## Planned stages

1. Recover and verify the original MATH 308 baseline and resume claims.
2. Export, clean, deduplicate, and document the ApplyPilot JD corpus.
3. Lock the design, power analysis, exclusions, outcomes, and hypotheses in Git.
4. Validate the measurement instrument with positive and negative controls.
5. Run the controlled variants across TF-IDF, SVD, and a modern sentence embedding.
6. Report paired effects, uncertainty, multiplicity correction, and robustness checks.
7. Deliver a tested one-command pipeline and a 6-8 page report.

## Export the local JD corpus

```bash
python3 scripts/export_jds.py \
  --input /Users/sihanchen/Desktop/ApplyPilot-MVP/data/data.json
```

The command writes ignored, local-only files under `data/raw/`: the retained
corpus, a rejection ledger, and a quality report. It never modifies ApplyPilot.
Run the current data-stage tests with:

```bash
python3 -m unittest discover -s tests -v
```
