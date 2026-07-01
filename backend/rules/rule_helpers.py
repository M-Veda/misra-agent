import re


_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:unsigned\s+|signed\s+|const\s+|volatile\s+|static\s+|extern\s+|register\s+|short\s+|long\s+|int\s+|char\s+|float\s+|double\s+|_Bool\s+|bool\s+|struct\s+|union\s+|enum\s+)(?P<decl>[^;]+);"
)
_FULL_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?P<decl>[^;]+);"
)
_SYMBOL_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\b")
_TYPE_KEYWORDS = {
    "auto",
    "const",
    "volatile",
    "register",
    "static",
    "extern",
    "typedef",
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
    "if",
    "for",
    "while",
    "switch",
    "return",
    "sizeof",
}


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
    text = (declarator or "").strip()
    if not text:
        return None

    tokens = [token for token in _SYMBOL_PATTERN.findall(text) if token not in _TYPE_KEYWORDS]
    if not tokens:
        return None
    return tokens[-1]


def declaration_match(line):
    return _DECLARATION_PATTERN.match(line)


def full_declaration_match(line):
    return _FULL_DECLARATION_PATTERN.match(line)


def declaration_snippet(match_text):
    if not match_text:
        return ""
    return match_text.strip().splitlines()[0].strip()


def normalize_declaration_signature(declaration):
    signature = strip_comments(declaration or "").strip()
    if not signature:
        return ""

    signature = re.sub(r"\s+", " ", signature)
    signature = re.sub(r"\s*=\s*.*$", "", signature)
    signature = re.sub(r"\s*\([^)]*\)\s*$", "", signature)
    signature = re.sub(r"\s*\[[^\]]*\]\s*$", "", signature)
    signature = re.sub(r"\s+([A-Za-z_]\w*)\s*$", "", signature)
    for storage_class in ("extern", "static", "register", "typedef", "auto"):
        signature = re.sub(rf"\b{re.escape(storage_class)}\b", "", signature)
    signature = re.sub(r"\s+", " ", signature).strip(" ;")
    return signature


def declaration_has_storage_class(declaration, storage_class):
    return bool(re.search(rf"\b{re.escape(storage_class)}\b", declaration or ""))
