from __future__ import annotations

import numpy as np


def cosine_scores(left, right) -> np.ndarray:
    product = left @ right.T
    return np.asarray(product.todense() if hasattr(product, "todense") else product)


def paired_cohens_d(differences) -> float:
    values = np.asarray(differences, dtype=float)
    sd = values.std(ddof=1)
    if sd == 0:
        return 0.0 if values.mean() == 0 else float(np.sign(values.mean()) * np.inf)
    return float(values.mean() / sd)

