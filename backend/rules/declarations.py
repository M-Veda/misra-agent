import re

from rules.base_rule import BaseRule
from rules.rule_helpers import (
    declaration_has_storage_class,
    declaration_match,
    declaration_snippet,
    extract_declarators,
    extract_symbol,
    full_declaration_match,
    is_function_prototype,
    normalize_declaration_signature,
    strip_comments,
)

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


def _extract_file_scope_objects(code):
    objects = []
    brace_depth = 0

    for line_number, raw_line in enumerate(code.splitlines(), start=1):
        line = strip_comments(raw_line)
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "/*", "*")):
            continue

        brace_depth += stripped.count("{") - stripped.count("}")
        if brace_depth != 0:
            continue

        if stripped.startswith(("typedef", "extern", "static", "inline", "__inline", "__inline__")):
            continue
        if "(" in stripped and ")" in stripped and ";" in stripped:
            continue
        if not re.search(r"\b(?:int|char|float|double|void|short|long|signed|unsigned|bool|_Bool|struct|union|enum)\b", stripped):
            continue

        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;)", stripped)
        if not match:
            continue

        objects.append({"name": match.group(1), "line": line_number})

    return objects


def _extract_function_definitions(code):
    functions = []
    pattern = re.compile(r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;{]*\)\s*\{", re.MULTILINE)

    for match in pattern.finditer(code):
        opening_brace = match.end() - 1
        depth = 0
        end_index = None
        for index in range(opening_brace, len(code)):
            char = code[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end_index = index
                    break
        if end_index is None:
            continue

        body = code[opening_brace + 1:end_index]
        functions.append(
            {
                "name": match.group("name"),
                "line": code.count("\n", 0, opening_brace) + 1,
                "body": body,
            }
        )

    return functions


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

            original = declaration_snippet(match.group(0))
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
                    original = declaration_snippet(match.group(0))
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


class Rule83(BaseRule):
    RULE_ID = "8.3"
    TITLE = "All declarations of an object or function shall use the same type and type qualifiers"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "All declarations of an object or function shall use the same type and type qualifiers."
    RATIONALE = "Consistent declarations make interfaces easier to understand and reduce the risk of accidental type mismatches."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.3",)
    PRIORITY = 32
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []
        seen_symbols = {}

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = strip_comments(raw_line)
            match_result = full_declaration_match(line)
            if not match_result:
                continue

            declaration = match_result.group("decl")
            if is_function_prototype(declaration) or declaration_has_storage_class(declaration, "typedef"):
                continue

            signature = normalize_declaration_signature(declaration)
            if not signature:
                continue

            for declarator in extract_declarators(declaration):
                symbol = extract_symbol(declarator)
                if not symbol:
                    continue

                previous = seen_symbols.get(symbol)
                if previous is None:
                    seen_symbols[symbol] = {"signature": signature, "line": line_number}
                    continue

                if previous["signature"] != signature:
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line.strip(),
                            suggestion=(
                                "Review these declarations and ensure the same type and qualifiers are used for this identifier."
                            ),
                            explanation=(
                                f"Identifier '{symbol}' is declared with inconsistent type information. "
                                "All declarations of an object or function should use the same type and type qualifiers."
                            ),
                            metadata={
                                "symbol": symbol,
                                "previous_signature": previous["signature"],
                                "current_signature": signature,
                            },
                        )
                    )
                    break

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        violations = self.check(code, file_path)
        if analysis_context and getattr(analysis_context, "available", False):
            for violation in violations:
                violation.metadata["analysis_available"] = True
        return violations


class Rule85(BaseRule):
    RULE_ID = "8.5"
    TITLE = "There shall be no more than one declaration of an identifier in a translation unit"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "There shall be no more than one declaration of an identifier in a translation unit."
    RATIONALE = "Repeated declarations make dependencies harder to reason about and can hide accidental linkage mistakes."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.5",)
    PRIORITY = 32
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        violations = []
        seen_symbols = {}

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = strip_comments(raw_line)
            match_result = full_declaration_match(line)
            if not match_result:
                continue

            declaration = match_result.group("decl")
            if is_function_prototype(declaration) or declaration_has_storage_class(declaration, "typedef"):
                continue
            if declaration_has_storage_class(declaration, "static"):
                continue

            for declarator in extract_declarators(declaration):
                symbol = extract_symbol(declarator)
                if not symbol:
                    continue

                previous = seen_symbols.get(symbol)
                if previous is None:
                    seen_symbols[symbol] = line_number
                    continue

                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=raw_line.strip(),
                        suggestion=(
                            "Review this declaration and ensure the identifier is not declared more than once."
                        ),
                        explanation=(
                            f"Identifier '{symbol}' is declared more than once in the translation unit. "
                            "There should be one and only one declaration for an identifier with external linkage."
                        ),
                        metadata={"symbol": symbol, "previous_line": previous},
                    )
                )
                break

        return violations

    def check_with_context(self, code, file_path, analysis_context=None):
        violations = self.check(code, file_path)
        if analysis_context and getattr(analysis_context, "available", False):
            for violation in violations:
                violation.metadata["analysis_available"] = True
        return violations


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
                    original = declaration_snippet(match.group(0))
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


