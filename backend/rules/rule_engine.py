from collections import defaultdict
from datetime import datetime

from analyzer.analysis_context import AnalysisContext
from rules.execution_context import ExecutionContext
from config.settings import RULE_ENGINE_CONFIG
from models.violation import Violation
from rules.config import RuleEngineConfig
from rules.discovery import discover_rule_classes
from rules.registry import RuleRegistry
from utils.logger import logger
from rules.reporting import RuleReport
from rules.dependencies import RuleDependencyGraph
from rules.profiler import RuleProfiler
from rules.profile import profile_capabilities
from rules.parallel_executor import ParallelExecutor

class RuleEngine:
    """
    Plugin-based MISRA C:2012 Rule Engine.

    Responsibilities
    ----------------
    • Discover rule plugins
    • Load rule metadata
    • Execute enabled rules
    • Filter selected rules
    • Collect violations
    • Produce execution statistics
    """

    def __init__(self, config=None, packages=None, registry=None):
        self.config = self._build_config(config)
        self.packages = tuple(packages or ("rules",))
        self.registry = registry or RuleRegistry()
        self.last_execution = {}
        self.dependencies = RuleDependencyGraph()
        self.load_rules()
        self._build_dependencies()
        self.profiler = RuleProfiler()
        self.parallel_executor = ParallelExecutor()

    # ------------------------------------------------------------------
    # Rule Discovery
    # ------------------------------------------------------------------

    def load_rules(self):
        """Discover and register all rule plugins."""

        self.registry.clear()

        for package_name in self.packages:
            self._discover_package(package_name)

        logger.info(
            "Loaded %d MISRA rules.",
            len(self.registry),
        )

        return self.get_rule_classes(include_disabled=True)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_rules(self, include_disabled=False):
        return [
            rule.metadata()
            for rule in self.get_rule_classes(
                include_disabled=include_disabled
            )
        ]

    def get_rule_classes(self, include_disabled=False):
        classes = self.registry.all()

        if not include_disabled:
            classes = [
                rule
                for rule in classes
                if self.config.allows(
                    rule.metadata()
                )
            ]

        return sorted(
            classes,
            key=self._sort_key,
        )

    def get_rule(self, rule_id):
        rule = self.registry.get(rule_id)

        if rule is None:
            return None

        return rule.metadata()

    def rules_by_chapter(
        self,
        include_disabled=False,
    ):
        grouped = defaultdict(list)

        for rule in self.get_rule_classes(
            include_disabled=include_disabled
        ):
            grouped[
                rule.metadata().chapter
            ].append(
                rule.metadata()
            )

        return dict(grouped)

    def enabled_rules(self):
        return len(
            self.get_rule_classes()
        )

    def registered_rules(self):
        return len(self.registry)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
    self,
    code,
    file_path="",
    analysis_context=None,
    execution_context=None,
    rule_ids=None,
):
        """
        Execute all enabled rules.
        """

        started = datetime.now()

        if execution_context is None:
            from rules.execution_context import ExecutionContext
            execution_context = ExecutionContext()

        #
        # Build semantic analysis once.
        #
        needs_semantic = any(
    self.supports_semantic_analysis(rule)
    for rule in self.get_rule_classes()
)

        if analysis_context is None and needs_semantic:
            analysis_context = AnalysisContext(
        code=code,
        file_path=file_path,
    ).build()

        selected_rule_ids = (
            {str(rule) for rule in rule_ids}
            if rule_ids
            else None
        )

        violations = []
        report = RuleReport()

        execution_stats = {
            "started": started.strftime("%Y-%m-%d %H:%M:%S"),
            "executed": 0,
            "failed": 0,
            "skipped": 0,
            "violations": 0,
            "functions": 0,
            "declarations": 0,
            "identifiers": 0,
            "loops": 0,
            "conditionals": 0,
            "rules": [],
        }

        execution_stats["functions"] = (
    analysis_context.function_count
    if analysis_context
    else 0
)

        execution_stats["declarations"] = (
    analysis_context.declaration_count
    if analysis_context
    else 0
)

        execution_stats["identifiers"] = (
    analysis_context.identifier_count
    if analysis_context
    else 0
)

        execution_stats["loops"] = (
    analysis_context.loop_count
    if analysis_context
    else 0
)

        execution_stats["conditionals"] = (
    analysis_context.conditional_count
    if analysis_context
    else 0
)

        logger.info(
            "Starting rule execution."
        )

        def _run_rule(rule_class):
            metadata = rule_class.metadata()

            if (
        selected_rule_ids is not None
        and metadata.rule_id not in selected_rule_ids
    ):
                return None

            rule = rule_class()
            rule_started = self.profiler.start()

            execution_mode = (
        "semantic"
        if analysis_context is not None
        and any(
            capability in ("ast", "semantic", "hybrid")
            for capability in getattr(metadata, "capabilities", ())
        )
        else "text"
    )

            try:

                capabilities = set(getattr(metadata, "capabilities", ()))

                supports_context = (
            analysis_context is not None
            and capabilities.intersection(
                {"ast", "semantic", "hybrid"}
            )
        )

                if supports_context and hasattr(rule, "check_with_context"):

                    result = rule.check_with_context(
                code=code,
                file_path=file_path,
                analysis_context=analysis_context,
                execution_context=execution_context,
            )

                else:

                    result = rule.check(
                code=code,
                file_path=file_path,
            )

            except Exception:

                logger.exception(
            "Rule %s failed.",
            metadata.rule_id,
        )

                return {
            "failed": True,
            "metadata": metadata,
        }

            self.profiler.stop(
        metadata.rule_id,
        rule_started,
    )

            return {
        "failed": False,
        "metadata": metadata,
        "mode": execution_mode,
        "result": result,
    }
        
        jobs = [
    lambda rc=rule_class: _run_rule(rc)
    for rule_class in self.get_rule_classes()
]

        results = self.parallel_executor.execute(jobs)

        for item in results:

            if item is None:
                execution_stats["skipped"] += 1
                continue

            metadata = item["metadata"]

            if item["failed"]:
                execution_stats["failed"] += 1
                continue

            execution_stats["executed"] += 1

            result = item["result"]

            if result is None:
                continue

            if not isinstance(result, list):
                result = [result]

            rule_violation_count = 0

            for violation in result:

                violations.append(violation)
                report.add(violation)

                rule_violation_count += 1
                execution_stats["violations"] += 1

            execution_stats["rules"].append(
        {
            "rule_id": metadata.rule_id,
            "title": metadata.title,
            "violations": rule_violation_count,
            "severity": metadata.severity,
            "category": metadata.category,
            "mode": item["mode"],
        }
    )

        duration = (
            datetime.now() - started
        ).total_seconds()

        execution_stats[
            "duration_seconds"
        ] = round(
            duration,
            3,
        )

        execution_stats[
            "success_rate"
        ] = (
            round(
                (
                    execution_stats[
                        "executed"
                    ]
                    /
                    max(
                        execution_stats[
                            "executed"
                        ]
                        + execution_stats[
                            "failed"
                        ],
                        1,
                    )
                )
                * 100,
                2,
            )
        )

        execution_stats[
    "report"
] = report.summary()

        self.last_execution = execution_stats

        if analysis_context is not None:

            execution_stats["semantic_summary"] = {
        "functions": analysis_context.function_count,
        "declarations": analysis_context.declaration_count,
        "identifiers": analysis_context.identifier_count,
        "loops": analysis_context.loop_count,
        "conditionals": analysis_context.conditional_count,
    }
            
        execution_stats["coverage"] = {
    "registered_rules": self.registered_rules(),
    "enabled_rules": self.enabled_rules(),
    "executed_rules": execution_stats["executed"],
    "skipped_rules": execution_stats["skipped"],
}

        logger.info(
            "Rule execution completed. "
            "%d violations found.",
            len(violations),
        )

        return violations
    
    def supports_semantic_analysis(
        self,
        rule_class,
    ):
        """
        Returns True if the rule requires semantic analysis.
        """

        capabilities = set(
            rule_class.metadata().capabilities
        )

        return bool(
            capabilities.intersection(
                {
                    "ast",
                    "semantic",
                    "hybrid",
                }
            )
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def execution_summary(self):
        """
        Statistics from the latest execution.
        """

        return self.last_execution

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _discover_package(
        self,
        package_name,
    ):
        for rule_class in discover_rule_classes(
            (package_name,)
        ):
            self.registry.register(
                rule_class
            )

    @staticmethod
    def _build_config(config):

        if isinstance(
            config,
            RuleEngineConfig,
        ):
            return config

        if config is None:
            config = RULE_ENGINE_CONFIG

        return RuleEngineConfig.from_mapping(
            config
        )

    @staticmethod
    def _sort_key(rule_class):
        metadata = rule_class.metadata()

        return (
            metadata.priority,
            RuleEngine._rule_id_key(
                metadata.rule_id
            ),
        )

    @staticmethod
    def _rule_id_key(rule_id):

        key = []

        for part in rule_id.split("."):

            try:
                key.append(int(part))

            except ValueError:
                key.append(part)

        return tuple(key)
    
    def violations_by_chapter(
    self,
    violations,
):

        grouped = defaultdict(list)

        for violation in violations:
            chapter = violation.rule_id.split(".")[0]
            grouped[chapter].append(violation)

        return dict(grouped)
    
    def severity_summary(
    self,
    violations,
):

        summary = defaultdict(int)

        for violation in violations:
            summary[
            violation.severity
        ] += 1

        return dict(summary)
    
    def _build_dependencies(
    self,
):

    #
    # Type rules depend on declarations.
    #

        self.dependencies.add(
        "10.1",
        "8.1",
    )

        self.dependencies.add(
        "10.2",
        "8.1",
    )

        self.dependencies.add(
        "10.3",
        "8.1",
    )

        self.dependencies.add(
        "10.4",
        "8.1",
    )

    #
    # Initialization depends on declarations.
    #

        self.dependencies.add(
        "9.1",
        "8.1",
    )

        self.dependencies.add(
        "9.2",
        "8.1",
    )

        self.dependencies.add(
        "9.3",
        "8.1",
    )
