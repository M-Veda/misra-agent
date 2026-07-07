import re


_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?:unsigned\s+|signed\s+|const\s+|volatile\s+|static\s+|extern\s+|register\s+|short\s+|long\s+|int\s+|char\s+|float\s+|double\s+|_Bool\s+|bool\s+|struct\s+|union\s+|enum\s+)(?P<decl>[^;]+);"
)
_FULL_DECLARATION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?P<decl>[^;]+);"
)
_SYMBOL_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\b")
_COMMENT_LINE_PATTERN = re.compile(r"//.*")
_BLOCK_COMMENT_PATTERN = re.compile(r"/\*.*?\*/")
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
    line = _COMMENT_LINE_PATTERN.sub("", line)
    line = _BLOCK_COMMENT_PATTERN.sub("", line)
    return line


def strip_string_literals(text):
    result = []
    index = 0
    in_string = None
    while index < len(text):
        char = text[index]
        if in_string is None:
            if char in {'"', "'"}:
                in_string = char
                result.append(" ")
                index += 1
                continue
            result.append(char)
            index += 1
            continue

        if char == "\\" and index + 1 < len(text):
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

_IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def is_identifier(token):
    """
    Returns True if token is a valid C identifier.
    """

    if token is None:
        return False

    return bool(_IDENTIFIER_PATTERN.fullmatch(token))


def count_pointer_level(declaration):
    """
    Returns pointer indirection level.

    Examples
    --------
    int a;          -> 0
    int *a;         -> 1
    int **a;        -> 2
    int ***a;       -> 3
    """

    if not declaration:
        return 0

    return len(re.findall(r"\*", declaration))


def is_array_declaration(declaration):
    """
    Detects whether the declaration is an array.
    """

    return bool(
    re.search(
        r"\[[^\]]*\]",
        declaration or "",
    )
)


def is_pointer_declaration(declaration):
    """
    Detects pointer declarations.
    """

    return bool(
    re.search(
        r"\*",
        declaration or "",
    )
)


def remove_initializer(declaration):
    """
    Removes initializer while preserving declaration.

    Example:
        int x = 5;
        ->
        int x;
    """

    if not declaration:
        return ""

    declaration = re.sub(
        r"\s*=\s*.*",
        "",
        declaration,
    ).strip()

    if not declaration.endswith(";"):
        declaration += ";"

    return declaration


def declaration_type(declaration):
    """
    Returns the primitive type if one exists.
    """

    declaration = declaration or ""

    primitive_types = (
        "void",
        "char",
        "short",
        "int",
        "long",
        "float",
        "double",
        "_Bool",
        "bool",
    )

    for primitive in primitive_types:

        if re.search(
            rf"\b{primitive}\b",
            declaration,
        ):
            return primitive

    return "unknown"


def declaration_is_const(declaration):
    return bool(
        re.search(
            r"\bconst\b",
            declaration or "",
        )
    )


def declaration_is_static(declaration):
    return bool(
        re.search(
            r"\bstatic\b",
            declaration or "",
        )
    )


def declaration_is_extern(declaration):
    return bool(
        re.search(
            r"\bextern\b",
            declaration or "",
        )
    )


def normalize_whitespace(text):
    """
    Converts multiple whitespace characters
    into a single space.
    """

    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def safe_lines(code):
    """
    Returns code lines while preserving
    line numbering.
    """

    if not code:
        return []

    return code.splitlines()


def line_at(code, line_number):
    """
    Returns a specific source line.
    """

    lines = safe_lines(code)

    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]

    return ""


def declaration_is_volatile(declaration):
    return bool(
        re.search(
            r"\bvolatile\b",
            declaration or "",
        )
    )


def declaration_is_typedef(declaration):
    return bool(
        re.search(
            r"\btypedef\b",
            declaration or "",
        )
    )


def declaration_is_function(declaration):
    return bool(
        re.search(
            r"\([^)]*\)",
            declaration or "",
        )
    )


def declaration_is_initialized(declaration):
    return "=" in (declaration or "")

def contains_keyword(text, keyword):
    return bool(
        re.search(
            rf"\b{re.escape(keyword)}\b",
            text or "",
        )
    )
