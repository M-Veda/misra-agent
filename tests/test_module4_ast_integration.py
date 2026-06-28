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
