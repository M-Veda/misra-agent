"""
Production Analysis Pipeline.

Provides a single entry point for running MISRA analysis
from the CLI, API, tests, or any future UI.
"""

from pathlib import Path
from autofix.fix_engine import FixEngine
from analyzer.analysis_context import AnalysisContext
from rules.rule_engine import RuleEngine
from rules.execution_context import ExecutionContext
from autofix.fix_manager import FixManager
from cache.analysis_cache import AnalysisCache

class AnalysisPipeline:
    """
    Main MISRA analysis pipeline.

    Responsibilities
    ----------------
    • Read source code
    • Build semantic analysis context
    • Execute the rule engine
    • Return violations
    • Expose execution summary
    """

    def __init__(self):

        self.engine = RuleEngine()
        self.fix_engine = FixEngine()
        self.fix_manager = FixManager()
        self.cache = AnalysisCache()

    # ---------------------------------------------------------
    # Source Analysis
    # ---------------------------------------------------------

    def analyze_source(
    self,
    source,
    file_path="",
    rule_ids=None,
    profile="full",
):
        """
        Analyze C source code provided as a string.
        """

        context = self.cache.get(source)

        if context is None:

            context = AnalysisContext(
        code=source,
        file_path=file_path,
    ).build()

            self.cache.put(
        source,
        context,
    )

        execution_context = ExecutionContext(
    profile=profile,
)

        violations = self.engine.execute(
    source,
    file_path=file_path,
    analysis_context=context,
    rule_ids=rule_ids,
)

        return violations

    # ---------------------------------------------------------
    # File Analysis
    # ---------------------------------------------------------

    def analyze_file(
    self,
    file_path,
    rule_ids=None,
    profile="full",
):
        """
        Analyze a C source file.
        """

        source = Path(file_path).read_text(
            encoding="utf-8",
        )

        return self.analyze_source(
    source=source,
    file_path=str(file_path),
    rule_ids=rule_ids,
    profile=profile,
)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def execution_summary(self):
        """
        Return statistics from the latest execution.
        """

        return self.engine.execution_summary()
    
    def apply_fixes(
    self,
    source,
    violations,
):
        return self.fix_manager.apply_to_source(
        source,
        violations,
    )