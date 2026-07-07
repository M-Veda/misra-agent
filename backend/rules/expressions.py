"""MISRA C:2012 expression rule plugins."""

import re

from rules.base_rule import BaseRule
from rules.rule_helpers import strip_comments, strip_string_literals

_OCTAL_LITERAL_PATTERN = re.compile(r"(?<![0-9A-Za-z_\\.])0[0-7]+(?![0-9A-Za-z_])")
_HEX_OR_OCTAL_LITERAL_PATTERN = re.compile(
    r"(?<![0-9A-Za-z_\\.])(?:0[xX][0-9A-Fa-f]+|0[0-7]+)(?![0-9A-Za-z_\\.])"
)
_INTEGER_LITERAL_PATTERN = re.compile(
    r"\b(?:0[xX][0-9A-Fa-f]+|\d+)([uUlL]*)\b"
)
_STRING_LITERAL_PATTERN = re.compile(r'"(?:\\.|[^"\\])*"')
_CHARACTER_LITERAL_PATTERN = re.compile(r"'(?:\\.|[^'\\])'")
_MULTI_CHARACTER_LITERAL_PATTERN = re.compile(r"'(?:\\.|[^'\\]){2,}'")
_WIDE_CHARACTER_LITERAL_PATTERN = re.compile(r"(?:^|[^A-Za-z0-9_])(L|u8|u|U)'(?:\\.|[^'\\])'")

# ---------------------------------------------------------------------
# Chapter 13 Patterns
# ---------------------------------------------------------------------

_INCREMENT_PATTERN = re.compile(
    r"(?:\+\+|--)"
)

_ASSIGNMENT_PATTERN = re.compile(
    r"(?<![=!<>])=(?!=)"
)

_LOGICAL_PATTERN = re.compile(
    r"(&&|\|\|)"
)

_FUNCTION_CALL_PATTERN = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\("
)

_SIDE_EFFECT_FUNCTIONS = {
    "malloc",
    "calloc",
    "realloc",
    "free",
    "printf",
    "scanf",
    "sprintf",
    "snprintf",
    "strcpy",
    "strncpy",
}

_PERSISTENT_SIDE_EFFECT_FUNCTIONS = {
    "malloc",
    "calloc",
    "realloc",
    "free",
    "printf",
    "scanf",
    "sprintf",
    "snprintf",
    "strcpy",
    "strncpy",
    "memcpy",
    "memmove",
    "fopen",
    "fclose",
    "fread",
    "fwrite",
}

_ASSIGNMENT_AS_VALUE_PATTERN = re.compile(
    r"""
    (
        if\s*\(\s*\([^)]*=[^=][^)]*\)
        |
        while\s*\(\s*\([^)]*=[^=][^)]*\)
        |
        return\s*\(\s*[^)]*=[^=][^)]*\)
        |
        [A-Za-z_]\w*\s*=\s*\([^)]*=[^=][^)]*\)
    )
    """,
    re.VERBOSE,
)

_LOGICAL_SIDE_EFFECT_PATTERN = re.compile(
    r"""
    (&&|\|\|)
    (.*)
    """,
    re.VERBOSE,
)

_SIZEOF_PATTERN = re.compile(
    r"sizeof\s*\((.*?)\)"
)

class Rule71(BaseRule):
    RULE_ID = "7.1"
    TITLE = "Octal constants shall not be used"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Octal constants shall not be used."
    RATIONALE = "Octal literals are easy to misread and can create ambiguity in expressions."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.1",)
    PRIORITY = 25
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = strip_string_literals(strip_comments(line))
            for match in _OCTAL_LITERAL_PATTERN.finditer(cleaned_line):
                literal = match.group(0)
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            f"Octal constant '{literal}' is not permitted; use a decimal or hexadecimal literal instead."
                        ),
                    )
                )
                break
        return violations


