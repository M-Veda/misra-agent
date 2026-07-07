from datetime import datetime

from analyzer.analysis_context import AnalysisContext
from analyzer.ast_visitor import ASTVisitor
from analyzer.cfg_builder import CFGBuilder
from analyzer.clang_parser import ClangParser
from analyzer.symbol_table import SymbolTableBuilder
from analyzer.type_analyzer import TypeAnalyzer
from utils.logger import logger


class ASTExtractor:
    """
    Builds the complete semantic analysis context.

    Pipeline
    --------
        Source
            ↓
        Clang Parser
            ↓
        AST Visitor
            ↓
        Symbol Table
            ↓
        Type Analysis
            ↓
        CFG Builder
            ↓
        AnalysisContext
    """

    def __init__(self):
        self.parser = ClangParser()
        self.symbol_builder = SymbolTableBuilder()
        self.type_analyzer = TypeAnalyzer()
        self.cfg_builder = CFGBuilder()

    def extract(self, file_path):
        logger.info(
            "Starting AST extraction: %s",
            file_path,
        )

        started = datetime.now()

        try:
            parsed = self.parser.parse(file_path)

            context = self._build_context(
                file_path=file_path,
                source_code=parsed.get(
                    "source",
                    "",
                ),
                parsed=parsed,
                available=True,
            )

            context.metadata = {
                "started_at": started.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "duration_ms": (
                    datetime.now() - started
                ).total_seconds()
                * 1000,
                "parser": "clang",
            }

            logger.info(
                "AST extraction finished."
            )

            return context

        except Exception as exc:

            logger.exception(
                "AST extraction failed."
            )

            context = AnalysisContext(
                file_path=file_path,
                source_code="",
                available=False,
                parse_error=str(exc),
                visitor=ASTVisitor(),
            )

            context.metadata = {
                "started_at": started.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "parser": "clang",
                "status": "failed",
            }

            return context

    def extract_from_source(
        self,
        source_code,
    ):
        return self._build_context(
            file_path="<memory>",
            source_code=source_code,
            parsed={
                "source": source_code
            },
            available=True,
        )

    def _build_context(
        self,
        file_path,
        source_code,
        parsed=None,
        available=True,
        parse_error=None,
    ):
        visitor = ASTVisitor(
            ast=parsed
        )

        visitor.visit(parsed)

        context = AnalysisContext(
            file_path=file_path,
            source_code=source_code,
            available=available,
            ast=parsed,
            visitor=visitor,
            parse_error=parse_error,
            declarations=getattr(
                visitor,
                "declarations",
                [],
            ),
        )

        context.symbol_table = (
            self.symbol_builder.build(
                context
            )
        )

        context.type_information = (
            self.type_analyzer.analyze(
                context
            )
        )

        context.cfg = self.cfg_builder.build(
            context
        )

        context.statistics = visitor.statistics()

        return context