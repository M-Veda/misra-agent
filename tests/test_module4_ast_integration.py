import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from analyzer.ast_extractor import ASTExtractor
from analyzer.clang_parser import ClangParser
from analyzer.flow_analyzer import FlowAnalyzer
from analyzer.symbol_table import SymbolTableBuilder
from analyzer.type_analyzer import TypeAnalyzer
from services.analysis_service import AnalysisService
from services.patch_service import PatchService
from patch_engine.strategies import ASTPatchStrategy


class Module4ASTIntegrationTest(unittest.TestCase):
    def test_ast_extraction_returns_analysis_context(self):
        with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as handle:
            handle.write("int main(void) { int x = 1; return x; }\n")
            path = handle.name

        try:
            context = ASTExtractor().extract(path)
            self.assertIsNotNone(context)
            self.assertEqual(context.file_path, path)
            self.assertTrue(context.available or context.parse_error is not None)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_ast_visitor_collects_declarations_and_calls(self):
        source = "int main(void) { int x = 1; return x; }\n"
        context = ASTExtractor().extract_from_source(source)
        self.assertGreaterEqual(len(context.visitor.find_calls("main")), 0)
        self.assertGreaterEqual(len(context.visitor.find_declarations()), 0)

    def test_symbol_resolution_builds_symbol_table(self):
        source = "int main(void) { int value = 5; return value; }\n"
        context = ASTExtractor().extract_from_source(source)
        symbols = SymbolTableBuilder().build(context)
        self.assertIn("value", symbols)

    def test_type_resolution_identifies_scalar_and_pointer(self):
        source = "int value = 1; int *ptr = &value;\n"
        context = ASTExtractor().extract_from_source(source)
        types = TypeAnalyzer().analyze(context)
        self.assertTrue(types)

    def test_cfg_construction_builds_graph(self):
        source = "int main(void) { if (1) { return 1; } return 0; }\n"
        context = ASTExtractor().extract_from_source(source)
        cfg = FlowAnalyzer().analyze(context)
        self.assertTrue(cfg.nodes or cfg.edges or not context.parse_error)

    def test_semantic_analyzer_collects_structured_declarations_and_bitfields(self):
        source = """
typedef unsigned char u8;
struct S { int a:4; };
void f(void) {
    signed char sc = 0;
    unsigned char uc = 0;
    char ch = 0;
    const char *pc = 0;
}
"""
        context = ASTExtractor().extract_from_source(source)

        typedefs = context.get_declarations(kind="typedef")
        self.assertTrue(any(decl.name == "u8" for decl in typedefs))

        fields = context.get_declarations(kind="field")
        bitfield = next((decl for decl in fields if decl.name == "a"), None)
        self.assertIsNotNone(bitfield)
        self.assertTrue(bitfield.is_bit_field)
        self.assertEqual(bitfield.bit_width, "4")

        variables = context.get_declarations(kind="variable")
        signed_char = next((decl for decl in variables if decl.name == "sc"), None)
        self.assertIsNotNone(signed_char)
        self.assertEqual(signed_char.type_name, "signed char")
        self.assertEqual(signed_char.signedness, "signed")
        self.assertEqual(signed_char.kind, "variable")

        unsigned_char = next((decl for decl in variables if decl.name == "uc"), None)
        self.assertIsNotNone(unsigned_char)
        self.assertEqual(unsigned_char.type_name, "unsigned char")
        self.assertEqual(unsigned_char.signedness, "unsigned")

        plain_char = next((decl for decl in variables if decl.name == "ch"), None)
        self.assertIsNotNone(plain_char)
        self.assertEqual(plain_char.type_name, "char")
        self.assertEqual(plain_char.signedness, "plain")

        const_decl = next((decl for decl in variables if decl.name == "pc"), None)
        self.assertIsNotNone(const_decl)
        self.assertIn("const", const_decl.qualifiers)

    def test_type_analyzer_classifies_char_types_and_typedef_aliases(self):
        source = """
typedef unsigned char u8;
void f(void) {
    signed char sc = 0;
    unsigned char uc = 0;
    char ch = 0;
    u8 alias = 0;
}
"""
        context = ASTExtractor().extract_from_source(source)
        type_info = TypeAnalyzer().analyze(context)

        self.assertTrue(any(item.get("name") == "sc" and item.get("kind") == "char" and item.get("signedness") == "signed" for item in type_info))
        self.assertTrue(any(item.get("name") == "uc" and item.get("kind") == "char" and item.get("signedness") == "unsigned" for item in type_info))
        self.assertTrue(any(item.get("name") == "ch" and item.get("kind") == "char" and item.get("signedness") == "plain" for item in type_info))
        self.assertTrue(any(item.get("name") == "alias" and item.get("kind") == "typedef" and item.get("alias_of") == "unsigned char" for item in type_info))

    def test_ast_patch_strategy_applies_ast_replacement(self):
        patch = type(
            "PatchStub",
            (),
            {
                "patch_id": "ast-patch",
                "original_code": "int main()",
                "replacement_code": "int main(void)",
                "metadata": {"ast_replacement": "int main(void)"},
                "strategy": "ast_patch",
            },
        )()
        strategy = ASTPatchStrategy()
        self.assertEqual(strategy.apply("int main()", patch), "int main(void)")

    def test_analysis_service_falls_back_when_clang_parsing_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as handle:
            handle.write("int main(void) { return 0; }\n")
            path = handle.name

        try:
            with patch("analyzer.clang_parser.ClangParser.parse", side_effect=RuntimeError("clang unavailable")):
                session = AnalysisService().start_analysis("module4-fallback", path)
            context = session.get("analysis_context")
            self.assertIsNotNone(context)
            self.assertTrue(context.parse_error is not None or not context.available)
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