class Rule72(BaseRule):
    RULE_ID = "7.2"
    TITLE = "A u suffix shall be applied to all octal or hexadecimal constants that are represented in an unsigned form"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Octal and hexadecimal constants should use an unsigned suffix when represented as unsigned values."
    RATIONALE = "Unsigned suffixes make the intended type of octal and hexadecimal literals explicit and avoid accidental sign-related behavior."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.2",)
    PRIORITY = 26
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []

        for line_number, raw_line in enumerate(code.splitlines(), start=1):

            cleaned_line = strip_string_literals(
            strip_comments(raw_line)
        )

            for match in _HEX_OR_OCTAL_LITERAL_PATTERN.finditer(cleaned_line):

                literal = match.group(0)

            #
            # Already unsigned.
            #
                if re.search(r"[uU]", literal):
                    continue

            #
            # Ignore zero.
            #
                if literal == "0":
                    continue

            #
            # Decimal literals are not covered.
            #
                if not (
                literal.lower().startswith("0x")
                or (
                    literal.startswith("0")
                    and len(literal) > 1
                )
            ):
                    continue

                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        f"Unsigned hexadecimal/octal constant "
                        f"'{literal}' should use a 'U' suffix."
                    ),
                    suggestion=(
                        f"Use '{literal}U'."
                    ),
                )
            )

                break

        return violations


class Rule73(BaseRule):
    RULE_ID = "7.3"
    TITLE = "The lowercase character l shall not be used in a literal suffix"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Literal suffixes should use uppercase 'L' rather than lowercase 'l'."
    RATIONALE = "Lowercase suffix letters are easy to confuse with the digit '1' and reduce readability."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.3",)
    PRIORITY = 27
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = strip_string_literals(strip_comments(line))
            for match in _INTEGER_LITERAL_PATTERN.finditer(cleaned_line):
                literal = match.group(0)
                suffix = match.group(1) or ""
                if not suffix or "l" not in suffix:
                    continue
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            f"Literal suffix '{suffix}' uses lowercase 'l'; use uppercase 'L' instead."
                        ),
                    )
                )
                break
        return violations


class Rule74(BaseRule):
    RULE_ID = "7.4"
    TITLE = "A string literal shall not be assigned to an object unless the object is const-qualified"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "String literals should not be assigned to non-const objects."
    RATIONALE = "Assigning string literals to non-const objects can lead to undefined behavior and violates the intended immutability of string literals."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.4",)
    PRIORITY = 28
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            if not _STRING_LITERAL_PATTERN.search(candidate_line):
                continue
            if re.search(r"\bconst\b", candidate_line):
                continue
            if re.search(r"\b(?:char|wchar_t)\b\s*\*", candidate_line) and "=" in candidate_line:
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation="A string literal is assigned to a non-const object; make the object const-qualified or use a different initialization approach.",
                    )
                )
        return violations


class Rule75(BaseRule):
    RULE_ID = "7.5"
    TITLE = "A character literal shall not be assigned to an object unless the object is const-qualified"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Character literals should not be assigned to non-const objects."
    RATIONALE = "Assigning character literals to non-const objects can lead to undefined behavior and violates the intended immutability of character literals."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.5",)
    PRIORITY = 29
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            if not _CHARACTER_LITERAL_PATTERN.search(candidate_line):
                continue
            if re.search(r"\bconst\b", candidate_line):
                continue
            if re.search(r"\bchar\b", candidate_line) and "=" in candidate_line:
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation="A character literal is assigned to a non-const object; make the object const-qualified or use a different initialization approach.",
                    )
                )
        return violations


class Rule76(BaseRule):
    RULE_ID = "7.6"
    TITLE = "Multi-character literals shall not be used"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Multi-character literals should not be used."
    RATIONALE = "Multi-character literals are implementation-defined and can be misleading in source code."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.6",)
    PRIORITY = 30
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            for match in _MULTI_CHARACTER_LITERAL_PATTERN.finditer(candidate_line):
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=f"Multi-character literal '{match.group(0)}' is not permitted; use separate character constants or a string literal instead.",
                    )
                )
                break
        return violations


