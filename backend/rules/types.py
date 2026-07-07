"""
MISRA C:2012 Essential Type Model rules.
"""

import re

from analyzer.essential_types import (
    classify_type,
    compatible,
)
from analyzer.analysis_context import AnalysisContext
from rules.base_rule import BaseRule
from rules.rule_helpers import (
    strip_comments,
    strip_string_literals,
)
from rules.rule_mixins import RuleMixin

# ---------------------------------------------------------
# Common Patterns
# ---------------------------------------------------------

_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ([A-Za-z_]\w*)
    \s*=\s*
    (.+?)
    ;
    """,
    re.VERBOSE,
)

_CAST_PATTERN = re.compile(
    r"\(\s*[A-Za-z_][A-Za-z0-9_\s\*]*\)"
)

_INTEGER_LITERAL_PATTERN = re.compile(
    r"\b\d+[uUlL]*\b"
)

_FLOAT_LITERAL_PATTERN = re.compile(
    r"\b\d+\.\d+[fFlL]?\b"
)


def _clean(line):
    return strip_string_literals(
        strip_comments(line)
    )


def _literal_type(expression):
    """
    Infer the type of a literal expression.

    Returns:
        "float"
        "integer"
        None
    """

    expression = expression.strip()

    if _FLOAT_LITERAL_PATTERN.fullmatch(expression):
        return "float"

    if _INTEGER_LITERAL_PATTERN.fullmatch(expression):
        return "integer"

    return None


# ---------------------------------------------------------
# Rule 10.1
# ---------------------------------------------------------


class Rule101(RuleMixin,BaseRule):
    """
    MISRA C:2012 Rule 10.1

    Operands shall not be of an inappropriate
    essential type.
    """

    RULE_ID = "10.1"

    TITLE = "Operands shall use appropriate essential types"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Operands shall not be of an inappropriate "
        "essential type."
    )

    RATIONALE = (
        "Implicit type misuse can introduce "
        "unexpected behaviour."
    )

    FIXABLE = False

    PRIORITY = 101

    CAPABILITIES = (
        "text",
        "semantic",
    )

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            match = _ASSIGNMENT_PATTERN.search(line)

            if match is None:
                continue

            lhs = match.group(1)

            rhs = match.group(2).strip()

            literal_type = _literal_type(rhs)

            #
            # Only obvious suspicious cases for now.
            #
            if literal_type is None:
                continue

            if _CAST_PATTERN.search(rhs):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    suggestion=(
                        "Verify that both operands "
                        "have compatible essential types."
                    ),
                    explanation=(
                        f"Assignment to '{lhs}' uses "
                        f"a {literal_type} literal."
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
        """
        Semantic implementation of Rule 10.1.

        Uses declaration information to compare
        essential types.
        """

        if analysis_context is None:
            return self.check(
                code,
                file_path,
            )

        violations = []

        #
        # Build declaration lookup table.
        #
        declaration_table = {}

        for declaration in analysis_context.declarations:

            if not declaration.name:
                continue

            declaration_table[
                declaration.name
            ] = declaration

        #
        # Scan assignments.
        #
        for line_number, raw_line, line in self.iter_lines(
    code
):

            match = _ASSIGNMENT_PATTERN.search(line)

            if match is None:
                continue

            lhs = match.group(1)

            rhs = match.group(2).strip()

            lhs_decl = declaration_table.get(lhs)

            if lhs_decl is None:
                continue

            #
            # Determine LHS essential type.
            #
            lhs_type = classify_type(
                lhs_decl.type_name
            )

            rhs_type = None

            literal = _literal_type(rhs)

            if literal == "integer":

                rhs_type = classify_type(
                    "int"
                )

            elif literal == "float":

                rhs_type = classify_type(
                    "float"
                )

            elif rhs in declaration_table:

                rhs_type = classify_type(
                    declaration_table[
                        rhs
                    ].type_name
                )

            if rhs_type is None:
                continue

            if compatible(
                lhs_type,
                rhs_type,
            ):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    suggestion=(
                        "Use operands with compatible "
                        "essential types."
                    ),
                    explanation=(
                        f"'{lhs}' has essential type "
                        f"'{lhs_type.category}', "
                        f"but RHS has essential type "
                        f"'{rhs_type.category}'."
                    ),
                )
            )

        return violations
    
# ---------------------------------------------------------
# Rule 10.2
# ---------------------------------------------------------


from analyzer.expression_analysis import (
    expression_type,
)


class Rule102(RuleMixin,BaseRule):
    """
    MISRA C:2012 Rule 10.2

    Character types shall not participate in
    inappropriate arithmetic expressions.
    """

    RULE_ID = "10.2"

    TITLE = (
        "Character types shall not be used "
        "in arithmetic expressions"
    )

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Essentially character operands shall not "
        "participate in arithmetic expressions."
    )

    RATIONALE = (
        "Character values represent text, not numbers."
    )

    FIXABLE = False

    PRIORITY = 102

    CAPABILITIES = ("hybrid",)

    _ARITHMETIC_PATTERN = re.compile(
        r"""
        ([A-Za-z_]\w*)
        \s*
        (\+|-|\*|/|%)
        \s*
        ([A-Za-z_]\w*|\d+)
        """,
        re.VERBOSE,
    )

    def check(self, code, file_path):
        violations = []

        pattern = re.compile(r"\b[a-zA-Z_]\w*\s*[\+\-\*/%]\s*['\"0-9a-zA-Z_]")

        for line_no, raw, line in self.iter_lines(code):
            if pattern.search(line):
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_no,
                        original=raw,
                        explanation="Possible arithmetic involving character operands.",
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

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
    analysis_context
)

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            for match in self._ARITHMETIC_PATTERN.finditer(line):

                left = match.group(1)

                operator = match.group(2)

                right = match.group(3)

                left_type = expression_type(
                    left,
                    declaration_table,
                )

                right_type = expression_type(
                    right,
                    declaration_table,
                )

                if (
                    left_type.category == "character"
                    or
                    right_type.category == "character"
                ):

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line,
                            suggestion=(
                                "Avoid arithmetic on "
                                "essentially character types."
                            ),
                            explanation=(
                                f"Arithmetic operator '{operator}' "
                                "uses a character operand."
                            ),
                        )
                    )

        return violations
    
# ---------------------------------------------------------
# Rule 10.3
# ---------------------------------------------------------


class Rule103(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 10.3

    Assignment shall not narrow the
    essential type category.
    """

    RULE_ID = "10.3"

    TITLE = "Assignment shall preserve essential type"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Assignments shall not convert between "
        "incompatible essential type categories."
    )

    RATIONALE = (
        "Implicit conversions may lose information."
    )

    FIXABLE = False

    PRIORITY = 103

    CAPABILITIES = ("semantic",)

    def check(self, code, file_path):
        violations = []

        for line_no, raw, line in self.iter_lines(code):
            if "=" in line and "(" in line:
                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_no,
                    original=raw,
                    explanation="Assignment may narrow essential type.",
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

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
    analysis_context
)

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            match = _ASSIGNMENT_PATTERN.search(line)

            if match is None:
                continue

            lhs = match.group(1)
            rhs = match.group(2).strip()

            if (
                lhs not in declaration_table
            ):
                continue

            lhs_type = classify_type(
                declaration_table[lhs].type_name
            )

            rhs_type = expression_type(
                rhs,
                declaration_table,
            )

            if rhs_type.category == "unknown":
                continue

            if compatible(
                lhs_type,
                rhs_type,
            ):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Assignment converts between "
                        "different essential types."
                    ),
                )
            )

        return violations


