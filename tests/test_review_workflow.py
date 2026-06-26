import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.analysis_service import AnalysisService
from services.review_service import ReviewService


class InteractiveReviewWorkflowTest(unittest.TestCase):
    def tearDown(self):
        for path in (
            PROJECT_ROOT / "fixed_code" / "module-1-unit.c",
            PROJECT_ROOT / "reports" / "module-1-unit_compliance_report.json",
        ):
            if path.exists():
                path.unlink()

    def test_accept_applies_only_approved_patch_and_generates_report(self):
        session_id = "module-1-unit"
        source_path = PROJECT_ROOT / "input" / "sample.c"

        analysis = AnalysisService()
        review = ReviewService()

        session = analysis.start_analysis(session_id, str(source_path))
        self.assertEqual(len(session["violations"]), 1)
        current = review.current(session)
        self.assertEqual(current["rule_id"], "8.1")
        self.assertEqual(current["suggested_code"], "int main(void)")

        decision_response = review.submit(session_id, "accept")
        self.assertTrue(decision_response["review_complete"])
        self.assertEqual(decision_response["progress"]["accepted"], 1)

        result = review.finalize(session_id)
        self.assertEqual(result["status"], "finished")
        self.assertIn("int main(void)", result["final_code"])
        self.assertEqual(result["compliance_report"]["accepted"], 1)
        self.assertEqual(result["compliance_report"]["applied_patches"], 1)

    def test_skip_generates_no_patch(self):
        session_id = "module-1-unit"
        source_path = PROJECT_ROOT / "input" / "sample.c"

        analysis = AnalysisService()
        review = ReviewService()

        analysis.start_analysis(session_id, str(source_path))
        review.submit(session_id, "skip")
        result = review.finalize(session_id)

        self.assertEqual(result["progress"]["skipped"], 1)
        self.assertEqual(result["progress"]["patches_ready"], 0)
        self.assertNotIn("int main(void)", result["final_code"])


if __name__ == "__main__":
    unittest.main()
