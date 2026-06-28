from analyzer.analysis_context import AnalysisContext
from analyzer.ast_visitor import ASTVisitor
from analyzer.cfg_builder import CFGBuilder
from analyzer.clang_parser import ClangParser
from analyzer.symbol_table import SymbolTableBuilder
from analyzer.type_analyzer import TypeAnalyzer


class ASTExtractor:
    def __init__(self):
        self.parser = ClangParser()
        self.symbol_builder = SymbolTableBuilder()
        self.type_analyzer = TypeAnalyzer()
        self.cfg_builder = CFGBuilder()

    def extract(self, file_path):
        try:
            parsed = self.parser.parse(file_path)
            context = AnalysisContext(
                file_path=file_path,
                source_code=parsed.get("source", ""),
                available=True,
                ast=parsed,
                visitor=ASTVisitor(ast=parsed),
            )
            context.visitor.visit(parsed)
            context.symbol_table = self.symbol_builder.build(context)
            context.type_information = self.type_analyzer.analyze(context)
            context.cfg = self.cfg_builder.build(context)
            return context
        except Exception as exc:
            return AnalysisContext(
                file_path=file_path,
                source_code="",
                available=False,
                parse_error=str(exc),
                visitor=ASTVisitor(),
            )

    def extract_from_source(self, source_code):
        context = AnalysisContext(file_path="<memory>", source_code=source_code, available=True, ast={"source": source_code}, visitor=ASTVisitor(ast={"source": source_code}))
        context.visitor.visit(context.ast)
        context.symbol_table = self.symbol_builder.build(context)
        context.type_information = self.type_analyzer.analyze(context)
        context.cfg = self.cfg_builder.build(context)
        return context