"""
MISRA C:2012 statement rule plugins.
"""

import re

from rules.base_rule import BaseRule
from rules.autofix import AutoFix


def _line_number(code: str, index: int) -> int:
    return code[:index].count("\n") + 1

def _source_line(
    code: str,
    position: int,
):
    """
    Return both the source line number and
    original source text.
    """

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

class Rule155(BaseRule):
    """
    MISRA C:2012 Rule 15.5

    A function should have a single point of exit at the end of the function.
    """

    RULE_ID = "15.5"
    TITLE = "Single point of exit"
    CHAPTER = "15"
    CATEGORY = "Statements"
    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Functions should normally have a single return statement located "
        "at the end of the function."
    )

    RATIONALE = (
        "Multiple return statements make control flow harder to understand "
        "and maintain."
    )

    FIXABLE = False

    PRIORITY = 155

    CAPABILITIES = ("text",)

    RETURN_PATTERN = re.compile(r"\breturn\b")

    def check(self, code: str, file_path: str):

        violations = []

        matches = list(self.RETURN_PATTERN.finditer(code))

        if len(matches) <= 1:
            return violations

        for match in matches[:-1]:

            line, original = _source_line(
    code,
    match.start(),
)

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion="Consider restructuring the function to use a single return statement.",
                    explanation=(
                        "MISRA Rule 15.5 recommends a single exit point "
                        "from a function."
                    ),
                )
            )

        return violations
    
# ---------------------------------------------------------------------
# Rule 15.1
# ---------------------------------------------------------------------


class Rule151(BaseRule):
    """
    MISRA C:2012 Rule 15.1

    The goto statement should not be used.
    """

    RULE_ID = "15.1"
    TITLE = "goto shall not be used"
    CHAPTER = "15"
    CATEGORY = "Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "The goto statement shall not be used."
    )

    RATIONALE = (
        "goto statements make control flow difficult to understand."
    )

    FIXABLE = False

    PRIORITY = 151

    CAPABILITIES = ("text",)

    GOTO_PATTERN = re.compile(
        r"\bgoto\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
    )

    def check(self, code, file_path):

        violations = []

        for match in self.GOTO_PATTERN.finditer(code):

            line, original = _source_line(
    code,
    match.start(),
)

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion="Replace goto with structured control flow.",
                    explanation=(
                        "MISRA Rule 15.1 prohibits the use of goto."
                    ),
                )
            )

        return violations


# ---------------------------------------------------------------------
# Rule 15.2
# ---------------------------------------------------------------------


class Rule152(BaseRule):
    """
    MISRA C:2012 Rule 15.2

    goto labels should be unique.
    """

    RULE_ID = "15.2"
    TITLE = "Unique goto labels"
    CHAPTER = "15"
    CATEGORY = "Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "Labels referenced by goto should be unique."
    )

    RATIONALE = (
        "Duplicate labels create ambiguity."
    )

    FIXABLE = False

    PRIORITY = 152

    CAPABILITIES = ("text",)

    LABEL_PATTERN = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:",
        re.MULTILINE,
    )

    def check(self, code, file_path):

        violations = []

        labels = {}

        for match in self.LABEL_PATTERN.finditer(code):

            name = match.group(1)

            if name not in labels:
                labels[name] = []

            labels[name].append(match.start())

        for name, locations in labels.items():

            if len(locations) < 2:
                continue

            for location in locations[1:]:

                line = _line_number(
                    code,
                    location,
                )

                original = code.splitlines()[line - 1]

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        original=original,
                        suggestion="Rename duplicate label.",
                        explanation=(
                            f"Duplicate label '{name}' detected."
                        ),
                    )
                )

        return violations


# ---------------------------------------------------------------------
# Rule 15.3
# ---------------------------------------------------------------------


class Rule153(BaseRule):
    """
    MISRA C:2012 Rule 15.3

    goto shall not jump into a block.
    """

    RULE_ID = "15.3"
    TITLE = "goto shall not jump into a block"
    CHAPTER = "15"
    CATEGORY = "Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "goto statements shall not jump into nested blocks."
    )

    RATIONALE = (
        "Jumping into blocks bypasses initialization."
    )

    FIXABLE = False

    PRIORITY = 153

    CAPABILITIES = ("text",)

    GOTO_PATTERN = re.compile(
        r"\bgoto\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
    )

    def check(self, code, file_path):

        violations = []

        lines = code.splitlines()

        for match in self.GOTO_PATTERN.finditer(code):

            line = _line_number(
                code,
                match.start(),
            )

            label = match.group(1)

            target_line = None

            for index, current in enumerate(lines):

                if re.match(
                    rf"\s*{re.escape(label)}\s*:",
                    current,
                ):
                    target_line = index + 1
                    break

            if target_line is None:
                continue

            if target_line > line + 1:

                original = lines[line - 1]

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        original=original,
                        suggestion="Replace goto with structured control flow.",
                        explanation=(
                            "Potential jump into nested block detected."
                        ),
                    )
                )

        return violations
    
