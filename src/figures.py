#!/usr/bin/env python3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLORS = {"tfidf": "#4C78A8", "svd100": "#F58518", "minilm": "#54A24B"}


def main() -> None:
    output = Path("figures")
    output.mkdir(exist_ok=True)
    results = pd.read_csv("data/processed/results.csv")
    pooled = results[results.scope == "pooled"].copy()
    order = ["tfidf", "svd100", "minilm"]
    pooled["model"] = pd.Categorical(pooled.model, order, ordered=True)
    pooled = pooled.sort_values("model")

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    positions = np.arange(len(pooled))
    errors = np.vstack([
        pooled.mean_difference - pooled.mean_ci_low,
        pooled.mean_ci_high - pooled.mean_difference,
    ])
    for index, (_, row) in enumerate(pooled.iterrows()):
        ax.errorbar(
            row.mean_difference, positions[index],
            xerr=[[errors[0, index]], [errors[1, index]]], fmt="none",
            ecolor=COLORS[str(row.model)], capsize=5, linewidth=2,
        )
    ax.scatter(pooled.mean_difference, positions, s=85, c=[COLORS[str(model)] for model in pooled.model], zorder=3)
    ax.axvline(0, color="#444444", linewidth=1, linestyle="--")
    ax.set_yticks(positions, ["TF-IDF", "SVD-100", "MiniLM"])
    ax.set_xlabel("Mean cosine-score difference: English-name mean - Chinese-name mean")
    ax.set_title("Name substitution changes raw similarity scores by model")
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    fig.savefig(output / "main_effect.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    categories = results[(results.scope != "pooled")].pivot(index="scope", columns="model", values="mean_difference")
    categories = categories.reindex(columns=order)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    image = ax.imshow(categories.values, cmap="RdBu_r", aspect="auto", vmin=-.012, vmax=.012)
    ax.set_xticks(range(3), ["TF-IDF", "SVD-100", "MiniLM"])
    ax.set_yticks(range(len(categories)), categories.index.str.title())
    for row in range(len(categories)):
        for column in range(3):
            ax.text(column, row, f"{categories.iloc[row, column]:+.4f}", ha="center", va="center", fontsize=9)
    ax.set_title("Exploratory category-level mean score differences")
    fig.colorbar(image, ax=ax, label="English - Chinese")
    fig.tight_layout()
    fig.savefig(output / "category_heatmap.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    robustness = pd.read_csv("data/processed/robustness.csv")
    matrix = robustness.pivot(index="setting", columns="model", values="mean_difference").reindex(columns=order)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for model in order:
        ax.plot(matrix.index, matrix[model], marker="o", label=model, color=COLORS[model])
    ax.axhline(0, color="#444444", linewidth=1, linestyle="--")
    ax.set_ylabel("Mean score difference")
    ax.set_title("Direction persists across split-sample and trimming checks")
    ax.tick_params(axis="x", rotation=18)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output / "robustness.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
