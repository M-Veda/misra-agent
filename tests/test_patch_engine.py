import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.final_code_service import FinalCodeService
from services.patch_service import PatchService
from services.review_service import ReviewService


class PatchEngineModule3Test(unittest.TestCase):
    def setUp(self):
        self.service = PatchService()

    def test_text_patch_strategy_applies_replacement(self):
        patch = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="Use explicit void parameter",
        )

        code = "int main()\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [patch])

        self.assertIn("int main(void)", result)
        self.assertTrue(patch.applied)
        self.assertEqual(patch.status, "applied")

    def test_regex_patch_strategy_applies_with_pattern_metadata(self):
        patch = self.service.create_patch(
            violation=self._violation("return 0;", "return 1;", line_number=2),
            replacement_code="return 1;",
            strategy="regex_patch",
            description="Replace return value",
            metadata={"regex_pattern": r"return\s+0;", "regex_replacement": "return 1;"},
        )

        code = "int main(void)\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [patch])

        self.assertIn("return 1;", result)
        self.assertTrue(patch.applied)

    def test_conflict_detection_marks_overlapping_patch(self):
        first = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="First patch",
        )
        second = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="Second patch",
        )

        code = "int main()\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [first, second])

        self.assertIn("int main(void)", result)
        self.assertEqual(first.status, "applied")
        self.assertEqual(second.status, "conflicted")
        self.assertIn("conflict", second.conflict_reason.lower())

    def test_rollback_restores_previous_code(self):
        patch = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="Use explicit void parameter",
        )

        code = "int main()\n{\n    return 0;\n}\n"
        applied_code = self.service.apply_patches(code, [patch])
        restored_code = self.service.rollback_patch(applied_code, patch)

        self.assertEqual(restored_code, code)
        self.assertEqual(patch.status, "rolled_back")

    def test_patch_queue_and_history_are_recorded(self):
        patch = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="manual_patch",
            description="Manual patch",
        )

        session = {"patch_queue": [], "patch_history": []}
        self.service.enqueue_patch(session, patch)

        self.assertEqual(len(session["patch_queue"]), 1)
        self.assertEqual(session["patch_queue"][0]["patch_id"], patch.patch_id)
        self.assertEqual(len(session["patch_history"]), 1)

    def test_deterministic_execution_order_across_multiple_patches(self):
        first = self.service.create_patch(
            violation=self._violation("return 0;", "return 1;", line_number=2),
            replacement_code="return 1;",
            strategy="regex_patch",
            description="Return value change",
            metadata={"regex_pattern": r"return\s+0;", "regex_replacement": "return 1;"},
        )
        second = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="Prototype change",
        )

        code = "int main()\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [first, second])

        self.assertIn("int main(void)", result)
        self.assertIn("return 1;", result)
        self.assertEqual(first.status, "applied")
        self.assertEqual(second.status, "applied")

    def test_multiline_conflict_is_detected(self):
        first = self.service.create_patch(
            violation=self._violation("int main()\n{\n    return 0;\n}", "int main(void)\n{\n    return 1;\n}", line_number=1),
            replacement_code="int main(void)\n{\n    return 1;\n}",
            strategy="ast_patch",
            description="Multiline change",
            metadata={"ast_replacement": "int main(void)\n{\n    return 1;\n}"},
        )
        second = self.service.create_patch(
            violation=self._violation("return 0;", "return 2;", line_number=3),
            replacement_code="return 2;",
            strategy="text_patch",
            description="Conflicting change",
        )

        code = "int main()\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [first, second])

        self.assertIn("int main(void)", result)
        self.assertEqual(second.status, "conflicted")

    def test_failure_recovery_does_not_break_subsequent_patches(self):
        failing = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="regex_patch",
            description="Will fail",
            metadata={},
        )
        valid = self.service.create_patch(
            violation=self._violation("return 0;", "return 1;", line_number=2),
            replacement_code="return 1;",
            strategy="regex_patch",
            description="Valid patch",
            metadata={"regex_pattern": r"return\s+0;", "regex_replacement": "return 1;"},
        )

        code = "int main()\n{\n    return 0;\n}\n"
        result = self.service.apply_patches(code, [failing, valid])

        self.assertIn("return 1;", result)
        self.assertEqual(failing.status, "conflicted")
        self.assertEqual(valid.status, "applied")

    def test_review_and_final_code_service_integration(self):
        review = ReviewService()
        final_code = FinalCodeService()

        session_id = "module-3-integration"
        session = {
            "session_id": session_id,
            "patch_queue": [],
            "patch_history": [],
            "patches": [],
            "violations": [],
            "decisions": [],
            "current_index": 0,
            "status": "building",
            "original_code": "int main()\n{\n    return 0;\n}\n",
        }
        patch = self.service.create_patch(
            violation=self._violation("int main()", "int main(void)", line_number=1),
            replacement_code="int main(void)",
            strategy="text_patch",
            description="Prototype update",
        )
        review.patch_service.enqueue_patch(session, patch)
        session["patches"].append(patch)
        final_code_text = final_code.generate(session["original_code"], session["patches"], session=session)

        self.assertIn("int main(void)", final_code_text)
        self.assertEqual(len(session["patch_history"]), 2)

    def _violation(self, original_code, suggested_code, line_number):
        return type(
            "ViolationStub",
            (),
            {
                "violation_id": "v-1",
                "rule_id": "8.1",
                "title": "Prototype",
                "description": "Prototype issue",
                "severity": "Required",
                "category": "Declarations",
                "file_path": "unit.c",
                "line_number": line_number,
                "column_number": 0,
                "original_code": original_code,
                "suggested_code": suggested_code,
                "explanation": "Use explicit void",
                "auto_fixable": True,
                "confidence": 1.0,
                "fix_strategy": "",
                "patch_id": "",
                "metadata": {},
            },
        )()


if __name__ == "__main__":
    unittest.main()
