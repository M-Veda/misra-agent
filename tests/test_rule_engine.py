import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

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
        self.assertEqual(engine.enabled_rules(), 1)

        rules = engine.get_rules()
        self.assertEqual([rule.rule_id for rule in rules], ["8.1"])
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
        self.assertEqual([rule.rule_id for rule in grouped["8"]], ["8.1"])

    def test_executes_enabled_rules_and_returns_violations(self):
        code = "int main()\n{\n    return 0;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c")

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIsInstance(violation, Violation)
        self.assertEqual(violation.rule_id, "8.1")
        self.assertEqual(violation.original_code, "int main()")
        self.assertEqual(violation.suggested_code, "int main(void)")
        self.assertTrue(violation.auto_fixable)
        self.assertEqual(violation.fix_strategy, "prototype_void_parameter")
        self.assertEqual(violation.metadata["chapter"], "8")
        self.assertEqual(violation.metadata["priority"], 30)

    def test_filters_disabled_rule(self):
        engine = RuleEngine(config={"disabled_rules": ["8.1"]})

        self.assertEqual(engine.enabled_rules(), 0)
        self.assertEqual(engine.execute("int main()\n", "unit.c"), [])
        self.assertEqual([rule.rule_id for rule in engine.get_rules(include_disabled=True)], ["8.1"])

    def test_filters_by_enabled_rule_and_chapter(self):
        enabled = RuleEngine(config={"enabled_rules": ["8.1"], "enabled_chapters": ["8"]})
        disabled_by_chapter = RuleEngine(config={"enabled_chapters": ["9"]})

        self.assertEqual(enabled.enabled_rules(), 1)
        self.assertEqual(disabled_by_chapter.enabled_rules(), 0)

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


if __name__ == "__main__":
    unittest.main()