import re


_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:unsigned\s+|signed\s+|const\s+|volatile\s+|static\s+|extern\s+|register\s+|short\s+|long\s+|int\s+|char\s+|float\s+|double\s+|_Bool\s+|bool\s+|struct\s+|union\s+|enum\s+)(?P<decl>[^;]+);"
)
_SYMBOL_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\b")


def strip_comments(line):
    line = re.sub(r"//.*", "", line)
    line = re.sub(r"/\*.*?\*/", "", line)
    return line


def is_function_prototype(declaration):
    return "(" in declaration and ")" in declaration and "=" not in declaration


def extract_declarators(declarator_text):
    parts = []
    current = []
    depth = 0
    for char in declarator_text:
        if char in "([":
            depth += 1
        elif char in ")]":
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


def extract_symbol(declarator):
    match = _SYMBOL_PATTERN.match(declarator.strip())
    if match:
        return match.group(1)
    return None


def declaration_match(line):
    return _DECLARATION_PATTERN.match(line)


def declaration_snippet(match_text):
    if not match_text:
        return ""
    return match_text.strip().splitlines()[0].strip()
