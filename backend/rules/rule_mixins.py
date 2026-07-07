"""
Reusable helpers for MISRA rule implementations.
"""

from rules.rule_helpers import (
    strip_comments,
    strip_string_literals,
)


class RuleMixin:
    """
    Shared helper methods for rule implementations.
    """

    @staticmethod
    def clean(line):
        return strip_string_literals(
            strip_comments(line)
        )

    @staticmethod
    def iter_lines(code):

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            yield (
                line_number,
                raw_line,
                RuleMixin.clean(raw_line),
            )

    @staticmethod
    def declaration_table(
        analysis_context,
    ):

        if analysis_context is None:
            return {}

        return analysis_context.declaration_table
