import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from models.patch import Patch
from services.patch_service import PatchService


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
