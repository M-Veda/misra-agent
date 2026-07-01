import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from analyzer.analysis_context import AnalysisContext
from models.violation import Violation
from rules.base_rule import BaseRule
from rules.config import RuleEngineConfig
from rules.registry import RuleRegistry
from rules.rule_engine import RuleEngine
from services.rule_service import RuleService


class RuleEngineModule2Test(unittest.TestCase):
    def test_discovers_registered_rule_metadata(self):
        engine = RuleEngine()

        self.assertGreaterEqual(engine.registered_rules(), 1)
        self.assertEqual(engine.enabled_rules(), 11)

        rules = engine.get_rules()
        self.assertEqual([rule.rule_id for rule in rules], ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "9.1", "9.2", "9.3"])
        rule = rules[0]
        self.assertEqual(rule.chapter, "8")
        self.assertEqual(rule.category, "Declarations and definitions")
        self.assertEqual(rule.severity, "Required")
        self.assertTrue(rule.fixable)
        self.assertEqual(rule.priority, 30)
        self.assertIn("MISRA C:2012 Rule 8.1", rule.references)
        self.assertTrue(rule.rationale)

    def test_groups_rules_by_chapter(self):
        grouped = RuleEngine().rules_by_chapter()

        self.assertIn("8", grouped)
        self.assertEqual([rule.rule_id for rule in grouped["8"]], ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8"])

    def test_executes_enabled_rules_and_returns_violations(self):
        code = "int main()\n{\n    return 0;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c")

        self.assertEqual(len(violations), 2)
        self.assertEqual({violation.rule_id for violation in violations}, {"8.1", "8.7"})
        violation = next(v for v in violations if v.rule_id == "8.1")
        self.assertIsInstance(violation, Violation)
        self.assertEqual(violation.original_code, "int main()")
        self.assertEqual(violation.suggested_code, "int main(void)")
        self.assertTrue(violation.auto_fixable)
        self.assertEqual(violation.fix_strategy, "prototype_void_parameter")
        self.assertEqual(violation.metadata["chapter"], "8")
        self.assertEqual(violation.metadata["priority"], 30)

    def test_rule_82_reports_missing_parameter_names(self):
        code = "int sum(int, int);\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.2"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.2")
        self.assertIn("parameter names", violation.explanation.lower())

    def test_rule_83_reports_inconsistent_declarations(self):
        code = "int value;\nconst int value;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.3"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.3")
        self.assertIn("type", violation.explanation.lower())

    def test_rule_83_ignores_consistent_declarations(self):
        code = "int value;\nextern int value;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.3"])

        self.assertEqual(violations, [])

    def test_rule_84_reports_pointer_array_parameters(self):
        code = "void process(int *data);\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.4"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.4")
        self.assertIn("array notation", violation.explanation.lower())

    def test_rule_85_reports_repeated_external_declarations(self):
        code = "int shared_value;\nint shared_value;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.5"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.5")
        self.assertIn("one and only one", violation.explanation.lower())

    def test_rule_85_ignores_static_internal_declarations(self):
        code = "static int shared_value;\nstatic int shared_value;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.5"])

        self.assertEqual(violations, [])

    def test_rule_87_reports_external_linkage(self):
        code = "int global_value;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.7"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.7")
        self.assertIn("external linkage", violation.explanation.lower())

    def test_rule_86_reports_shadowed_outer_scope_identifiers(self):
        code = "int value = 1;\nvoid helper(void)\n{\n    int value = 2;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.6"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.6")
        self.assertIn("shadow", violation.explanation.lower())

    def test_rule_88_reports_internal_linkage_without_static(self):
        code = "int helper(void)\n{\n    return 0;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.8"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.8")
        self.assertIn("static", violation.explanation.lower())

    def test_filters_disabled_rule(self):
        engine = RuleEngine(config={"disabled_rules": ["8.1"]})

        self.assertEqual(engine.enabled_rules(), 10)
        self.assertEqual(engine.execute("static int x = 1;\n", "unit.c"), [])
        self.assertEqual(
            [rule.rule_id for rule in engine.get_rules(include_disabled=True)],
            ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "9.1", "9.2", "9.3"],
        )

    def test_filters_by_enabled_rule_and_chapter(self):
        enabled = RuleEngine(config={"enabled_rules": ["8.1"], "enabled_chapters": ["8"]})
        disabled_by_chapter = RuleEngine(config={"enabled_chapters": ["9"]})

        self.assertEqual(enabled.enabled_rules(), 1)
        self.assertEqual(disabled_by_chapter.enabled_rules(), 3)

    def test_rule_83_and_rule_85_execute_with_context(self):
        code = "int value;\nconst int value;\nint shared_value;\nint shared_value;\n"
        context = AnalysisContext(file_path="unit.c", source_code=code, available=True)
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.3", "8.5"], analysis_context=context)

        self.assertEqual(len(violations), 3)
        self.assertTrue(all(violation.metadata.get("analysis_available") for violation in violations))

    def test_registry_rejects_duplicate_rule_ids(self):
        class RuleA(BaseRule):
            RULE_ID = "99.1"
            TITLE = "Synthetic rule"
            CHAPTER = "99"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Synthetic test rule."

            def check(self, code, file_path):
                return []

        class RuleB(RuleA):
            pass

        registry = RuleRegistry()
        registry.register(RuleA)

        with self.assertRaises(ValueError):
            registry.register(RuleB)

    def test_registry_requires_base_rule_subclasses(self):
        registry = RuleRegistry()

        with self.assertRaises(TypeError):
            registry.register(object)

    def test_engine_rejects_non_violation_results(self):
        class BadRule(BaseRule):
            RULE_ID = "98.1"
            TITLE = "Bad synthetic rule"
            CHAPTER = "98"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Returns invalid results for engine contract testing."

            def check(self, code, file_path):
                return {"not": "a violation"}

        engine = RuleEngine(config={"enabled_rules": []})
        engine.registry.clear()
        engine.registry.register(BadRule)

        with self.assertRaises(TypeError):
            engine.execute("", "unit.c")

    def test_rule_service_serializes_metadata(self):
        service = RuleService()
        rules = service.get_rules()
        grouped = service.get_rules_by_chapter()

        self.assertEqual(rules[0]["rule_id"], "8.1")
        self.assertEqual(rules[0]["chapter"], "8")
        self.assertIn("8", grouped)
        self.assertEqual(grouped["8"][0]["rule_id"], "8.1")

    def test_rule_engine_config_mapping_normalizes_filters(self):
        config = RuleEngineConfig.from_mapping({"disabled_rules": ["8.1", ""], "enabled_chapters": ["8"]})
        rule = RuleEngine().get_rule("8.1")

        self.assertFalse(config.allows(rule))

    def test_metadata_validation_rejects_unknown_capabilities(self):
        class InvalidCapabilityRule(BaseRule):
            RULE_ID = "97.1"
            TITLE = "Invalid capability rule"
            CHAPTER = "97"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Used to verify capability validation."
            CAPABILITIES = ("invalid",)

            def check(self, code, file_path):
                return []

        with self.assertRaises(ValueError):
            InvalidCapabilityRule.metadata()

    def test_discovers_new_rule_plugins_from_package(self):
        engine = RuleEngine(packages=("tests.rules.sample_plugin",))

        self.assertTrue(any(rule.rule_id == "99.1" for rule in engine.get_rules(include_disabled=True)))

    def test_executes_ast_aware_text_and_hybrid_rules(self):
        class ASTAwareRule(BaseRule):
            RULE_ID = "90.1"
            TITLE = "AST aware rule"
            CHAPTER = "90"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Exercises AST-aware execution."
            CAPABILITIES = ("ast",)

            def check(self, code, file_path):
                return []

            def check_with_context(self, code, file_path, analysis_context=None):
                return [self.create_violation(file_path=file_path, line=1, original=code.strip(), metadata={"analysis_available": bool(analysis_context and analysis_context.available)})]

        class TextRule(BaseRule):
            RULE_ID = "90.2"
            TITLE = "Text rule"
            CHAPTER = "90"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Exercises text-only execution."
            CAPABILITIES = ("text",)

            def check(self, code, file_path):
                return [self.create_violation(file_path=file_path, line=1, original=code.strip())]

        class HybridRule(BaseRule):
            RULE_ID = "90.3"
            TITLE = "Hybrid rule"
            CHAPTER = "90"
            CATEGORY = "Synthetic"
            SEVERITY = "Required"
            DESCRIPTION = "Exercises hybrid execution."
            CAPABILITIES = ("text", "ast")

            def check(self, code, file_path):
                return []

            def check_with_context(self, code, file_path, analysis_context=None):
                return [self.create_violation(file_path=file_path, line=1, original=code.strip(), metadata={"hybrid": True, "analysis_available": bool(analysis_context and analysis_context.available)})]

        engine = RuleEngine(config={"enabled_rules": []})
        engine.registry.clear()
        engine.registry.register(ASTAwareRule)
        engine.registry.register(TextRule)
        engine.registry.register(HybridRule)

        context = AnalysisContext(file_path="unit.c", source_code="int main() { return 0; }", available=True)
        violations = engine.execute("int main() { return 0; }", "unit.c", analysis_context=context)

        self.assertEqual(len(violations), 3)
        self.assertEqual({violation.rule_id for violation in violations}, {"90.1", "90.2", "90.3"})
        self.assertTrue(any(violation.metadata.get("analysis_available") for violation in violations))
        self.assertTrue(any(violation.metadata.get("hybrid") for violation in violations))


if __name__ == "__main__":
    unittest.main()