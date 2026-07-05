import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from analyzer.ast_extractor import ASTExtractor
from analyzer.declaration_model import Declaration
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

    def test_analysis_context_exposes_canonical_declaration_metadata(self):
        source = "typedef unsigned char u8; static int counter;"
        extractor = ASTExtractor()
        context = extractor.extract_from_source(source)

        self.assertTrue(context.available)
        declarations = context.get_declarations()
        self.assertTrue(declarations)
        self.assertTrue(all(isinstance(decl, Declaration) for decl in declarations))
        self.assertIn("u8", context.typedefs)
        self.assertEqual(context.typedefs["u8"].type_name, "unsigned char")
        self.assertIn("counter", context.storage_classes)
        self.assertEqual(context.storage_classes["counter"], ("static",))
        self.assertIn("counter", context.qualifiers)
        self.assertIn("counter", context.signedness)


if __name__ == "__main__":
    unittest.main()
