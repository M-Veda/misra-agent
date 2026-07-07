"""
MISRA C:2012 Pointer Conversion rules.
"""

import re

from rules.base_rule import BaseRule
from rules.rule_mixins import RuleMixin
from analyzer.essential_types import (
    classify_type,
    pointer_compatible,
)
from analyzer.expression_analysis import (
    expression_type,
)

# ---------------------------------------------------------
# Common Patterns
# ---------------------------------------------------------

_POINTER_CAST_PATTERN = re.compile(
    r"""
    \(
        \s*
        [A-Za-z_][A-Za-z0-9_]*
        (?:\s*\*)?
        \s*
    \)
    """,
    re.VERBOSE,
)

_INCOMPLETE_POINTER_PATTERN = re.compile(
    r"""
    \(
        \s*
        void
        \s*
        \*
        \s*
    \)
    """,
    re.VERBOSE,
)

_INTEGER_CAST_PATTERN = re.compile(
    r"""
    \(
        \s*
        (?:u?int|short|long|char)
        [A-Za-z0-9_\s]*
        \)
    """,
    re.VERBOSE,
)

_VOID_POINTER_CAST_PATTERN = re.compile(
    r"""
    \(
        \s*
        void
        \s*
        \*
        \s*
    \)
    """,
    re.VERBOSE,
)


def _clean(line):
    return RuleMixin.clean(line)

# ---------------------------------------------------------
# Rule 11.1
# ---------------------------------------------------------


class Rule111(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 11.1
    """

    RULE_ID = "11.1"

    TITLE = (
        "Function pointer conversions "
        "shall not be performed"
    )

    CHAPTER = "11"

    CATEGORY = "Pointer Conversions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Conversions involving function pointers "
        "shall not be performed."
    )

    RATIONALE = (
        "Function pointer conversions are not portable."
    )

    FIXABLE = False

    PRIORITY = 111

    CAPABILITIES = (
        "text",
    )

    def check(self, code, file_path):

        violations = []

        for line_number, raw_line, line in self.iter_lines(code):

            line = line.strip()

        # Ignore ordinary pointer casts
            if re.search(r"\([A-Za-z_]\w*\s*\*\)", line):
                continue

        # Detect casts like (Func2)foo
            if re.search(r"\([A-Za-z_]\w*\)\s*[A-Za-z_]\w*", line):

                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Function pointer conversion detected."
                    ),
                )
            )

        return violations
    
# ---------------------------------------------------------
# Rule 11.2
# ---------------------------------------------------------


class Rule112(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 11.2
    """

    RULE_ID = "11.2"

    TITLE = (
        "Conversions involving incomplete pointer "
        "types shall not be performed"
    )

    CHAPTER = "11"

    CATEGORY = "Pointer Conversions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Conversions between pointers to incomplete "
        "types and other object types shall not occur."
    )

    RATIONALE = (
        "Incomplete object types provide insufficient "
        "type information for safe conversion."
    )

    FIXABLE = False

    PRIORITY = 112

    CAPABILITIES = (
        "text",
    )

    def check(self, code, file_path):

        violations = []

        has_void_pointer = "void *" in code or "void*" in code

        if not has_void_pointer:
            return violations

        for line_number, raw_line, line in self.iter_lines(code):

            if re.search(r"\([A-Za-z_]\w*\s*\*\)", line):

                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Conversion involving a void pointer detected."
                    ),
                )
            )

        return violations


# ---------------------------------------------------------
# Rule 11.3
# ---------------------------------------------------------