class Rule814(BaseRule):
    RULE_ID = "8.14"
    TITLE = "The register storage class specifier shall not be used"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "The register storage class specifier shall not be used."
    RATIONALE = "The register storage class specifier is not portable and may be ignored by the implementation."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.14",)
    PRIORITY = 40
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = self._strip_strings_and_char_literals(line)
            if re.search(r"\bregister\b", cleaned_line):
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            "The register storage class specifier is not permitted; use a normal declaration instead."
                        ),
                    )
                )
        return violations

    @staticmethod
    def _strip_strings_and_char_literals(line):
        result = []
        index = 0
        in_string = None
        while index < len(line):
            char = line[index]
            if in_string is None:
                if char in {'"', "'"}:
                    in_string = char
                    result.append(" ")
                    index += 1
                    continue
                result.append(char)
                index += 1
                continue

            if char == "\\" and index + 1 < len(line):
                result.append(" ")
                result.append(" ")
                index += 2
                continue

            if char == in_string:
                in_string = None
                result.append(" ")
                index += 1
                continue

            result.append(" ")
            index += 1

        return "".join(result)


class Rule89(BaseRule):
    RULE_ID = "8.9"
    TITLE = "A file-scope object should be declared in block scope if it is only used by one function"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "A file-scope object that is only used by one function should be reviewed for placement in block scope."
    RATIONALE = "Restricting an object to the narrowest scope reduces coupling and makes ownership clearer."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.9",)
    PRIORITY = 34
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        return self._check(code, file_path, analysis_context=None)

    def check_with_context(self, code, file_path, analysis_context=None):
        return self._check(code, file_path, analysis_context=analysis_context)

    def _check(self, code, file_path, analysis_context=None):
        violations = []
        objects = _extract_file_scope_objects(code)
        functions = _extract_function_definitions(code)
        if not objects or not functions:
            return violations

        for declaration in objects:
            name = declaration["name"]
            users = []
            for function in functions:
                if re.search(rf"\b{re.escape(name)}\b", function["body"]):
                    users.append(function["name"])

            if len(set(users)) != 1:
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=declaration["line"],
                    original=declaration["name"],
                    suggestion="Consider moving this object to block scope if it is only required by one function.",
                    explanation=(
                        f"Object '{name}' appears to be used by only one function. "
                        "Review whether it should be moved to block scope to reduce file-scope coupling."
                    ),
                    metadata={
                        "symbol": name,
                        "used_by": users[0],
                        "analysis_available": bool(analysis_context and getattr(analysis_context, "available", False)),
                    },
                )
            )

        return violations


class Rule810(BaseRule):
    RULE_ID = "8.10"
    TITLE = "A file-scope function should be reviewed if it is only used by one function"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "A file-scope function that is only used by one function should be reviewed for scope reduction."
    RATIONALE = "Reducing a function's exposure to the rest of the translation unit improves encapsulation and maintainability."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.10",)
    PRIORITY = 35
    CAPABILITIES = ("hybrid",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "hybrid"}

    def check(self, code, file_path):
        return self._check(code, file_path, analysis_context=None)

    def check_with_context(self, code, file_path, analysis_context=None):
        return self._check(code, file_path, analysis_context=analysis_context)

    def _check(self, code, file_path, analysis_context=None):
        violations = []
        functions = _extract_function_definitions(code)
        if not functions:
            return violations

        for function in functions:
            name = function["name"]
            if name in {"main"}:
                continue

            callers = []
            for candidate in functions:
                if candidate["name"] == name:
                    continue
                if re.search(rf"\b{re.escape(name)}\b", candidate["body"]):
                    callers.append(candidate["name"])

            if len(set(callers)) != 1:
                continue

            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=function["line"],
                    original=name,
                    suggestion="Consider whether this function should be restricted to the single caller that uses it.",
                    explanation=(
                        f"Function '{name}' appears to be used by only one function. "
                        "Review whether it should be restricted to block scope or otherwise reduced in visibility."
                    ),
                    metadata={
                        "symbol": name,
                        "called_by": callers[0],
                        "analysis_available": bool(analysis_context and getattr(analysis_context, "available", False)),
                    },
                )
            )

        return violations
