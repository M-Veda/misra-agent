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
        self.assertEqual(engine.enabled_rules(), 21)

        rules = engine.get_rules()
        self.assertEqual([rule.rule_id for rule in rules], ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "8.1", "7.7", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "9.1", "8.10", "9.2", "9.3", "8.14"])
        rule = rules[0]
        self.assertEqual(rule.chapter, "7")
        self.assertEqual(rule.category, "Expressions")
        self.assertEqual(rule.severity, "Required")
        self.assertFalse(rule.fixable)
        self.assertEqual(rule.priority, 25)
        self.assertIn("MISRA C:2012 Rule 7.1", rule.references)
        self.assertTrue(rule.rationale)

    def test_groups_rules_by_chapter(self):
        grouped = RuleEngine().rules_by_chapter()

        self.assertIn("8", grouped)
        self.assertEqual([rule.rule_id for rule in grouped["8"]], ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10", "8.14"])

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

    def test_rule_89_reports_file_scope_object_only_used_by_one_function(self):
        code = "int shared_value;\n\nint helper(void)\n{\n    return shared_value;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.9"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.9")
        self.assertIn("block scope", violation.explanation.lower())

    def test_rule_89_skips_objects_with_multiple_function_users(self):
        code = "int shared_value;\n\nint helper(void)\n{\n    return shared_value;\n}\n\nint other(void)\n{\n    return shared_value + 1;\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.9"])

        self.assertEqual(violations, [])

    def test_rule_810_reports_file_scope_function_only_called_by_one_function(self):
        code = "int helper(void);\n\nint helper(void)\n{\n    return 1;\n}\n\nint main(void)\n{\n    return helper();\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.10"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.10")
        self.assertIn("block scope", violation.explanation.lower())

    def test_rule_810_skips_functions_used_by_multiple_functions(self):
        code = "int helper(void);\n\nint helper(void)\n{\n    return 1;\n}\n\nint main(void)\n{\n    return helper();\n}\n\nint other(void)\n{\n    return helper();\n}\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.10"])

        self.assertEqual(violations, [])

    def test_rule_71_reports_octal_constants(self):
        code = "int value = 0123;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.1"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "7.1")
        self.assertIn("octal", violation.explanation.lower())

    def test_rule_71_ignores_decimal_and_hex_literals(self):
        code = "int decimal = 123;\nint hex = 0x7b;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.1"])

        self.assertEqual(violations, [])

    def test_rule_71_ignores_octal_literals_in_strings(self):
        code = 'const char *text = "0123";\n'
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.1"])

        self.assertEqual(violations, [])

    def test_rule_72_reports_unsigned_octal_and_hex_literals_without_suffix(self):
        code = "int value = 0x7f;\nint other = 0123;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.2"])

        self.assertEqual(len(violations), 2)
        self.assertTrue(all(violation.rule_id == "7.2" for violation in violations))
        self.assertTrue(all("unsigned" in violation.explanation.lower() for violation in violations))

    def test_rule_72_ignores_unsigned_octal_and_hex_literals_with_suffix(self):
        code = "int value = 0x7fu;\nint other = 0123u;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.2"])

        self.assertEqual(violations, [])

    def test_rule_72_ignores_decimal_literals(self):
        code = "int value = 127;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.2"])

        self.assertEqual(violations, [])

    def test_rule_73_reports_lowercase_long_suffixes(self):
        code = "long value = 123l;\nunsigned long other = 0x1full;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.3"])

        self.assertEqual(len(violations), 2)
        self.assertTrue(all(violation.rule_id == "7.3" for violation in violations))
        self.assertTrue(all("lowercase" in violation.explanation.lower() for violation in violations))

    def test_rule_73_ignores_uppercase_long_suffixes(self):
        code = "long value = 123L;\nunsigned long other = 0x1fUL;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.3"])

        self.assertEqual(violations, [])

    def test_rule_73_ignores_non_literal_suffixes(self):
        code = 'const char *text = "123l";\n'
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.3"])

        self.assertEqual(violations, [])

    def test_rule_74_reports_string_literal_initialization_of_non_const_objects(self):
        code = 'char *message = "hello";\n'
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.4"])

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "7.4")
        self.assertIn("string literal", violations[0].explanation.lower())

    def test_rule_74_ignores_const_string_literal_initialization(self):
        code = 'const char *message = "hello";\n'
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.4"])

        self.assertEqual(violations, [])

    def test_rule_74_ignores_non_literal_initialization(self):
        code = 'char *message = other;\n'
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.4"])

        self.assertEqual(violations, [])

    def test_rule_75_reports_character_literal_initialization_of_non_const_objects(self):
        code = "char value = 'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.5"])

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "7.5")
        self.assertIn("character literal", violations[0].explanation.lower())

    def test_rule_75_ignores_const_character_literal_initialization(self):
        code = "const char value = 'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.5"])

        self.assertEqual(violations, [])

    def test_rule_75_ignores_non_literal_initialization(self):
        code = "char value = 88;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.5"])

        self.assertEqual(violations, [])

    def test_rule_76_reports_multi_character_literals(self):
        code = "int value = 'ab';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.6"])

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "7.6")
        self.assertIn("multi-character", violations[0].explanation.lower())

    def test_rule_76_ignores_single_character_literals(self):
        code = "int value = 'a';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.6"])

        self.assertEqual(violations, [])

    def test_rule_76_ignores_escaped_character_literals(self):
        code = "int value = '\\n';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.6"])

        self.assertEqual(violations, [])

    def test_rule_77_reports_wide_character_literals(self):
        code = "wchar_t value = L'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.7"])

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "7.7")
        self.assertIn("wide-character", violations[0].explanation.lower())

    def test_rule_77_ignores_regular_character_literals(self):
        code = "char value = 'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.7"])

        self.assertEqual(violations, [])

    def test_rule_77_ignores_const_wide_character_literals(self):
        code = "const wchar_t value = L'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.7"])

        self.assertEqual(violations, [])

    def test_rule_76_and_rule_77_execute_together(self):
        code = "int value = 'ab';\nwchar_t wide = L'x';\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["7.6", "7.7"])

        self.assertEqual({violation.rule_id for violation in violations}, {"7.6", "7.7"})

    def test_rule_814_reports_register_storage_class_specifier(self):
        code = "register int value = 1;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.14"])

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "8.14")
        self.assertIn("register", violation.explanation.lower())

    def test_rule_814_ignores_non_register_declarations(self):
        code = "int value = 1;\n"
        violations = RuleEngine().execute(code=code, file_path="unit.c", rule_ids=["8.14"])

        self.assertEqual(violations, [])

    def test_filters_disabled_rule(self):
        engine = RuleEngine(config={"disabled_rules": ["8.1"]})

        self.assertEqual(engine.enabled_rules(), 20)
        self.assertEqual(engine.execute("static int x = 1;\n", "unit.c"), [])
        self.assertEqual(
            [rule.rule_id for rule in engine.get_rules(include_disabled=True)],
            ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "8.1", "7.7", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "9.1", "8.10", "9.2", "9.3", "8.14"],
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

        self.assertEqual(rules[0]["rule_id"], "7.1")
        self.assertEqual(rules[0]["chapter"], "7")
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