class Rule113(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 11.3
    """

    RULE_ID = "11.3"

    TITLE = (
        "Object pointer casts shall preserve type"
    )

    CHAPTER = "11"

    CATEGORY = "Pointer Conversions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Object pointers shall not be converted to "
        "different object pointer types."
    )

    RATIONALE = (
        "Object pointer conversions reduce type safety."
    )

    FIXABLE = False

    PRIORITY = 113

    CAPABILITIES = (
        "semantic",
    )

    def check(
        self,
        code,
        file_path,
    ):
        #
        # Semantic implementation only.
        #
        return []

    def check_with_context(
    self,
    code,
    file_path,
    analysis_context=None,
    execution_context=None,
):

        violations = []

        for line_number, raw_line, line in self.iter_lines(code):

            if re.search(
        r"\([A-Za-z_]\w*\s*\*\)\s*&",
        line,
    ):

                violations.append(
            self.create_violation(
                file_path=file_path,
                line=line_number,
                original=raw_line,
                explanation=(
                    "Object pointer conversion detected."
                ),
            )
        )

        return violations

        declaration_table = (
            self.declaration_table(
                analysis_context
            )
        )

        violations = []

        for line_number, raw_line, line in self.iter_lines(
            code
        ):

            if "(" not in line:
                continue

            if ")" not in line:
                continue

            cast = _POINTER_CAST_PATTERN.search(
                line
            )

            if cast is None:
                continue

            #
            # Very simple extraction:
            # (type *) variable
            #
            remainder = line[
                cast.end():
            ].strip()

            if not remainder:
                continue

            symbol = (
    remainder
    .replace("&", "")
    .split()[0]
    .rstrip(";")
)

            declaration = declaration_table.get(
                symbol
            )

            if declaration is None:
                continue

            source_type = classify_type(
                declaration.type_name
            )

            #
            # If the source is not already a pointer,
            # flag the conversion.
            #
            if source_type.category == "pointer":

                violations.append(
        self.create_violation(
            file_path=file_path,
            line=line_number,
            original=raw_line,
            suggestion=(
                "Avoid object pointer conversions."
            ),
            explanation=(
                f"Pointer '{symbol}' is converted "
                "to another pointer type."
            ),
        )
    )

        return violations


# ---------------------------------------------------------
# Rule 11.4
# ---------------------------------------------------------


class Rule114(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 11.4
    """

    RULE_ID = "11.4"

    TITLE = (
        "Pointer and integer conversions should be avoided"
    )

    CHAPTER = "11"

    CATEGORY = "Pointer Conversions"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Conversions between object pointers and integer "
        "types should not be performed."
    )

    RATIONALE = (
        "Pointer/integer conversions reduce portability."
    )

    FIXABLE = False

    PRIORITY = 114

    CAPABILITIES = (
        "semantic",
    )

    def check(
        self,
        code,
        file_path,
    ):
        return []

    def check_with_context(
    self,
    code,
    file_path,
    analysis_context=None,
    execution_context=None,
):

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
            analysis_context
        )

        violations = []

        for line_number, raw_line, line in self.iter_lines(
            code
        ):

            cast = _INTEGER_CAST_PATTERN.search(
                line
            )

            if cast is None:
                continue

            remainder = line[
                cast.end():
            ].strip()

            if not remainder:
                continue

            symbol = (
                remainder
                .split()[0]
                .rstrip(";")
            )

            declaration = declaration_table.get(
                symbol
            )

            if declaration is None:
                continue

            source_type = classify_type(
                declaration.type_name
            )

            if source_type.category != "pointer":
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    suggestion=(
                        "Avoid pointer-to-integer "
                        "or integer-to-pointer conversions."
                    ),
                    explanation=(
                        f"Pointer '{symbol}' is converted "
                        "to an integer type."
                    ),
                )
            )

        return violations


# ---------------------------------------------------------
# Rule 11.5
# ---------------------------------------------------------


class Rule115(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 11.5
    """

    RULE_ID = "11.5"

    TITLE = (
        "Conversions from void pointers "
        "shall not be performed"
    )

    CHAPTER = "11"

    CATEGORY = "Pointer Conversions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "A conversion from void* to an object pointer "
        "shall not be performed."
    )

    RATIONALE = (
        "Such conversions reduce type safety."
    )

    FIXABLE = False

    PRIORITY = 115

    CAPABILITIES = (
        "semantic",
    )

    def check(
        self,
        code,
        file_path,
    ):
        return []

    def check_with_context(
    self,
    code,
    file_path,
    analysis_context=None,
    execution_context=None,
):

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
            analysis_context
        )

        violations = []

        for line_number, raw_line, line in self.iter_lines(
            code
        ):

            cast = _POINTER_CAST_PATTERN.search(line)

            if cast is None:
                continue

            remainder = line[
                cast.end():
            ].strip()

            if not remainder:
                continue

            symbol = (
                remainder
                .split()[0]
                .rstrip(";")
            )

            declaration = declaration_table.get(
                symbol
            )

            if declaration is None:
                continue

            source_type = classify_type(
                declaration.type_name
            )

            if (
    source_type.category != "pointer"
    or getattr(source_type, "pointee", None) != "void"
):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    suggestion=(
                        "Avoid converting void pointers "
                        "to object pointers."
                    ),
                    explanation=(
                        f"Pointer '{symbol}' is a "
                        "void pointer being converted."
                    ),
                )
            )

        return violations

__all__ = (
    "Rule111",
    "Rule112",
    "Rule113",
    "Rule114",
    "Rule115",
)
