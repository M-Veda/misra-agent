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

        self.assertGreaterEqual(len(session["violations"]), 1)

        accepted = 0

        while not review.status(session_id)["review_complete"]:
            current = review.current(session_id)

            if (
                current is not None
                and current.get("suggested_code")
                and current.get("auto_fixable", False)
            ):
                review.submit(session_id, "accept")
                accepted += 1
            else:
                review.submit(session_id, "skip")

        result = review.finalize(session_id)

        self.assertEqual(result["status"], "finished")
        self.assertTrue(len(result["final_code"]) > 0)
        self.assertEqual(
            result["compliance_report"]["accepted"],
            accepted,
        )
        self.assertEqual(
            result["compliance_report"]["applied_patches"],
            accepted,
        )

    def test_skip_generates_no_patch(self):
        session_id = "module-1-unit"
        source_path = PROJECT_ROOT / "input" / "sample.c"

        analysis = AnalysisService()
        review = ReviewService()

        analysis.start_analysis(session_id, str(source_path))

        while not review.status(session_id)["review_complete"]:
            review.submit(session_id, "skip")

        result = review.finalize(session_id)

        self.assertEqual(result["status"], "finished")
        self.assertEqual(result["progress"]["patches_ready"], 0)
        self.assertEqual(result["progress"]["skipped"], result["progress"]["reviewed"])
        self.assertNotIn("int main(void)", result["final_code"])

        report = result["compliance_report"]
        self.assertEqual(report["accepted"], 0)
        self.assertEqual(report["applied_patches"], 0)


if __name__ == "__main__":
    unittest.main()