class Rule77(BaseRule):
    RULE_ID = "7.7"
    TITLE = "Wide-character literals shall not be used"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Wide-character literals should not be used."
    RATIONALE = "Wide-character literals are less portable and can obscure the intended character semantics."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.7",)
    PRIORITY = 31
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            for match in _WIDE_CHARACTER_LITERAL_PATTERN.finditer(candidate_line):
                literal = match.group(0).strip()
                
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=f"Wide-character literal '{literal}' is not permitted; use a regular character literal or string literal instead.",
                    )
                )
                break
        return violations

# ---------------------------------------------------------------------
# Rule 13.2
# ---------------------------------------------------------------------

class Rule132(BaseRule):
    """
    MISRA C:2012 Rule 13.2

    Expressions shall have the same value and persistent
    side effects regardless of evaluation order.
    """

    RULE_ID = "13.2"

    TITLE = "No undefined evaluation order"

    CHAPTER = "13"

    CATEGORY = "Expressions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Expressions shall not depend upon undefined "
        "evaluation order."
    )

    RATIONALE = (
        "Avoid expressions whose value depends on compiler "
        "evaluation order."
    )

    FIXABLE = False

    PRIORITY = 132

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

            line = strip_comments(
                strip_string_literals(raw_line)
            ).strip()

            if not line:
                continue

            increment_count = len(
                _INCREMENT_PATTERN.findall(
                    line
                )
            )

            assignment_count = len(
                _ASSIGNMENT_PATTERN.findall(
                    line
                )
            )

            logical_count = len(
                _LOGICAL_PATTERN.findall(
                    line
                )
            )

            if (
                increment_count >= 2
                or
                (
                    increment_count >= 1
                    and logical_count >= 1
                )
                or
                (
                    assignment_count >= 2
                )
            ):

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Split the expression into "
                            "multiple statements."
                        ),
                        explanation=(
                            "Expression may depend on "
                            "evaluation order."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------------------
# Rule 13.3
# ---------------------------------------------------------------------


class Rule133(BaseRule):
    """
    MISRA C:2012 Rule 13.3

    A full expression containing ++ or --
    should contain no other side effects.
    """

    RULE_ID = "13.3"

    TITLE = (
        "Increment/decrement expressions "
        "shall not contain additional side effects"
    )

    CHAPTER = "13"

    CATEGORY = "Expressions"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Expressions containing increment or decrement "
        "operators should not contain other side effects."
    )

    RATIONALE = (
        "Separating side effects improves readability "
        "and avoids subtle bugs."
    )

    FIXABLE = False

    PRIORITY = 133

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

            line = strip_comments(
                strip_string_literals(raw_line)
            ).strip()

            if not line:
                continue

            #
            # No ++ / -- ?
            #
            if not _INCREMENT_PATTERN.search(line):
                continue

            #
            # Another assignment?
            #
            assignment_count = len(
                _ASSIGNMENT_PATTERN.findall(line)
            )

            #
            # Function call?
            #
            function_calls = [
                match.group(1)
                for match in _FUNCTION_CALL_PATTERN.finditer(line)
                if match.group(1)
                not in {
                    "if",
                    "while",
                    "for",
                    "switch",
                    "sizeof",
                }
            ]

            if (
                assignment_count >= 1
                or len(function_calls) >= 1
            ):

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        suggestion=(
                            "Move increment/decrement "
                            "into its own statement."
                        ),
                        explanation=(
                            "Increment/decrement is combined "
                            "with another side effect."
                        ),
                    )
                )

        return violations
    

# ---------------------------------------------------------------------
# Rule 13.4
# ---------------------------------------------------------------------


class Rule134(BaseRule):
    """
    MISRA C:2012 Rule 13.4

    The result of an assignment operator should not be used.
    """

    RULE_ID = "13.4"

    TITLE = "Assignment result shall not be used"

    CHAPTER = "13"

    CATEGORY = "Expressions"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "The value produced by an assignment operator "
        "should not be used."
    )

    RATIONALE = (
        "Assignments used as expressions reduce "
        "clarity and are error-prone."
    )

    FIXABLE = False

    PRIORITY = 134

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

            line = strip_comments(
                strip_string_literals(raw_line)
            ).strip()

            if not line:
                continue

            if not _ASSIGNMENT_AS_VALUE_PATTERN.search(
                line
            ):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    suggestion=(
                        "Separate the assignment from "
                        "the expression."
                    ),
                    explanation=(
                        "Assignment result is used "
                        "as a value."
                    ),
                )
            )

        return violations
    

