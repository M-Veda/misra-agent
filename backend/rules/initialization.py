import re

from rules.base_rule import BaseRule
from analyzer.initialization_analysis import (
    build_initialization_tracker,
)
from rules.rule_helpers import declaration_match, extract_declarators, extract_symbol, is_function_prototype, strip_comments

_ASSIGNMENT_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\b\s*=(?!=)")
_SYMBOL_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\b")
_IGNORE_SYMBOLS = {
    "if",
    "while",
    "for",
    "switch",
    "return",
    "sizeof",
    "const",
    "volatile",
    "static",
    "extern",
    "register",
    "unsigned",
    "signed",
    "short",
    "long",
    "int",
    "char",
    "float",
    "double",
    "_Bool",
    "bool",
    "struct",
    "union",
    "enum",
}


class Rule91(BaseRule):
    RULE_ID = "9.1"
    TITLE = "Objects shall be initialized before use"
    CHAPTER = "9"
    CATEGORY = "Initialization"
    SEVERITY = "Required"
    DESCRIPTION = "Objects shall be initialized before their value is used."
    RATIONALE = "Using initialized data prevents undefined behavior and improves program safety."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 9.1",)
    PRIORITY = 34
    CAPABILITIES = (
    "text",
    "semantic",
)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}

    def _shared_check(
    self,
    code,
    file_path,
    tracker,
):
        """
    Shared implementation used by both the
    text and semantic entry points.
    """

        violations = []

        for line_number, raw_line in enumerate(
        code.splitlines(),
        start=1,
    ):

            line = strip_comments(raw_line)

            declaration_match_result = declaration_match(
            line
        )

            if declaration_match_result:

                declaration = declaration_match_result.group(
                "decl"
            )

                if is_function_prototype(
                declaration
            ):
                    continue

                for declarator in extract_declarators(
                declaration
            ):

                    symbol = extract_symbol(
                    declarator
                )

                    if not symbol:
                        continue

                    if "=" in declarator:
                        tracker.assign(
                        symbol,
                        line=line_number,
                    )
                    else:
                        tracker.declare(
    declarator,
    line=line_number,
)

                continue

            for assignment_match in _ASSIGNMENT_PATTERN.finditer(
            line
        ):

                symbol = assignment_match.group(1)

                if symbol not in _IGNORE_SYMBOLS:
                    tracker.assign(
                    symbol,
                    line=line_number,
                )

            tokens = [
            token
            for token in _SYMBOL_PATTERN.findall(
                line
            )
            if token not in _IGNORE_SYMBOLS
        ]

            for token in tokens:

                tracker.use(
                token,
                line=line_number,
            )

                if tracker.initialized_state(
                token
            ):
                    continue

                if re.search(
                rf"\b{re.escape(token)}\b\s*=(?!=)",
                line,
            ):
                    continue

                if re.search(
                rf"sizeof\s*\(\s*{re.escape(token)}\b",
                line,
            ):
                    continue

                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line.strip(),
                    explanation=(
                        "Object may be used before "
                        "initialization."
                    ),
                )
            )

                break

        return violations

    def check(
    self,
    code,
    file_path,
):
        tracker = build_initialization_tracker(
        code
    )

        return self._shared_check(
        code,
        file_path,
        tracker,
    )
    def check_with_context(
    self,
    code,
    file_path,
    analysis_context,
    execution_context=None,
):
        tracker = (
        analysis_context.initialization_tracker
        if (
            analysis_context
            and analysis_context.initialization_tracker
        )
        else build_initialization_tracker(
            code
        )
    )

        return self._shared_check(
        code,
        file_path,
        tracker,
    )

    
class Rule92(Rule91):
    RULE_ID = "9.2"
    TITLE = "Object value shall not be read before being set"
    CHAPTER = "9"
    CATEGORY = "Initialization"
    SEVERITY = "Required"
    DESCRIPTION = "The value of an object shall not be read before it has been set."
    RATIONALE = "Reading uninitialized values can lead to unpredictable behavior."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 9.2",)
    PRIORITY = 35
    CAPABILITIES = (
    "text",
    "semantic",
)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}


class Rule93(Rule91):
    RULE_ID = "9.3"
    TITLE = "Full objects shall not be read unless initialized"
    CHAPTER = "9"
    CATEGORY = "Initialization"
    SEVERITY = "Required"
    DESCRIPTION = "A full object shall not be read unless it has been initialized."
    RATIONALE = "Full object reads before initialization may access indeterminate memory."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 9.3",)
    PRIORITY = 36
    CAPABILITIES = (
    "text",
    "semantic",
)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}
