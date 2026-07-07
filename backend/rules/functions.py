"""
MISRA C:2012 function rule plugins.

This module contains ONLY rule implementations.

Parsing, semantic analysis and query utilities live in:
    - function_parser.py
    - function_analysis.py
    - function_query.py
"""
from __future__ import annotations
import re

from rules.base_rule import BaseRule
from rules.function_parser import iter_functions
from rules.function_query import FunctionQuery
from rules.function_analysis import analyze_functions

# =========================================================
# Rule 8.4 (Foundation)
# =========================================================


class Rule84(BaseRule):
    """
    MISRA C:2012 Rule 8.4

    A compatible declaration shall be visible when an
    object or function with external linkage is defined.
    """

    RULE_ID = "8.4"

    TITLE = (
        "Compatible declaration shall be visible "
        "for externally linked functions"
    )

    CHAPTER = "8"

    CATEGORY = "Functions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Functions with external linkage should have a "
        "compatible declaration visible before the definition."
    )

    RATIONALE = (
        "Ensures consistent interfaces across translation units."
    )

    FIXABLE = False

    PRIORITY = 84

    CAPABILITIES = (
        "text",
        "ast",
    )

    def check(
        self,
        code,
        file_path,
    ):

        analysis = analyze_functions(code)

        query = FunctionQuery(analysis)

        violations = []

        for name in query.names():

            definition = query.definition(name)

            if definition is None:
                continue

            #
            # Static functions have internal linkage.
            #
            if definition.is_static:
                continue

            declaration = query.declaration(name)

            #
            # No visible declaration.
            #
            if declaration is None:

                line = code.splitlines()[
                    definition.line - 1
                ]

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=definition.line,
                        original=line,
                        suggestion=(
                            "Provide a compatible prototype before "
                            "the function definition."
                        ),
                        explanation=(
                            f"Function '{name}' has external linkage "
                            "but no visible declaration."
                        ),
                    )
                )

                continue

            #
            # Declaration exists but signatures differ.
            #
            if (
                declaration.parameters
                != definition.parameters
                or
                declaration.normalized_return_type
                != definition.normalized_return_type
            ):

                line = code.splitlines()[
                    definition.line - 1
                ]

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=definition.line,
                        original=line,
                        suggestion=(
                            "Ensure declaration and definition use "
                            "identical function signatures."
                        ),
                        explanation=(
                            f"Declaration of '{name}' is not "
                            "compatible with its definition."
                        ),
                    )
                )

        return violations

class Rule172(BaseRule):
    """
    MISRA C:2012 Rule 17.2

    Functions shall not call themselves,
    either directly or indirectly.
    """

    RULE_ID = "17.2"

    TITLE = "No recursion"

    CHAPTER = "17"

    CATEGORY = "Functions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Functions shall not be recursive."
    )

    RATIONALE = (
        "Recursive execution can produce "
        "unpredictable stack usage."
    )

    FIXABLE = False

    PRIORITY = 172

    CAPABILITIES = (
        "ast",
        "hybrid",
    )

    def check(
    self,
    code,
    file_path,
):

        violations = []

        function_match = re.search(
        r"""
        ([A-Za-z_][A-Za-z0-9_]*)
        \s*
        \(
        [^)]*
        \)
        \s*
        \{
        """,
        code,
        re.VERBOSE,
    )

        if function_match is None:
            return violations

        function_name = function_match.group(1)

        pattern = re.compile(
        rf"\b{re.escape(function_name)}\s*\("
    )

        matches = list(
        pattern.finditer(code)
    )

    #
    # one occurrence is declaration/definition
    # second occurrence means recursion
    #
        if len(matches) > 1:

            line = code[:matches[1].start()].count("\n") + 1

            violations.append(
            self.create_violation(
                file_path=file_path,
                line=line,
                original=code.splitlines()[line-1],
                suggestion=(
                    "Replace recursion with an "
                    "iterative solution."
                ),
                explanation=(
                    f"Function '{function_name}' "
                    f"is recursive."
                ),
            )
        )

        return violations

    def check_with_context(
        self,
        code,
        file_path,
        analysis_context=None,
        execution_context=None,
    ):

        if (
            analysis_context is None
            or analysis_context.ast is None
        ):
            return self.check(
                code,
                file_path,
            )

        visitor = getattr(
            analysis_context,
            "visitor",
            None,
        )

        if visitor is None:

            return []

        violations = []

        for function in visitor.recursive_functions():

            line = (
                function.line
                or 1
            )

            source_line = code.splitlines()[
                line - 1
            ]

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=source_line,
                    suggestion=(
                        "Replace recursion with an "
                        "iterative solution."
                    ),
                    explanation=(
                        f"Function '{function.name}' "
                        "is recursive."
                    ),
                )
            )

        return violations
    

__all__ = (
    "Rule84",
    "Rule172",
)
