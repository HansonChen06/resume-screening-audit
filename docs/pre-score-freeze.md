# Pre-score Freeze

Frozen on 2026-08-28 before any model score was computed.

## Corpus

- retained JDs: 269
- rejected candidates: 53
- category counts: SWE 70, data 60, consulting 43, product 60, unclassified 36
- `data/raw/jds.csv` SHA-256: `dbb07e1f28f5dd099651a459cb3bd0b614025c430317e4a4a42b4019b3c446b8`
- collection providers: local ApplyPilot, Greenhouse Job Board API, Lever Postings API

## Resume

- `data/base_resume.txt` SHA-256: `44fc3bd096b3ee45c8b8c510e81c9272e190f734354dbb70bfa52f75ff243cf5`
- direct personal contact details replaced with inert placeholders
- displayed name is the only confirmatory manipulation

## Models

- TF-IDF: scikit-learn 1.5.2, word 1-2 grams, sublinear term frequency
- rank-100 SVD: scikit-learn 1.5.2 TruncatedSVD on the frozen TF-IDF feature matrix
- sentence model: `sentence-transformers/all-MiniLM-L6-v2`, immutable revision
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, sentence-transformers 3.2.1

The original MATH 308 co-occurrence matrix was not recovered. The rank-100
model therefore preserves the course project's truncation and cosine-scoring
method but is fitted to this frozen audit corpus. It is not the original course
embedding and is labelled `svd100` throughout.

## Determinism

- global random seed: 42
- bootstrap resamples: 2,000
- paired permutation/sign-flip draws: 10,000
- floating-point tolerance for repeated embeddings: `1e-7`

