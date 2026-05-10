"""Automated integration smoke test using the full pipeline runner."""

import unittest

from automated_tests.run_full_pipeline_check import run_check


class ResumeIQFullPipelineFastTests(unittest.TestCase):
    """Keep unittest discovery practical while the full 50-resume check remains available."""

    def test_offline_pipeline_smoke_with_real_resumes(self):
        summary = run_check("offline", limit=5)

        self.assertEqual(summary["resumes_uploaded"], 5)
        self.assertEqual(summary["candidates_created"], 5)
        self.assertEqual(summary["match_distribution_total"], 5)
        self.assertEqual(summary["semantic_distribution_total"], 5)
        self.assertEqual(summary["domain_distribution_total"], 5)
        self.assertGreaterEqual(summary["average_match"], 0)
        self.assertTrue(summary["top_skill"])


if __name__ == "__main__":
    unittest.main()