# ---------------------------------------------------------------------
# Rule 13.5
# ---------------------------------------------------------------------


class Rule135(BaseRule):
    """
    MISRA C:2012 Rule 13.5

    The right-hand operand of && or ||
    shall not contain persistent side effects.
    """

    RULE_ID = "13.5"

    TITLE = (
        "Logical RHS shall not contain "
        "persistent side effects"
    )

    CHAPTER = "13"

    CATEGORY = "Expressions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "The right-hand operand of && and || "
        "shall not contain persistent side effects."
    )

    RATIONALE = (
        "Short-circuit evaluation can prevent the "
        "right-hand operand from executing."
    )

    FIXABLE = False

    PRIORITY = 135

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

            line = strip_comments(
                strip_string_literals(raw_line)
            )

            match = _LOGICAL_SIDE_EFFECT_PATTERN.search(
                line
            )

            if match is None:
                continue

            rhs = match.group(2)

            #
            # ++ or --
            #
            if _INCREMENT_PATTERN.search(rhs):

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        explanation=(
                            "Right-hand operand contains "
                            "increment/decrement."
                        ),
                    )
                )

                continue

            #
            # Assignment
            #
            if _ASSIGNMENT_PATTERN.search(rhs):

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        explanation=(
                            "Right-hand operand contains "
                            "an assignment."
                        ),
                    )
                )

                continue

            #
            # Function calls
            #
            for function in _FUNCTION_CALL_PATTERN.finditer(
                rhs
            ):

                name = function.group(1)

                if (
                    name
                    in _PERSISTENT_SIDE_EFFECT_FUNCTIONS
                ):

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            explanation=(
                                f"Function '{name}' may "
                                "have persistent side effects "
                                "inside a logical RHS."
                            ),
                        )
                    )

                    break

        return violations
    

# ---------------------------------------------------------------------
# Rule 13.6
# ---------------------------------------------------------------------


class Rule136(BaseRule):
    """
    MISRA C:2012 Rule 13.6

    The operand of sizeof shall not contain
    expressions with side effects.
    """

    RULE_ID = "13.6"

    TITLE = "sizeof operand shall have no side effects"

    CHAPTER = "13"

    CATEGORY = "Expressions"

    SEVERITY = "Required"

    DESCRIPTION = (
        "The operand of sizeof shall not contain "
        "side effects."
    )

    RATIONALE = (
        "Although sizeof does not evaluate its operand, "
        "placing expressions with side effects inside it "
        "is misleading."
    )

    FIXABLE = False

    PRIORITY = 136

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

            line = strip_comments(
                strip_string_literals(raw_line)
            )

            for match in _SIZEOF_PATTERN.finditer(line):

                operand = match.group(1)

                #
                # ++ or --
                #
                if _INCREMENT_PATTERN.search(
                    operand
                ):

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            explanation=(
                                "sizeof operand contains "
                                "increment/decrement."
                            ),
                        )
                    )

                    continue

                #
                # Assignment
                #
                if _ASSIGNMENT_PATTERN.search(
                    operand
                ):

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            explanation=(
                                "sizeof operand contains "
                                "an assignment."
                            ),
                        )
                    )

                    continue

                #
                # Function call
                #
                for function in _FUNCTION_CALL_PATTERN.finditer(
                    operand
                ):

                    name = function.group(1)

                    if name == "sizeof":
                        continue

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            explanation=(
                                f"sizeof operand contains "
                                f"function call '{name}'."
                            ),
                        )
                    )

                    break

        return violations
    

__all__ = (
    "Rule71",
    "Rule72",
    "Rule73",
    "Rule74",
    "Rule75",
    "Rule76",
    "Rule77",
    "Rule132",
    "Rule133",
    "Rule134",
    "Rule135",
    "Rule136",
)