# ---------------------------------------------------------------------
# Rule 15.4
# ---------------------------------------------------------------------


class Rule154(BaseRule):
    """
    MISRA C:2012 Rule 15.4

    Every if...else if construct shall terminate with an else statement.
    """

    RULE_ID = "15.4"
    TITLE = "if-else chain shall terminate with else"
    CHAPTER = "15"
    CATEGORY = "Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "Every if...else if chain should terminate with an else clause."
    )

    RATIONALE = (
        "Ensures all execution paths are considered."
    )

    FIXABLE = False

    PRIORITY = 154

    CAPABILITIES = ("text",)

    def check(self, code, file_path):

        violations = []

        pattern = re.compile(
        r"""
        if\s*\(.*?\)
        .*?
        else\s+if\s*\(.*?\)
        (?!.*?\belse\b)
        """,
        re.DOTALL | re.VERBOSE,
    )

        for match in pattern.finditer(code):

            line = _line_number(
            code,
            match.start(),
        )

            violations.append(
            self.create_violation(
                file_path=file_path,
                line=line,
                original=code.splitlines()[line-1],
                suggestion="Add final else clause.",
                explanation=(
                    "if/else-if chain does not terminate "
                    "with an else clause."
                ),
            )
        )

        return violations


# ---------------------------------------------------------------------
# Rule 16.1
# ---------------------------------------------------------------------


class Rule161(BaseRule):
    """
    MISRA C:2012 Rule 16.1

    Every switch statement shall be well formed.
    """

    RULE_ID = "16.1"
    TITLE = "Switch statement shall be well formed"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "Every switch statement should contain case labels."
    )

    RATIONALE = (
        "Empty switch statements are confusing."
    )

    FIXABLE = False

    PRIORITY = 161

    CAPABILITIES = ("text",)

    SWITCH_PATTERN = re.compile(
        r"switch\s*\([^)]*\)\s*\{",
        re.MULTILINE,
    )

    def check(self, code, file_path):

        violations = []

        for match in self.SWITCH_PATTERN.finditer(code):

            start = match.end()
            end = code.find("}", start)

            if end == -1:
                continue

            body = code[start:end]

            if "case" not in body or "default" not in body:

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
                        "Add case labels and default label."
                    ),
                    explanation=(
                        "Switch statement is incomplete."
                    ),
                )
            )

        return violations


# ---------------------------------------------------------------------
# Rule 16.3
# ---------------------------------------------------------------------


class Rule163(BaseRule):
    """
    MISRA C:2012 Rule 16.3

    Every switch clause shall terminate with break.
    """

    RULE_ID = "16.3"
    TITLE = "Switch clauses shall terminate with break"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "Every non-empty switch clause should terminate with break."
    )

    RATIONALE = (
        "Prevents accidental fall-through."
    )

    FIXABLE = False

    PRIORITY = 163

    CAPABILITIES = ("text",)

    CASE_PATTERN = re.compile(
        r"(case\s+.*?:|default\s*:)",
        re.MULTILINE,
    )

    def check(self, code, file_path):

        violations = []

        matches = list(
            self.CASE_PATTERN.finditer(code)
        )

        for index, match in enumerate(matches):

            start = match.end()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(code)

            section = code[start:end]

            if (
    not re.search(
        r"\bbreak\s*;",
        section,
    )
    and
    not re.search(
        r"\breturn\b",
        section,
    )
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
                        suggestion="Terminate switch clause with break.",
                        explanation=(
                            "Switch clause may fall through."
                        ),
                    )
                )

        return violations
    
# ---------------------------------------------------------------------
# Rule 16.4
# ---------------------------------------------------------------------


class Rule164(BaseRule):
    """
    MISRA C:2012 Rule 16.4

    Every switch statement should have a default label.
    """

    RULE_ID = "16.4"
    TITLE = "Switch statement should have default"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Every switch statement should contain a default label."
    )

    RATIONALE = (
        "Ensures unexpected values are handled."
    )

    FIXABLE = False

    PRIORITY = 164

    CAPABILITIES = ("text",)

    SWITCH_PATTERN = re.compile(
        r"switch\s*\([^)]*\)\s*\{",
        re.MULTILINE,
    )

    def check(self, code, file_path):

        violations = []

        for match in self.SWITCH_PATTERN.finditer(code):

            start = match.end()

            end = code.find("}", start)

            if end == -1:
                continue

            body = code[start:end]

            if not re.search(
    r"\bdefault\b",
    body,
):

                line = _line_number(
                    code,
                    match.start(),
                )

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        original=code.splitlines()[line - 1],
                        suggestion="Add a default label.",
                        explanation=(
                            "Switch statement has no default label."
                        ),
                    )
                )

        return violations


# ---------------------------------------------------------------------
# Rule 16.5
# ---------------------------------------------------------------------


