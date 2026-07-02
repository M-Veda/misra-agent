import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rules.base_rule import BaseRule
from rules.rule_engine import RuleEngine
from services.analysis_service import AnalysisService


class ArchitectureImprovementsTest(unittest.TestCase):
    def test_rule_engine_continues_when_rule_raises_exception(self):
        class ExplodingRule(BaseRule):
            RULE_ID = "98.1"
            TITLE = "Exploding synthetic rule"
            CHAPTER = "98"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Used to verify rule failures do not abort the engine."

            def check(self, code, file_path):
                raise RuntimeError("boom")

        class HealthyRule(BaseRule):
            RULE_ID = "98.2"
            TITLE = "Healthy synthetic rule"
            CHAPTER = "98"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Used to verify the engine continues after a failure."

            def check(self, code, file_path):
                return [self.create_violation(file_path=file_path, line=1, original=code.strip())]

        engine = RuleEngine(config={"enabled_rules": []})
        engine.registry.clear()
        engine.registry.register(ExplodingRule)
        engine.registry.register(HealthyRule)

        violations = engine.execute("int main() { return 0; }", "unit.c")

        self.assertEqual([violation.rule_id for violation in violations], ["98.2"])

    def test_analysis_service_handles_invalid_utf8_input(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".c", delete=False) as handle:
            handle.write(b"\xff\xfe\x00")
            file_path = handle.name

        try:
            service = AnalysisService()
            session = service.start_analysis("invalid-utf8", file_path)
            self.assertEqual(session["session_id"], "invalid-utf8")
            self.assertIn("status", session)
            self.assertIsInstance(session["original_code"], str)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
