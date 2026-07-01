import re

from rules.base_rule import BaseRule
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
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Initialization", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        scope_stack = [{}]

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match_result = declaration_match(line)
            if declaration_match_result:
                declaration = declaration_match_result.group("decl")
                if is_function_prototype(declaration):
                    continue

                for declarator in extract_declarators(declaration):
                    if "=" in declarator:
                        symbol = extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = extract_symbol(declarator)
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
            line = strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match_result = declaration_match(line)
            if declaration_match_result:
                declaration = declaration_match_result.group("decl")
                if is_function_prototype(declaration):
                    continue

                for declarator in extract_declarators(declaration):
                    if "=" in declarator:
                        symbol = extract_symbol(declarator)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = extract_symbol(declarator)
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
            line = strip_comments(raw_line)
            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            declaration_match_result = declaration_match(line)
            if declaration_match_result:
                declaration = declaration_match_result.group("decl")
                if is_function_prototype(declaration):
                    continue

                for declarator in extract_declarators(declaration):
                    key = declarator.strip()
                    if "=" in key:
                        symbol = extract_symbol(key)
                        if symbol:
                            scope_stack[-1][symbol] = True
                    else:
                        symbol = extract_symbol(key)
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
