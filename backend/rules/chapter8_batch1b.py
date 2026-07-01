import re

from rules.base_rule import BaseRule


class Rule86(BaseRule):
    RULE_ID = "8.6"
    TITLE = "Identifier declarations and definitions shall be unique within a scope"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Identifiers shall not be declared in a nested scope if they shadow an identifier in an enclosing scope."
    RATIONALE = "Shadowing makes code harder to follow and increases the chance of unintended name resolution bugs."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.6",)
    PRIORITY = 32
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        scope_stack = [{}]

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = re.sub(r"//.*", "", raw_line)
            line = re.sub(r"/\*.*?\*/", "", line)

            if "{" in line:
                scope_stack.append(scope_stack[-1].copy())
            if "}" in line and len(scope_stack) > 1:
                scope_stack.pop()

            for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", line):
                token = match.group(1)
                if token in {"if", "for", "while", "switch", "return", "sizeof", "int", "void", "char", "float", "double", "short", "long", "signed", "unsigned", "const", "volatile", "static", "extern", "register", "struct", "union", "enum", "bool", "_Bool"}:
                    continue
                if token in scope_stack[-1]:
                    continue
                scope_stack[-1][token] = True

            if re.search(r"\bint\b|\bchar\b|\bfloat\b|\bdouble\b|\bvoid\b|\bshort\b|\blong\b|\bsigned\b|\bunsigned\b|\bbool\b|\b_Bool\b", line):
                if re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\s*(?:=|;|\)|,)", line):
                    decl_match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;|\)|,)", line)
                    if decl_match:
                        name = decl_match.group(1)
                        if len(scope_stack) > 1 and name in scope_stack[-2]:
                            violations.append(
                                self.create_violation(
                                    file_path=file_path,
                                    line=line_number,
                                    original=raw_line.strip(),
                                    explanation=(
                                        f"Identifier '{name}' shadows an outer-scope declaration; "
                                        "review the declaration and use a unique name."
                                    ),
                                )
                            )
                            break

        return violations


class Rule88(BaseRule):
    RULE_ID = "8.8"
    TITLE = "Objects and functions with internal linkage shall be declared static"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Functions or objects intended to have internal linkage should be declared static."
    RATIONALE = "Static declarations make linkage explicit and prevent unintended exposure across translation units."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 8.8",)
    PRIORITY = 33
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        brace_depth = 0

        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = re.sub(r"//.*", "", raw_line)
            line = re.sub(r"/\*.*?\*/", "", line)
            stripped = line.strip()
            if not stripped:
                continue

            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth != 0:
                continue

            if re.match(r"^(?:static|extern|typedef|inline|__inline|__inline__)\b", stripped):
                continue
            if re.search(r"\b(?:int|char|float|double|void|short|long|signed|unsigned|bool|_Bool)\b", stripped) and re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped):
                name_match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped)
                if not name_match:
                    continue
                name = name_match.group(1)
                if name in {"main", "if", "for", "while", "switch", "return"}:
                    continue
                if "static" not in stripped:
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line_number,
                            original=raw_line.strip(),
                            explanation=(
                                "This function declaration should be declared static to make internal linkage explicit."
                            ),
                        )
                    )
        return violations
