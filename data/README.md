# Job-description data

## Source

`data/raw/jds.csv` combines the local ApplyPilot store with a frozen snapshot of
live public postings from the documented Greenhouse Job Board and Lever
Postings APIs, as authorized by `docs/amendment-01-public-ats.md`. Source files
are read-only during export. Raw full text, URLs, application notes, resume
choices, and other private job-search state are not committed to Git.

New ApplyPilot records preserve the browser extension's `capturedAt` timestamp.
For legacy records that lack it, `source_date` falls back to the ApplyPilot
record creation date. Neither value proves the employer's original posting date.

## Output schema

| Field | Meaning |
|---|---|
| `jd_id` | Stable hash derived from normalized source URL or record identity |
| `company` | Employer name from ApplyPilot or the public ATS feed |
| `title` | Posting title from ApplyPilot or the public ATS feed |
| `category` | Deterministic title heuristic: swe/data/consulting/product/unclassified |
| `text` | Conservatively cleaned responsibilities and qualifications text |
| `word_count` | Token count after cleaning |
| `source_date` | Capture date, or legacy record creation date when capture time is absent |

## Cleaning and exclusion rules

- Normalize whitespace and URL tracking parameters.
- Remove clearly headed company, compensation, benefits, EEO, accommodation,
  legal, privacy, and application-process sections.
- Retain responsibilities, qualifications, skills, and experience sections.
- Reject missing descriptions and cleaned descriptions under 80 words.
- Remove exact duplicates and near-duplicates with 5-token-shingle Jaccard
  similarity of at least 0.90.
- Keep ambiguous title categories as `unclassified`; never force a label.

`jd_rejections.csv` records every rejected source record and reason.
`quality_report.json` records accepted counts, category counts, limitations, and
whether every planned category has at least 20 retained descriptions.

## Privacy and version control

The repository ignores all files under `data/raw/`. Tests use obviously
synthetic `.test` domains in `tests/fixtures/`; fixture records must never be
included in the research corpus.
