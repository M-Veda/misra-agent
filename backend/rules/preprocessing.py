"""
MISRA C:2012 preprocessing directive rule plugins.
"""

import re

from rules.base_rule import BaseRule


def _line_number(
    code: str,
    index: int,
) -> int:
    return code[:index].count("\n") + 1


def _source_line(
    code: str,
    position: int,
):
    line = _line_number(
        code,
        position,
    )

    lines = code.splitlines()

    original = (
        lines[line - 1]
        if line <= len(lines)
        else ""
    )

    return (
        line,
        original,
    )

_INCLUDE_PATTERN = re.compile(
    r'^\s*#\s*include\b',
    re.MULTILINE,
)

_DEFINE_PATTERN = re.compile(
    r'^\s*#\s*define\b',
    re.MULTILINE,
)

_UNDEF_PATTERN = re.compile(
    r'^\s*#\s*undef\b',
    re.MULTILINE,
)

_IFDEF_PATTERN = re.compile(
    r'^\s*#\s*(ifdef|ifndef|if|elif|else|endif)\b',
    re.MULTILINE,
)

class Rule201(BaseRule):
    """
    MISRA C:2012 Rule 20.1

    #include directives should only appear
    before declarations and definitions.
    """

    RULE_ID = "20.1"

    TITLE = "#include placement"

    CHAPTER = "20"

    CATEGORY = "Preprocessing"

    SEVERITY = "Required"

    DESCRIPTION = (
        "#include directives shall only appear "
        "before declarations or definitions."
    )

    RATIONALE = (
        "Late include directives make compilation "
        "order difficult to understand."
    )

    FIXABLE = False

    PRIORITY = 201

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        found_code = False

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = raw_line.strip()

            if (
                not line
                or line.startswith("//")
                or line.startswith("/*")
            ):
                continue

            if _INCLUDE_PATTERN.match(line):

                if found_code:

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            suggestion=(
                                "Move #include directives "
                                "to the top of the file."
                            ),
                            explanation=(
                                "#include appears after "
                                "code has started."
                            ),
                        )
                    )

                continue

            if not line.startswith("#"):
                found_code = True

        return violations
    
class Rule202(BaseRule):
    """
    MISRA C:2012 Rule 20.2

    Macro names shall be unique.
    """

    RULE_ID = "20.2"

    TITLE = "Macro names shall be unique"

    CHAPTER = "20"

    CATEGORY = "Preprocessing"

    SEVERITY = "Required"

    DESCRIPTION = (
        "A macro name shall not be redefined."
    )

    RATIONALE = (
        "Redefining macros can lead to confusing "
        "and unpredictable preprocessing."
    )

    FIXABLE = False

    PRIORITY = 202

    CAPABILITIES = ("text",)

    DEFINE_PATTERN = re.compile(
        r"""
        ^
        \s*
        \#
        \s*
        define
        \s+
        (?P<name>[A-Za-z_]\w*)
        """,
        re.MULTILINE | re.VERBOSE,
    )

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        macros = {}

        for match in self.DEFINE_PATTERN.finditer(
            code
        ):

            name = match.group("name")

            line, original = _source_line(
                code,
                match.start(),
            )

            if name not in macros:

                macros[name] = line
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion=(
                        "Rename or remove the duplicate "
                        "macro definition."
                    ),
                    explanation=(
                        f"Macro '{name}' is defined "
                        "more than once."
                    ),
                )
            )

        return violations
    
class Rule203(BaseRule):
    """
    MISRA C:2012 Rule 20.3

    Conditional preprocessing directives
    shall be properly balanced.
    """

    RULE_ID = "20.3"

    TITLE = "Balanced conditional preprocessing"

    CHAPTER = "20"

    CATEGORY = "Preprocessing"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Conditional preprocessing directives "
        "shall be correctly matched."
    )

    RATIONALE = (
        "Unbalanced preprocessing directives "
        "can lead to unexpected compilation."
    )

    FIXABLE = False

    PRIORITY = 203

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        stack = []

        for line_number, raw_line in enumerate(
            code.splitlines(),
            start=1,
        ):

            line = raw_line.strip()

            if re.match(
                r"^\s*#\s*(if|ifdef|ifndef)\b",
                line,
            ):
                stack.append(line_number)
                continue

            if re.match(
                r"^\s*#\s*endif\b",
                line,
            ):

                if stack:
                    stack.pop()
                else:

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            suggestion=(
                                "Remove the unmatched "
                                "#endif."
                            ),
                            explanation=(
                                "Found an #endif without "
                                "a matching opening directive."
                            ),
                        )
                    )

        for line_number in stack:

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=code.splitlines()[
                        line_number - 1
                    ],
                    suggestion=(
                        "Add a matching #endif."
                    ),
                    explanation=(
                        "Conditional preprocessing block "
                        "is not closed."
                    ),
                )
            )

        return violations
    
class Rule204(BaseRule):
    """
    MISRA C:2012 Rule 20.4

    A macro should not be defined with an empty replacement list.
    """

    RULE_ID = "20.4"

    TITLE = "Empty macro replacement list"

    CHAPTER = "20"

    CATEGORY = "Preprocessing"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Object-like macros should not have an "
        "empty replacement list."
    )

    RATIONALE = (
        "Empty macro definitions reduce readability "
        "and may hide intent."
    )

    FIXABLE = False

    PRIORITY = 204

    CAPABILITIES = ("text",)

    DEFINE_PATTERN = re.compile(
        r"""
        ^
        \s*
        \#
        \s*
        define
        \s+
        (?P<name>[A-Za-z_]\w*)
        (?P<body>\s*)$
        """,
        re.MULTILINE | re.VERBOSE,
    )

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for match in self.DEFINE_PATTERN.finditer(
            code
        ):

            line, original = _source_line(
                code,
                match.start(),
            )

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion=(
                        "Provide a replacement list or "
                        "remove the macro."
                    ),
                    explanation=(
                        "Macro has an empty replacement list."
                    ),
                )
            )

        return violations

class Rule205(BaseRule):
    """
    MISRA C:2012 Rule 20.5

    #undef shall not be used.
    """

    RULE_ID = "20.5"

    TITLE = "#undef shall not be used"

    CHAPTER = "20"

    CATEGORY = "Preprocessing"

    SEVERITY = "Required"

    DESCRIPTION = (
        "The #undef directive shall not be used."
    )

    RATIONALE = (
        "Removing macro definitions can make code "
        "difficult to reason about."
    )

    FIXABLE = False

    PRIORITY = 205

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for match in _UNDEF_PATTERN.finditer(code):

            line, original = _source_line(
                code,
                match.start(),
            )

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion=(
                        "Avoid using #undef."
                    ),
                    explanation=(
                        "MISRA Rule 20.5 prohibits "
                        "#undef."
                    ),
                )
            )

        return violations
    
__all__ = (
    "Rule201",
    "Rule202",
    "Rule203",
    "Rule204",
    "Rule205",
)