# ---------------------------------------------------------
# Rule 10.4
# ---------------------------------------------------------


class Rule104(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 10.4
    """

    RULE_ID = "10.4"

    TITLE = "Binary operators shall use compatible types"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Binary operators shall use operands "
        "with compatible essential types."
    )

    RATIONALE = (
        "Mixed essential types reduce portability."
    )

    FIXABLE = False

    PRIORITY = 104

    CAPABILITIES = ("semantic",)

    _BINARY_PATTERN = re.compile(
        r"""
        ([A-Za-z_]\w*)
        \s*
        (\+|-|\*|/|%)
        \s*
        ([A-Za-z_]\w*)
        """,
        re.VERBOSE,
    )

    def check(self, code, file_path):
        violations = []

        pattern = re.compile(r"\w+\s*[\+\-\*/]\s*\w+")

        for line_no, raw, line in self.iter_lines(code):
            if pattern.search(line):
                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_no,
                    original=raw,
                    explanation="Binary operator mixes essential types.",
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

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
    analysis_context
)

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            for match in self._BINARY_PATTERN.finditer(
                line
            ):

                left = expression_type(
                    match.group(1),
                    declaration_table,
                )

                right = expression_type(
                    match.group(3),
                    declaration_table,
                )

                if compatible(
                    left,
                    right,
                ):
                    continue

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line,
                        explanation=(
                            "Binary operator uses "
                            "different essential types."
                        ),
                    )
                )

        return violations


# ---------------------------------------------------------
# Rule 10.5
# ---------------------------------------------------------


class Rule105(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 10.5
    """

    RULE_ID = "10.5"

    TITLE = "Cast shall preserve essential type"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Advisory"

    DESCRIPTION = (
        "Casts should preserve the essential type."
    )

    RATIONALE = (
        "Unnecessary casts hide programming errors."
    )

    FIXABLE = False

    PRIORITY = 105

    CAPABILITIES = ("text",)

    def check(
    self,
    code,
    file_path,
):

        violations = []

        for line_number, raw_line, line in self.iter_lines(code):

            cast = _CAST_PATTERN.search(line)

            if cast is None:
                continue

            violations.append(
            self.create_violation(
                file_path=file_path,
                line=line_number,
                original=raw_line,
                explanation=(
                    "Review explicit cast for "
                    "essential type compatibility."
                ),
            )
        )

        # Only report the first explicit cast
            break

        return violations
    
# ---------------------------------------------------------
# Rule 10.6
# ---------------------------------------------------------


class Rule106(RuleMixin, BaseRule):
    """
    MISRA C:2012 Rule 10.6
    """

    RULE_ID = "10.6"

    TITLE = "Composite expressions shall not widen assignments"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Composite expressions shall not be assigned "
        "to a wider essential type."
    )

    RATIONALE = (
        "Implicit widening hides conversion intent."
    )

    FIXABLE = False

    PRIORITY = 106

    CAPABILITIES = ("semantic",)

    def check(self, code, file_path):
        violations = []

        for line_no, raw, line in self.iter_lines(code):
            if "=" in line and any(op in line for op in ["+","-","*","/"]):
                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_no,
                    original=raw,
                    explanation="Composite expression assignment.",
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

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
    analysis_context
)

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            match = _ASSIGNMENT_PATTERN.search(line)

            if match is None:
                continue

            lhs = match.group(1)

            rhs = match.group(2)

            if (
                "+"
                not in rhs
                and "-"
                not in rhs
                and "*"
                not in rhs
                and "/"
                not in rhs
            ):
                continue

            if lhs not in declaration_table:
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Composite expression assigned "
                        "to another essential type."
                    ),
                )
            )

        return violations
    
