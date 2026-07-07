"""MISRA C:2012 pointer and array rule plugins."""

import re

from rules.base_rule import BaseRule
from analyzer.ast_visitor import ASTVisitor
from rules.rule_helpers import (
    declaration_match,
    declaration_snippet,
    extract_declarators,
    extract_symbol,
    full_declaration_match,
    is_array_declaration,
    is_pointer_declaration,
    normalize_declaration_signature,
    strip_comments,
    strip_string_literals,
)

# ---------------------------------------------------------
# Common Regular Expressions
# ---------------------------------------------------------

_POINTER_DEREFERENCE_PATTERN = re.compile(
    r"\*\s*[A-Za-z_][A-Za-z0-9_]*"
)

_ADDRESS_OF_PATTERN = re.compile(
    r"&\s*[A-Za-z_][A-Za-z0-9_]*"
)

_ARRAY_INDEX_PATTERN = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*\s*\["
)

_UNKNOWN_ARRAY_SIZE_PATTERN = re.compile(
    r"""
    \[
    \s*
    \]
    """,
    re.VERBOSE,
)

_POINTER_ARITHMETIC_PATTERN = re.compile(
    r"""
    [A-Za-z_][A-Za-z0-9_]*
    \s*
    (\+|-)
    \s*
    [A-Za-z0-9_]+
    """,
    re.VERBOSE,
)

_POINTER_SUBTRACTION_PATTERN = re.compile(
    r"([A-Za-z_]\w*)\s*-\s*([A-Za-z_]\w*)"
)

_POINTER_RELATIONAL_PATTERN = re.compile(
    r"""
    ([A-Za-z_][A-Za-z0-9_]*)
    \s*
    (<=|>=|<|>)
    \s*
    ([A-Za-z_][A-Za-z0-9_]*)
    """,
    re.VERBOSE,
)

_POINTER_OPERATOR_PATTERN = re.compile(
    r"""
    \b([A-Za-z_][A-Za-z0-9_]*)\b
    \s*
    (
        \+=
        |
        -=
        |
        \+
        |
        -
    )
    """,
    re.VERBOSE,
)

_NULL_POINTER_PATTERN = re.compile(
    r"\bNULL\b|\bnullptr\b|\b0\b"
)

# ---------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------

def _clean(line):
    """
    Remove comments and string literals.
    """

    return strip_string_literals(
        strip_comments(line)
    )


def _iter_declarations(code):

    for line_number, line in enumerate(
        code.splitlines(),
        start=1,
    ):

        match = declaration_match(line)

        if match:

            yield (
                line_number,
                line,
                match.group("decl"),
            )


def _iter_full_declarations(code):

    for line_number, line in enumerate(
        code.splitlines(),
        start=1,
    ):

        match = full_declaration_match(line)

        if match:

            yield (
                line_number,
                line,
                match.group("decl"),
            )

def _collect_pointer_symbols(code):
    """
    Collect names of declared pointer variables.
    """

    pointers = set()

    for match in re.finditer(
        r"\*\s*([A-Za-z_][A-Za-z0-9_]*)",
        code,
    ):
        pointers.add(match.group(1))

    return pointers

def _pointer_declarations(code):
    """
    Return a mapping of pointer variable names to their
    declaration information.
    """

    declarations = {}

    for line_number, line, declaration in _iter_declarations(code):

        if not is_pointer_declaration(declaration):
            continue

        signature = normalize_declaration_signature(
            declaration
        )

        for declarator in extract_declarators(
            declaration
        ):

            symbol = extract_symbol(
                declarator
            )

            if symbol:

                declarations[symbol] = {
                    "line": line_number,
                    "signature": signature,
                    "declaration": declaration,
                }

    return declarations

def _array_declarations(code):
    """
    Return a mapping of array variable names.
    """

    arrays = {}

    for line_number, line, declaration in _iter_declarations(code):

        if not is_array_declaration(
            declaration
        ):
            continue

        signature = normalize_declaration_signature(
            declaration
        )

        for declarator in extract_declarators(
            declaration
        ):

            symbol = extract_symbol(
                declarator
            )

            if symbol:

                arrays[symbol] = {
                    "line": line_number,
                    "signature": signature,
                    "declaration": declaration,
                }

    return arrays

# ---------------------------------------------------------
# Rule 18.1
# ---------------------------------------------------------


