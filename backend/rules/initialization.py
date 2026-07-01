import re

from rules.base_rule import BaseRule

_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:unsigned\s+|signed\s+|const\s+|volatile\s+|static\s+|extern\s+|register\s+|short\s+|long\s+|int\s+|char\s+|float\s+|double\s+|_Bool\s+|bool\s+|struct\s+|union\s+|enum\s+)(?P<decl>[^;]+);"
)
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


def _strip_comments(line):
    line = re.sub(r"//.*", "", line)
    line = re.sub(r"/\*.*?\*/", "", line)
    return line


def _is_function_prototype(declaration):
    return "(" in declaration and ")" in declaration and "=" not in declaration


def _extract_declarators(declarator_text):
    parts = []
    current = []
    depth = 0
    for char in declarator_text:
        if char == "(" or char == "[":
            depth += 1
        elif char == ")" or char == "]":
            depth = max(depth - 1, 0)

        if char == "," and depth == 0:
            token = "".join(current).strip()
            if token:
                parts.append(token)
            current = []
            continue
        current.append(char)

    token = "".join(current).strip()
    if token:
        parts.append(token)
    return parts


def _extract_symbol(declarator):
    match = _SYMBOL_PATTERN.match(declarator.strip())
    if match:
        return match.group(1)
    return None


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
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        scope_stack = [{}]

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = _strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match = _DECLARATION_PATTERN.match(line)
            if declaration_match:
                declaration = declaration_match.group("decl")
                if _is_function_prototype(declaration):
                    continue

                for declarator in _extract_declarators(declaration):
                    if "=" in declarator:
                        symbol = _extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = _extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = False
                continue

            for assignment_match in _ASSIGNMENT_PATTERN.finditer(line):
                symbol = assignment_match.group(1)
                if symbol not in _IGNORE_SYMBOLS:
                    scope_stack[-1][symbol] = True

            tokens = [token for token in _SYMBOL_PATTERN.findall(line) if token not in _IGNORE_SYMBOLS]
            for token in tokens:
                if token in scope_stack[-1] and not scope_stack[-1][token]:
                    if re.search(rf"\b{re.escape(token)}\b\s*=(?!=)", line):
                        continue
                    if re.search(rf"sizeof\s*\(\s*{re.escape(token)}\b", line):
                        continue

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line.strip(),
                            explanation=(
                                "This object is used before it has been initialized. "
                                "Initialize objects prior to use to avoid undefined behavior."
                            ),
                        )
                    )
                    break

        return violations


class Rule92(BaseRule):
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
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        scope_stack = [{}]

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = _strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match = _DECLARATION_PATTERN.match(line)
            if declaration_match:
                declaration = declaration_match.group("decl")
                if _is_function_prototype(declaration):
                    continue

                for declarator in _extract_declarators(declaration):
                    if "=" in declarator:
                        symbol = _extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = _extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = False
                continue

            for assignment_match in _ASSIGNMENT_PATTERN.finditer(line):
                symbol = assignment_match.group(1)
                if symbol not in _IGNORE_SYMBOLS:
                    scope_stack[-1][symbol] = True

            tokens = [token for token in _SYMBOL_PATTERN.findall(line) if token not in _IGNORE_SYMBOLS]
            for token in tokens:
                if token in scope_stack[-1] and not scope_stack[-1][token]:
                    if re.search(rf"\b{re.escape(token)}\b\s*=(?!=)", line):
                        continue
                    if re.search(rf"sizeof\s*\(\s*{re.escape(token)}\b", line):
                        continue

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line.strip(),
                            explanation=(
                                "This object value is read before the object has been given a value. "
                                "Assign a value before reading from the object."
                            ),
                        )
                    )
                    break

        return violations


class Rule93(BaseRule):
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
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        scope_stack = [{}]

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = _strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match = _DECLARATION_PATTERN.match(line)
            if declaration_match:
                declaration = declaration_match.group("decl")
                if _is_function_prototype(declaration):
                    continue

                for declarator in _extract_declarators(declaration):
                    key = declarator.strip()
                    if "=" in key:
                        symbol = _extract_symbol(key)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = _extract_symbol(key)
                        if symbol:
                            scope_stack[-1][symbol] = False
                continue

            for assignment_match in _ASSIGNMENT_PATTERN.finditer(line):
                symbol = assignment_match.group(1)
                if symbol not in _IGNORE_SYMBOLS:
                    scope_stack[-1][symbol] = True

            for symbol, initialized in list(scope_stack[-1].items()):
                if not initialized and re.search(rf"\b{re.escape(symbol)}\b", line):
                    if re.search(rf"\b{re.escape(symbol)}\b\s*=(?!=)", line):
                        continue
                    if re.search(rf"\bsizeof\s*\(\s*{re.escape(symbol)}\b", line):
                        continue
                    if re.search(rf"\b&\s*{re.escape(symbol)}\b", line):
                        continue

                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line.strip(),
                            explanation=(
                                "A full object is read before it has been initialized. "
                                "Ensure full objects are initialized before they are used."
                            ),
                        )
                    )
                    break

        return violations
