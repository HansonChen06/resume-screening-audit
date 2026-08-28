import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analysis import name_differences  # noqa: E402


class PairingTest(unittest.TestCase):
    def test_pairs_within_jd_before_subtraction(self):
        rows = []
        for jd, english, chinese in (("a", 0.8, 0.3), ("b", 0.2, 0.4)):
            rows.extend([
                {"model":"tfidf", "variable":"name", "level":"english", "jd_category":"swe", "jd_id":jd, "score":english},
                {"model":"tfidf", "variable":"name", "level":"chinese", "jd_category":"swe", "jd_id":jd, "score":chinese},
            ])
        self.assertEqual(name_differences(pd.DataFrame(rows), "tfidf").tolist(), [0.5, -0.2])


if __name__ == "__main__":
    unittest.main()

