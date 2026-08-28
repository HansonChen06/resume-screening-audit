import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from embed import svd_embeddings, tfidf_embeddings  # noqa: E402


class EmbedTest(unittest.TestCase):
    def test_sparse_and_svd_embeddings_are_deterministic(self):
        docs = ["python sql data", "nursing patient care", "react software api"]
        first, _ = tfidf_embeddings(docs)
        second, _ = tfidf_embeddings(docs)
        np.testing.assert_allclose(first.toarray(), second.toarray(), atol=0)
        svd_a, _ = svd_embeddings(first, seed=42, rank=2)
        svd_b, _ = svd_embeddings(first, seed=42, rank=2)
        np.testing.assert_allclose(svd_a, svd_b, atol=1e-12)


if __name__ == "__main__":
    unittest.main()

