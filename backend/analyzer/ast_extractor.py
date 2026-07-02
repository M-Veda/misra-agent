from analyzer.analysis_context import AnalysisContext
from analyzer.ast_visitor import ASTVisitor
from analyzer.cfg_builder import CFGBuilder
from analyzer.clang_parser import ClangParser
from analyzer.symbol_table import SymbolTableBuilder
from analyzer.type_analyzer import TypeAnalyzer
from analyzer.declaration_model import Declaration


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
            context.declarations = self._declarations_from_visitor(context.visitor)
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
        context.declarations = self._declarations_from_visitor(context.visitor)
        context.symbol_table = self.symbol_builder.build(context)
        context.type_information = self.type_analyzer.analyze(context)
        context.cfg = self.cfg_builder.build(context)
        return context

    def _declarations_from_visitor(self, visitor):
        declarations = []
        for declaration in getattr(visitor, "find_declarations", lambda: [])():
            if isinstance(declaration, Declaration):
                declarations.append(declaration)
                continue
            if isinstance(declaration, dict):
                declarations.append(
                    Declaration(
                        kind=declaration.get("kind", "unknown"),
                        name=declaration.get("name"),
                        type_name=declaration.get("type_name"),
                        storage_specifiers=tuple(declaration.get("storage_specifiers", [])),
                        qualifiers=tuple(declaration.get("qualifiers", [])),
                        is_bit_field=declaration.get("is_bit_field", False),
                        bit_width=declaration.get("bit_width"),
                        line=declaration.get("line"),
                        column=declaration.get("column"),
                        signedness=declaration.get("signedness"),
                        alias_of=declaration.get("alias_of"),
                    )
                )
        return declarations