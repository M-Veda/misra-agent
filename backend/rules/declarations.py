import re

from rules.base_rule import BaseRule

_TYPE_KEYWORDS = {
    "auto",
    "const",
    "volatile",
    "register",
    "static",
    "extern",
    "signed",
    "unsigned",
    "short",
    "long",
    "int",
    "char",
    "float",
    "double",
    "void",
    "_Bool",
    "bool",
    "struct",
    "union",
    "enum",
}

_FUNCTION_DECL_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:[A-Za-z_][\w\s\*]*\s+)+([A-Za-z_]\w*)\s*\(\s*([^)]*)\s*\)\s*(?:;|\{|$)"
)

_GLOBAL_DECL_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:[A-Za-z_][\w\s\*]*\s+)+([A-Za-z_]\w*)\s*(?:\(|\[|;|=)"
)


def _split_parameters(parameter_list):
    if not parameter_list.strip():
        return []

    result = []
    current = []
    depth = 0

    for char in parameter_list:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(depth - 1, 0)

        if char == "," and depth == 0:
            token = "".join(current).strip()
            if token:
                result.append(token)
            current = []
            continue

        current.append(char)

    token = "".join(current).strip()
    if token:
        result.append(token)

    return result


def _contains_named_parameter(token):
    token = token.strip()
    if token == "void":
        return True

    if re.search(r"\(\s*\*\s*[A-Za-z_]\w*\s*\)", token):
        return True

    names = re.findall(r"[A-Za-z_]\w*", token)
    if not names:
        return False

    return names[-1] not in _TYPE_KEYWORDS


def _is_pointer_parameter(token):
    token = token.strip()
    if "*" not in token:
        return False
    if re.search(r"\(\s*\*\s*[A-Za-z_]\w*\s*\)", token):
        return False
    return "[" not in token


def _is_supported_top_level_declaration(line):
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "//", "/*", "*")):
        return False

    if stripped.startswith(("static ", "extern ", "typedef ", "inline ", "__inline", "__inline__")):
        return False

    if _GLOBAL_DECL_PATTERN.match(stripped):
        return True

    return False


def _declaration_snippet(match_text):
    if not match_text:
        return ""
    return match_text.strip().splitlines()[0].strip()


class Rule81(BaseRule):
    RULE_ID = "8.1"
    TITLE = "Function shall have prototype"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Function declarations and definitions shall declare all parameters explicitly."
    RATIONALE = "Explicit parameter lists prevent implicit interfaces and improve type checking reliability."
    FIXABLE = True
    REFERENCES = ("MISRA C:2012 Rule 8.1",)
    PRIORITY = 30
    FIX_STRATEGY = "prototype_void_parameter"
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []

        for match in _FUNCTION_DECL_PATTERN.finditer(code):
            parameter_list = match.group(2)
            if parameter_list.strip():
                continue

            original = _declaration_snippet(match.group(0))
            line = code.count("\n", 0, match.start()) + 1
            suggestion = re.sub(r"\(\s*\)", "(void)", original, count=1)

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion=suggestion,
                    explanation=(
                        "Function declarations with empty parameter lists should be rewritten "
                        "using explicit void notation to form a complete prototype."
                    ),
                )
            )

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        return self.check(code, file_path)

    def suggest_fix(self, violation):
        return violation.suggested_code or None


class Rule82(BaseRule):
    RULE_ID = "8.2"
    TITLE = "Function declarations shall specify parameter names for all parameters"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Function parameter lists shall include explicit names for all parameters."
    RATIONALE = "Parameter names make the interface contract more readable and maintainable."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.2",)
    PRIORITY = 31
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []

        for match in _FUNCTION_DECL_PATTERN.finditer(code):
            parameter_list = match.group(2)
            if not parameter_list.strip() or parameter_list.strip() == "void":
                continue

            for token in _split_parameters(parameter_list):
                if not _contains_named_parameter(token):
                    original = _declaration_snippet(match.group(0))
                    line = code.count("\n", 0, match.start()) + 1
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            original=original,
                            suggestion=(
                                "Review this declaration and add explicit parameter names where missing."
                            ),
                            explanation=(
                                "Function declarations should specify parameter names for every parameter "
                                "to make the interface explicit."
                            ),
                        )
                    )
                    break

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        return self.check(code, file_path)


class Rule84(BaseRule):
    RULE_ID = "8.4"
    TITLE = "Array declarator parameters shall use array notation"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Function parameters representing arrays should be declared using array notation."
    RATIONALE = "Array notation clarifies the intended use of a parameter as an array."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.4",)
    PRIORITY = 32
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []

        for match in _FUNCTION_DECL_PATTERN.finditer(code):
            parameter_list = match.group(2)
            for token in _split_parameters(parameter_list):
                if _is_pointer_parameter(token):
                    original = _declaration_snippet(match.group(0))
                    line = code.count("\n", 0, match.start()) + 1
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            original=original,
                            suggestion=(
                                "Review this pointer parameter and consider using array notation for clarity."
                            ),
                            explanation=(
                                "Pointer notation for function parameters that represent arrays should be reviewed "
                                "and rewritten using array notation when appropriate."
                            ),
                        )
                    )
                    break

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        return self.check(code, file_path)


class Rule87(BaseRule):
    RULE_ID = "8.7"
    TITLE = "Objects and functions shall not have external linkage unless required"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "File-scope objects and functions should not expose external linkage unless it is required."
    RATIONALE = "Reducing external linkage minimizes global coupling and improves encapsulation."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.7",)
    PRIORITY = 33
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []
        brace_depth = 0
        lines = code.splitlines()

        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*")):
                brace_depth += stripped.count("{") - stripped.count("}")
                continue

            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth != 0:
                continue

            if _is_supported_top_level_declaration(stripped):
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=index,
                        original=stripped,
                        suggestion=(
                            "Review whether this file-scope declaration should be restricted to internal linkage."
                        ),
                        explanation=(
                            "This declaration has external linkage by default. Confirm whether external linkage "
                            "is required or whether visibility can be restricted."
                        ),
                    )
                )

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        return self.check(code, file_path)
