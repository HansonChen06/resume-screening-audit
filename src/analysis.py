#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from score import paired_cohens_d


def bootstrap_ci(values, statistic, rng, draws=2000):
    array = np.asarray(values, dtype=float)
    estimates = []
    for _ in range(draws):
        sample = rng.choice(array, size=len(array), replace=True)
        estimates.append(statistic(sample))
    return tuple(float(x) for x in np.percentile(estimates, [2.5, 97.5]))


def sign_flip_p(values, rng, draws=10000):
    array = np.asarray(values, dtype=float)
    observed = abs(array.mean())
    simulated = np.empty(draws)
    for index in range(draws):
        simulated[index] = abs((array * rng.choice([-1, 1], size=len(array))).mean())
    return float((np.count_nonzero(simulated >= observed) + 1) / (draws + 1))


def name_differences(frame, model, category=None):
    subset = frame[(frame.model == model) & (frame.variable == "name")]
    if category:
        subset = subset[subset.jd_category == category]
    means = subset.groupby(["jd_id", "level"], as_index=False).score.mean()
    pivot = means.pivot(index="jd_id", columns="level", values="score").dropna()
    return (pivot["english"] - pivot["chinese"]).to_numpy()


def summarize(differences, model, scope, rng):
    values = np.asarray(differences)
    t_result = stats.ttest_1samp(values, 0.0)
    raw_ci = stats.t.interval(0.95, len(values) - 1, loc=values.mean(), scale=stats.sem(values))
    d_ci = bootstrap_ci(values, paired_cohens_d, rng)
    try:
        wilcoxon_p = float(stats.wilcoxon(values).pvalue)
    except ValueError:
        wilcoxon_p = 1.0
    return {
        "analysis": "name_group_difference",
        "model": model,
        "scope": scope,
        "n_jds": len(values),
        "mean_difference": float(values.mean()),
        "mean_ci_low": float(raw_ci[0]),
        "mean_ci_high": float(raw_ci[1]),
        "cohens_dz": paired_cohens_d(values),
        "dz_ci_low": d_ci[0],
        "dz_ci_high": d_ci[1],
        "p_value": float(t_result.pvalue),
        "p_adjusted": np.nan,
        "wilcoxon_p": wilcoxon_p,
        "sign_flip_p": sign_flip_p(values, rng),
        "mean_absolute_difference": float(np.abs(values).mean()),
        "fraction_abs_over_0_01": float((np.abs(values) > 0.01).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("data/processed/scores.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/results.csv"))
    parser.add_argument("--robustness", type=Path, default=Path("data/processed/robustness.csv"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    frame = pd.read_csv(args.scores)
    rng = np.random.default_rng(args.seed)
    models = ["tfidf", "svd100", "minilm"]
    rows = [summarize(name_differences(frame, model), model, "pooled", rng) for model in models]
    adjusted = multipletests([row["p_value"] for row in rows], method="fdr_bh")[1]
    for row, value in zip(rows, adjusted):
        row["p_adjusted"] = float(value)
    for model in models:
        for category in ("swe", "data", "consulting", "product", "unclassified"):
            differences = name_differences(frame, model, category)
            if len(differences) >= 20:
                rows.append(summarize(differences, model, category, rng))
    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)

    robustness_rows = []
    for model in models:
        full = name_differences(frame, model)
        for label, values in (
            ("full_sample", full),
            ("first_half", full[: len(full) // 2]),
            ("second_half", full[len(full) // 2 :]),
            ("trimmed_2_5pct", full[(full >= np.quantile(full, .025)) & (full <= np.quantile(full, .975))]),
        ):
            robustness_rows.append({
                "model": model, "setting": label, "n": len(values),
                "mean_difference": float(np.mean(values)),
                "cohens_dz": paired_cohens_d(values),
                "direction": "english_higher" if np.mean(values) > 0 else "chinese_higher" if np.mean(values) < 0 else "zero",
            })
    pd.DataFrame(robustness_rows).to_csv(args.robustness, index=False)
    print(output[output.scope == "pooled"].to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
