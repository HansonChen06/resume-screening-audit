#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from embed import sentence_embeddings, svd_embeddings, tfidf_embeddings
from score import cosine_scores
from variants import generate_variants


def write_scores(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jds", type=Path, default=Path("data/raw/jds.csv"))
    parser.add_argument("--resume", type=Path, default=Path("data/base_resume.txt"))
    parser.add_argument("--nursing", type=Path, default=Path("data/nursing_control.txt"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/scores.csv"))
    parser.add_argument("--controls", type=Path, default=Path("data/processed/controls.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    jds = pd.read_csv(args.jds).sort_values("jd_id").reset_index(drop=True)
    variants = generate_variants(args.resume.read_text(encoding="utf-8"))
    nursing = args.nursing.read_text(encoding="utf-8")
    texts = jds["text"].fillna("").tolist() + [item.text for item in variants] + [nursing]
    jd_count = len(jds)
    variant_count = len(variants)

    tfidf, _ = tfidf_embeddings(texts)
    svd, svd_model = svd_embeddings(tfidf, args.seed)
    modern, _ = sentence_embeddings(texts)
    matrices = {"tfidf": tfidf, "svd100": svd, "minilm": modern}

    rows = []
    controls = {"seed": args.seed, "jd_count": jd_count, "variant_count": variant_count, "models": {}}
    swe_mask = jds["category"].eq("swe").to_numpy()
    baseline_index = jd_count
    nursing_index = jd_count + variant_count
    for model_name, matrix in matrices.items():
        jd_matrix = matrix[:jd_count]
        variant_matrix = matrix[jd_count:jd_count + variant_count]
        scores = cosine_scores(variant_matrix, jd_matrix)
        for v_index, variant in enumerate(variants):
            metadata = variant.metadata()
            for jd_index, jd in jds.iterrows():
                rows.append({
                    **metadata,
                    "jd_id": jd.jd_id,
                    "jd_category": jd.category,
                    "model": model_name,
                    "score": float(scores[v_index, jd_index]),
                })
        repeat = cosine_scores(matrix[baseline_index:baseline_index + 1], matrix[baseline_index:baseline_index + 1])[0, 0]
        nurse_scores = cosine_scores(matrix[nursing_index:nursing_index + 1], jd_matrix)[0]
        base_scores = scores[0]
        controls["models"][model_name] = {
            "deterministic_identity_score": float(repeat),
            "swe_resume_mean": float(base_scores[swe_mask].mean()),
            "swe_nursing_mean": float(nurse_scores[swe_mask].mean()),
            "positive_control_pass": bool(base_scores[swe_mask].mean() > nurse_scores[swe_mask].mean()),
        }
    controls["svd_explained_variance"] = float(svd_model.explained_variance_ratio_.sum())
    write_scores(args.output, rows)
    args.controls.parent.mkdir(parents=True, exist_ok=True)
    args.controls.write_text(json.dumps(controls, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(controls, indent=2))


if __name__ == "__main__":
    main()
