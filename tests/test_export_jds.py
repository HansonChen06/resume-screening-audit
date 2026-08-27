import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_jds import (  # noqa: E402
    clean_description,
    export_records,
    infer_category,
    normalize_url,
    source_date,
)


class ExportJdsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = ROOT / "tests" / "fixtures" / "applypilot_sample.json"
        cls.applications = json.loads(fixture.read_text())["applications"]

    def test_tracking_parameters_are_removed(self):
        self.assertEqual(
            normalize_url("https://EXAMPLE.test/jobs/1/?utm_source=x&keep=yes#top"),
            "https://example.test/jobs/1?keep=yes",
        )

    def test_boilerplate_sections_are_removed(self):
        cleaned = clean_description(self.applications[0]["description"])
        self.assertIn("Responsibilities", cleaned)
        self.assertIn("Qualifications", cleaned)
        self.assertNotIn("changes the world", cleaned)
        self.assertNotIn("Salary range", cleaned)

    def test_short_and_duplicate_records_are_rejected(self):
        records, rejections = export_records(self.applications)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["category"], "swe")
        reasons = [item.reason for item in rejections]
        self.assertTrue(
            any(
                reason == "duplicate_url" or reason.startswith("duplicate_content")
                for reason in reasons
            )
        )
        self.assertTrue(any(reason.startswith("too_short") for reason in reasons))

    def test_ambiguous_titles_remain_unclassified(self):
        self.assertEqual(infer_category("AI Product Manager"), "unclassified")

    def test_capture_date_precedes_legacy_creation_fallback(self):
        self.assertEqual(source_date(self.applications[0]), "2026-08-19")
        self.assertEqual(
            source_date({"createdAt": "2026-08-20T12:00:00.000Z"}),
            "2026-08-20",
        )


if __name__ == "__main__":
    unittest.main()