class Rule181(BaseRule):
    """
    MISRA C:2012 Rule 18.1

    Pointer arithmetic shall remain within
    the same array object.
    """

    RULE_ID = "18.1"

    TITLE = "Pointer arithmetic shall remain within the same array"

    CHAPTER = "18"

    CATEGORY = "Pointers"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Pointer arithmetic shall not move a pointer "
        "outside the bounds of its originating array."
    )

    RATIONALE = (
        "Pointer arithmetic outside an array results "
        "in undefined behaviour."
    )

    FIXABLE = False

    PRIORITY = 181

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = _clean(raw_line)

            if not line.strip():
                continue

            #
            # Ignore declarations.
            #
            if declaration_match(line):
                continue

            for match in _POINTER_ARITHMETIC_PATTERN.finditer(line):

                expression = match.group(0)

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Verify that pointer arithmetic "
                            "remains within the same array object."
                        ),
                        explanation=(
                            f"Pointer arithmetic detected: "
                            f"'{expression}'."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------
# Rule 18.2
# ---------------------------------------------------------


class Rule182(BaseRule):
    """
    MISRA C:2012 Rule 18.2

    Pointer subtraction shall only occur between
    pointers into the same array object.
    """

    RULE_ID = "18.2"

    TITLE = "Pointer subtraction shall use the same array"

    CHAPTER = "18"

    CATEGORY = "Pointers"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Subtracting pointers from different arrays "
        "results in undefined behaviour."
    )

    RATIONALE = (
        "Pointer subtraction is only valid when both "
        "pointers refer to elements of the same array."
    )

    FIXABLE = False

    PRIORITY = 182

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = raw_line

            if not line.strip():
                continue

            pointer_symbols = _collect_pointer_symbols(code)

            for match in _POINTER_SUBTRACTION_PATTERN.finditer(line):

                left = match.group(1)
                right = match.group(2)

                #
                # Skip numeric subtraction.
                #

                if left not in pointer_symbols or right not in pointer_symbols:
                    continue

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Ensure both pointers refer "
                            "to the same array object."
                        ),
                        explanation=(
                            f"Pointer subtraction detected "
                            f"('{left} - {right}')."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------
# Rule 18.3
# ---------------------------------------------------------


class Rule183(BaseRule):
    """
    MISRA C:2012 Rule 18.3

    Pointer relational comparison.
    """

    RULE_ID = "18.3"

    TITLE = (
        "Pointer relational comparison "
        "shall remain within one array"
    )

    CHAPTER = "18"

    CATEGORY = "Pointers"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Pointers shall only be compared using "
        "relational operators when they refer to "
        "the same array object."
    )

    RATIONALE = (
        "Relational comparison between unrelated "
        "pointers has undefined behaviour."
    )

    FIXABLE = False

    PRIORITY = 183

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        pointer_symbols = _collect_pointer_symbols(
            code
        )

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = _clean(raw_line)

            if not line.strip():
                continue

            for match in _POINTER_RELATIONAL_PATTERN.finditer(
                line
            ):

                left = match.group(1)

                operator = match.group(2)

                right = match.group(3)

                if (
                    left not in pointer_symbols
                    or right not in pointer_symbols
                ):
                    continue

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Verify that both pointers "
                            "belong to the same array."
                        ),
                        explanation=(
                            f"Pointer comparison "
                            f"'{left} {operator} {right}' "
                            "may violate MISRA Rule 18.3."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------
# Rule 18.4
# ---------------------------------------------------------


class Rule184(BaseRule):
    """
    MISRA C:2012 Rule 18.4

    Pointer arithmetic operators should not be used.
    """

    RULE_ID = "18.4"

    TITLE = "Pointer arithmetic operators should not be used"

    CHAPTER = "18"

    CATEGORY = "Pointers"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "The +, -, += and -= operators should not "
        "be applied to expressions of pointer type."
    )

    RATIONALE = (
        "Pointer arithmetic reduces readability and "
        "is error-prone."
    )

    FIXABLE = False

    PRIORITY = 184

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        pointer_symbols = _collect_pointer_symbols(
            code
        )

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = _clean(raw_line)

            if not line.strip():
                continue

            if declaration_match(line):
                continue

            for match in _POINTER_OPERATOR_PATTERN.finditer(
                line
            ):

                symbol = match.group(1)

                operator = match.group(2)

                if symbol not in pointer_symbols:
                    continue

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Avoid pointer arithmetic."
                        ),
                        explanation=(
                            f"Pointer '{symbol}' uses "
                            f"operator '{operator}'."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------
# Rule 18.5
# ---------------------------------------------------------


class Rule185(BaseRule):
    """
    MISRA C:2012 Rule 18.5

    Arrays should have an explicit size.
    """

    RULE_ID = "18.5"

    TITLE = "Arrays should have explicit size"

    CHAPTER = "18"

    CATEGORY = "Pointers"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Objects should not be declared as arrays of "
        "unknown size."
    )

    RATIONALE = (
        "Explicit array sizes improve readability and "
        "prevent accidental misuse."
    )

    FIXABLE = False

    PRIORITY = 185

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        arrays = _array_declarations(code)

        if not arrays:
            return violations

        for symbol, info in arrays.items():

            declaration = info["declaration"]

            if not _UNKNOWN_ARRAY_SIZE_PATTERN.search(
                declaration
            ):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=info["line"],
                    original=declaration,
                    suggestion=(
                        "Specify an explicit array size."
                    ),
                    explanation=(
                        f"Array '{symbol}' is declared "
                        "without an explicit size."
                    ),
                )
            )

        return violations
    

__all__ = (
    "Rule181",
    "Rule182",
    "Rule183",
    "Rule184",
    "Rule185",
)