# ---------------------------------------------------------
# Rule 10.7
# ---------------------------------------------------------


class Rule107(RuleMixin, BaseRule):

    RULE_ID = "10.7"

    TITLE = "Composite operands shall use compatible types"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Composite operands shall use compatible "
        "essential types."
    )

    RATIONALE = (
        "Mixed-type composite expressions "
        "reduce portability."
    )

    FIXABLE = False

    PRIORITY = 107

    CAPABILITIES = ("semantic",)

    def check(self, code, file_path):
        violations=[]

        pattern=re.compile(r"\w+\s*[\+\-\*/]\s*\w+\s*[\+\-\*/]\s*\w+")

        for line_no, raw, line in self.iter_lines(code):
            if pattern.search(line):
                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_no,
                    original=raw,
                    explanation="Composite expression mixes types.",
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

        if analysis_context is None:
            return []

        declaration_table = self.declaration_table(
        analysis_context
    )

        violations = []

        binary_pattern = re.compile(
        r"""
        ([A-Za-z_]\w*)
        \s*
        (\+|-|\*|/|%)
        \s*
        ([A-Za-z_]\w*)
        \s*
        (\+|-|\*|/|%)
        \s*
        ([A-Za-z_]\w*)
        """,
        re.VERBOSE,
    )

        for line_number, raw_line, line in self.iter_lines(
        code
    ):

            for match in binary_pattern.finditer(
            line
        ):

                operands = (
                match.group(1),
                match.group(3),
                match.group(5),
            )

                types = []

                for operand in operands:

                    essential = expression_type(
                    operand,
                    declaration_table,
                )

                    if essential.category == "unknown":
                        continue

                    types.append(
                    essential.category
                )

                if len(set(types)) <= 1:
                    continue

                violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Composite expression mixes "
                        "different essential type "
                        "categories."
                    ),
                )
            )

        return violations
    

# ---------------------------------------------------------
# Rule 10.8
# ---------------------------------------------------------


class Rule108(RuleMixin,BaseRule):

    RULE_ID = "10.8"

    TITLE = "Composite expression shall not be cast"

    CHAPTER = "10"

    CATEGORY = "Essential Type Model"

    SEVERITY = "Required"

    DESCRIPTION = (
        "Composite expressions should not be "
        "cast to different essential types."
    )

    RATIONALE = (
        "Casting composite expressions may hide "
        "unexpected conversions."
    )

    FIXABLE = False

    PRIORITY = 108

    CAPABILITIES=("hybrid",)

    def check(
        self,
        code,
        file_path,
    ):

        violations = []

        for line_number, raw_line, line in self.iter_lines(
    code
):

            if "(" not in line:
                continue

            if ")" not in line:
                continue

            if "+" not in line and "-" not in line:
                continue

            if not _CAST_PATTERN.search(line):
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_number,
                    original=raw_line,
                    explanation=(
                        "Composite expression is cast."
                    ),
                )
            )

        return violations

__all__ = (
    "Rule101",
    "Rule102",
    "Rule103",
    "Rule104",
    "Rule105",
    "Rule106",
    "Rule107",
    "Rule108",
)