class Rule165(BaseRule):
    """
    MISRA C:2012 Rule 16.5

    Every switch statement should have at least two case labels.
    """

    RULE_ID = "16.5"
    TITLE = "Switch should contain multiple cases"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Switch statements should normally contain multiple case labels."
    )

    RATIONALE = (
        "A switch with only one case is usually unnecessary."
    )

    FIXABLE = False

    PRIORITY = 165

    CAPABILITIES = ("text",)

    def check(self, code, file_path):

        violations = []

        for match in re.finditer(
            r"switch\s*\([^)]*\)\s*\{",
            code,
        ):

            start = match.end()

            end = code.find("}", start)

            if end == -1:
                continue

            body = code[start:end]

            cases = re.findall(
                r"\bcase\b",
                body,
            )

            if len(cases) < 2:

                line = _line_number(
                    code,
                    match.start(),
                )

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        original=code.splitlines()[line - 1],
                        suggestion="Consider replacing with if-else or add more case labels.",
                        explanation=(
                            "Switch statement contains fewer than two case labels."
                        ),
                    )
                )

        return violations


# ---------------------------------------------------------------------
# Rule 16.6
# ---------------------------------------------------------------------


class Rule166(BaseRule):
    """
    MISRA C:2012 Rule 16.6

    Every switch statement should be well structured.
    """

    RULE_ID = "16.6"
    TITLE = "Nested switch depth"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Deeply nested switch statements should be avoided."
    )

    RATIONALE = (
        "Reduces code complexity."
    )

    FIXABLE = False

    PRIORITY = 166

    CAPABILITIES = ("text",)

    def check(self, code, file_path):

        violations = []

        depth = 0

        for index, line in enumerate(code.splitlines(), start=1):

            if re.search(
    r"\bswitch\b",
    line,
):
                depth += 1

                if depth > 2:

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=index,
                            original=line,
                            suggestion="Reduce nested switch depth.",
                            explanation=(
                                "Nested switch statements reduce readability."
                            ),
                        )
                    )

            depth -= line.count("}")

            if depth < 0:
                depth = 0

        return violations


# ---------------------------------------------------------------------
# Rule 16.7
# ---------------------------------------------------------------------


class Rule167(BaseRule):
    """
    MISRA C:2012 Rule 16.7

    Switch expressions should use appropriate controlling expressions.
    """

    RULE_ID = "16.7"
    TITLE = "Switch controlling expression"
    CHAPTER = "16"
    CATEGORY = "Switch Statements"
    SEVERITY = "Required"

    DESCRIPTION = (
        "The controlling expression of a switch statement should be simple."
    )

    RATIONALE = (
        "Complex expressions reduce readability."
    )

    FIXABLE = False

    PRIORITY = 167

    CAPABILITIES = ("text",)

    SWITCH_PATTERN = re.compile(
        r"switch\s*\((.*?)\)",
        re.MULTILINE,
    )

    def check(self, code, file_path):

        violations = []

        for match in self.SWITCH_PATTERN.finditer(code):

            expression = match.group(1)

            if any(
                operator in expression
                for operator in (
                    "+",
                    "-",
                    "*",
                    "/",
                    "%",
                    "&&",
                    "||",
                )
            ):

                line = _line_number(
                    code,
                    match.start(),
                )

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        original=code.splitlines()[line - 1],
                        suggestion="Assign the expression to a variable before switch.",
                        explanation=(
                            "Complex controlling expression detected."
                        ),
                    )
                )

        return violations
    
class Rule156(BaseRule):
    """
    MISRA C:2012 Rule 15.6

    Every selection and iteration statement shall use
    a compound statement.
    """

    RULE_ID = "15.6"

    TITLE = "Compound statements required"

    CHAPTER = "15"

    CATEGORY = "Statements"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Bodies of if, else, for, while and do statements "
        "shall always be enclosed in braces."
    )

    RATIONALE = (
        "Using compound statements prevents accidental "
        "logic errors when statements are modified."
    )

    FIXABLE = False

    PRIORITY = 156

    CAPABILITIES = ("text",)

    def check(
        self,
        code,
        file_path,
    ):

        import re

        violations = []

        pattern = re.compile(
            r"""
            ^
            \s*
            (if|else\s+if|else|for|while|do)
            \b
            [^{;]*$
            """,
            re.VERBOSE,
        )

        lines = code.splitlines()

        for index, line in enumerate(lines, start=1):

            stripped = line.strip()

            if not stripped:
                continue

            if "{" in stripped:
                continue

            if pattern.match(stripped):

                violations.append(
    self.create_violation(
        file_path=file_path,
        line=index,
        original=line,
        suggestion=(
            "Enclose the statement body in braces."
        ),
        explanation=(
            "MISRA Rule 15.6 requires compound statements."
        ),
    )
)

        return violations
    

__all__ = (
    "Rule151",
    "Rule152",
    "Rule153",
    "Rule154",
    "Rule155",
    "Rule156",
    "Rule161",
    "Rule163",
    "Rule164",
    "Rule165",
    "Rule166",
    "Rule167",
)
