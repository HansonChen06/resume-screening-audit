import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from score import paired_cohens_d  # noqa: E402


class ScoreTest(unittest.TestCase):
    def test_paired_effect_size_matches_hand_calculation(self):
        values = np.array([1.0, 2.0, 3.0])
        self.assertAlmostEqual(paired_cohens_d(values), 2.0)


if __name__ == "__main__":
    unittest.main()

