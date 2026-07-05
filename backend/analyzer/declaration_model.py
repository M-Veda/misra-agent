import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


_STORAGE_SPECIFIERS = {"static", "extern", "register", "typedef", "auto"}
_QUALIFIERS = {"const", "volatile", "restrict"}
_CONTROL_KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "do", "else"}
_BUILTIN_TYPE_WORDS = {
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
}
_TYPE_PREFIX_WORDS = _STORAGE_SPECIFIERS | _QUALIFIERS | _BUILTIN_TYPE_WORDS | {"struct", "union", "enum"}
_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_COMMENT_LINE_PATTERN = re.compile(r"//.*")
_BLOCK_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.S)
_FUNCTION_PATTERN = re.compile(
    r"(?mx)^[^\S\n]*(?P<prefix>(?:[A-Za-z_]\w*|\*|\s)+?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<parameters>[^;{}]*)\)\s*(?P<tail>;|\{|$)"
)
_TYPEDEF_PATTERN = re.compile(r"\btypedef\b(?P<rest>.*?);", re.S)
_BIT_FIELD_PATTERN = re.compile(
    r"\b(struct|union)\s+[A-Za-z_][A-Za-z0-9_]*\s*\{(?P<body>[^}]*)\}", re.S
)
_BIT_FIELD_DECLARATOR_PATTERN = re.compile(
    r"\b(?P<type>(?:signed|unsigned)\s+char|[A-Za-z_][A-Za-z0-9_\s]*?)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<width>\d+)"
)


@dataclass(slots=True)
class Declaration:
    kind: str
    name: Optional[str] = None
    type_name: Optional[str] = None
    storage_specifiers: Tuple[str, ...] = field(default_factory=tuple)
    qualifiers: Tuple[str, ...] = field(default_factory=tuple)
    typedef_name: Optional[str] = None
    is_bit_field: bool = False
    bit_width: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None
    signedness: Optional[str] = None
    alias_of: Optional[str] = None

    @classmethod
    def from_mapping(cls, declaration: Any) -> "Declaration":
        if isinstance(declaration, cls):
            return declaration
        if declaration is None:
            return cls(kind="unknown")
        if not isinstance(declaration, dict):
            return cls(kind="unknown", raw={"value": declaration})
        return cls(
            kind=declaration.get("kind", "unknown"),
            name=declaration.get("name"),
            type_name=declaration.get("type_name"),
            storage_specifiers=tuple(declaration.get("storage_specifiers", [])),
            qualifiers=tuple(declaration.get("qualifiers", [])),
            typedef_name=declaration.get("typedef_name"),
            is_bit_field=declaration.get("is_bit_field", False),
            bit_width=declaration.get("bit_width"),
            line=declaration.get("line"),
            column=declaration.get("column"),
            raw=declaration.get("raw"),
            signedness=declaration.get("signedness"),
            alias_of=declaration.get("alias_of"),
        )

    @classmethod
    def from_ast_node(cls, node: Any, node_name: Optional[str] = None) -> Optional["Declaration"]:
        node_name = node_name or getattr(node, "kind", None) or getattr(node, "type", None) or type(node).__name__
        if node_name == "Typedef":
            type_name = _type_name(getattr(node, "type", None))
            return cls(
                kind="typedef",
                name=getattr(node, "name", None),
                type_name=type_name,
                storage_specifiers=tuple(_collect_values(getattr(node, "storage", []))),
                qualifiers=tuple(_collect_values(getattr(node, "quals", []))),
                line=_coord_value(node, "line"),
                column=_coord_value(node, "column"),
                raw={"node_name": node_name},
                signedness=infer_signedness(type_name),
                alias_of=type_name,
            )

        if node_name in {"VarDecl", "FieldDecl", "Decl"}:
            declaration_kind = "field" if node_name == "FieldDecl" else "variable"
            type_name = _type_name(getattr(node, "type", None))
            bit_width = getattr(node, "bitsize", None)
            bit_width_value = getattr(bit_width, "value", None) if bit_width is not None else None
            return cls(
                kind=declaration_kind,
                name=getattr(node, "name", None),
                type_name=type_name,
                storage_specifiers=tuple(_collect_values(getattr(node, "storage", []))),
                qualifiers=tuple(_collect_values(getattr(node, "quals", []))),
                is_bit_field=bit_width is not None,
                bit_width=bit_width_value,
                line=_coord_value(node, "line"),
                column=_coord_value(node, "column"),
                raw={"node_name": node_name},
                signedness=infer_signedness(type_name),
            )

        if node_name == "FunctionDecl":
            return cls(
                kind="function",
                name=getattr(node, "name", None),
                type_name=_type_name(getattr(node, "type", None)),
                storage_specifiers=tuple(_collect_values(getattr(node, "storage", []))),
                qualifiers=tuple(_collect_values(getattr(node, "quals", []))),
                line=_coord_value(node, "line"),
                column=_coord_value(node, "column"),
                raw={"node_name": node_name},
            )

        if node_name == "ParmDecl":
            type_name = _type_name(getattr(node, "type", None))
            return cls(
                kind="parameter",
                name=getattr(node, "name", None),
                type_name=type_name,
                storage_specifiers=tuple(_collect_values(getattr(node, "storage", []))),
                qualifiers=tuple(_collect_values(getattr(node, "quals", []))),
                line=_coord_value(node, "line"),
                column=_coord_value(node, "column"),
                raw={"node_name": node_name},
                signedness=infer_signedness(type_name),
            )

        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "type_name": self.type_name,
            "storage_specifiers": list(self.storage_specifiers),
            "qualifiers": list(self.qualifiers),
            "typedef_name": self.typedef_name,
            "is_bit_field": self.is_bit_field,
            "bit_width": self.bit_width,
            "line": self.line,
            "column": self.column,
            "signedness": self.signedness,
            "alias_of": self.alias_of,
        }


def extract_declarations_from_source(source_code: str) -> List[Declaration]:
    if not source_code:
        return []

    declarations: List[Declaration] = []
    typedef_names = set()
    consumed_typedef_spans = set()

    for match in _TYPEDEF_PATTERN.finditer(source_code):
        declaration = _parse_typedef(match.group("rest"), source_code, match.start("rest"))
        if declaration is None:
            continue
        declarations.append(declaration)
        if declaration.name:
            typedef_names.add(declaration.name)
        consumed_typedef_spans.add((match.start(), match.end()))

    declarations.extend(_extract_bit_fields(source_code))
    declarations.extend(_extract_functions(source_code))

    for start, end, statement in _iter_semicolon_statements(source_code):
        if _span_is_consumed(start, end, consumed_typedef_spans):
            continue
        declarations.extend(_parse_object_declaration(statement, source_code, start, typedef_names))

    return declarations


def declaration_source(declaration: Declaration) -> str:
    raw = getattr(declaration, "raw", None)
    if isinstance(raw, dict):
        return raw.get("source") or raw.get("line") or raw.get("statement") or str(raw)
    if raw:
        return str(raw)
    return str(declaration)


def declaration_scope_depth(declaration: Declaration) -> int:
    raw = getattr(declaration, "raw", None)
    if isinstance(raw, dict):
        return int(raw.get("scope_depth") or 0)
    return 0


def declaration_type_signature(declaration: Declaration) -> str:
    if declaration is None:
        return ""
    qualifiers = tuple(getattr(declaration, "qualifiers", ()) or ())
    type_name = (getattr(declaration, "type_name", None) or "").strip()
    signedness = getattr(declaration, "signedness", None) or ""
    parts = [*qualifiers, type_name]
    if signedness and signedness not in type_name:
        parts.append(signedness)
    return " ".join(part for part in parts if part).strip()


def infer_signedness(type_name: Optional[str]) -> Optional[str]:
    if not type_name:
        return None
    lowered = type_name.lower().strip()
    if lowered.startswith("unsigned"):
        return "unsigned"
    if lowered.startswith("signed"):
        return "signed"
    if lowered == "char":
        return "plain"
    if lowered.endswith("char") and "unsigned" in lowered:
        return "unsigned"
    if lowered.endswith("char") and "signed" in lowered:
        return "signed"
    return None


def split_declarators(declarator_text: str) -> List[str]:
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


def _parse_typedef(rest: str, source_code: str, rest_offset: int) -> Optional[Declaration]:
    cleaned = _strip_comments(rest).strip()
    alias_match = re.search(r"(?P<alias>[A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?\s*$", cleaned)
    if alias_match is None:
        return None
    alias = alias_match.group("alias")
    type_name = cleaned[: alias_match.start()].strip()
    type_name = re.sub(r"\s+", " ", type_name).strip()
    if not type_name:
        return None
    alias_offset = source_code.find(alias, rest_offset)
    raw_source = f"typedef {cleaned};"
    return Declaration(
        kind="typedef",
        name=alias,
        type_name=type_name,
        storage_specifiers=("typedef",),
        line=_line_number(source_code, alias_offset),
        column=_column_number(source_code, alias_offset),
        raw={"source": raw_source, "statement": raw_source, "scope_depth": _scope_depth(source_code, rest_offset)},
        signedness=infer_signedness(type_name),
        alias_of=type_name,
    )


def _extract_bit_fields(source_code: str) -> List[Declaration]:
    declarations = []
    for struct_match in _BIT_FIELD_PATTERN.finditer(source_code):
        body = struct_match.group("body")
        body_offset = struct_match.start("body")
        for field_match in _BIT_FIELD_DECLARATOR_PATTERN.finditer(body):
            type_name = re.sub(r"\s+", " ", field_match.group("type")).strip()
            name_offset = body_offset + field_match.start("name")
            declarations.append(
                Declaration(
                    kind="field",
                    name=field_match.group("name"),
                    type_name=type_name,
                    is_bit_field=True,
                    bit_width=field_match.group("width"),
                    line=_line_number(source_code, name_offset),
                    column=_column_number(source_code, name_offset),
                    raw={
                        "source": field_match.group(0).strip(),
                        "statement": struct_match.group(0).strip(),
                        "scope_depth": _scope_depth(source_code, struct_match.start()),
                    },
                    signedness=infer_signedness(type_name),
                )
            )
    return declarations


def _extract_functions(source_code: str) -> List[Declaration]:
    declarations = []
    for match in _FUNCTION_PATTERN.finditer(source_code):
        name = match.group("name")
        if name in _CONTROL_KEYWORDS:
            continue
        prefix = _normalize_space(match.group("prefix"))
        storage_specifiers, qualifiers, type_name = _split_specifiers(prefix)
        if not type_name or type_name in _CONTROL_KEYWORDS:
            continue
        declarations.append(
            Declaration(
                kind="function",
                name=name,
                type_name=type_name,
                storage_specifiers=tuple(storage_specifiers),
                qualifiers=tuple(qualifiers),
                line=_line_number(source_code, match.start("name")),
                column=_column_number(source_code, match.start("name")),
                raw={
                    "source": match.group(0).strip(),
                    "statement": match.group(0).strip(),
                    "scope_depth": _scope_depth(source_code, match.start()),
                    "parameters": match.group("parameters"),
                    "tail": match.group("tail"),
                },
                signedness=infer_signedness(type_name),
            )
        )
    return declarations


def _parse_object_declaration(
    statement: str,
    source_code: str,
    start_offset: int,
    typedef_names: set,
) -> List[Declaration]:
    cleaned = _strip_comments(statement).strip()
    if not cleaned or not cleaned.endswith(";"):
        return []
    if cleaned.startswith("#") or cleaned.startswith(("typedef", "return", "case", "break", "continue")):
        return []
    if "{" in cleaned or "}" in cleaned or ":" in cleaned:
        return []
    if "(" in cleaned and ")" in cleaned and "=" not in cleaned:
        return []

    body = cleaned[:-1].strip()
    specifiers, declarator_text = _split_declaration_prefix(body)
    if not specifiers or not declarator_text:
        return []
    first_specifier = specifiers.split()[0] if specifiers else ""
    if first_specifier in _CONTROL_KEYWORDS:
        return []
    if not _looks_like_type_specifier(specifiers, typedef_names):
        return []

    storage_specifiers, qualifiers, type_name = _split_specifiers(specifiers)
    if not type_name:
        return []

    declarations = []
    for declarator in split_declarators(declarator_text):
        declarator_without_initializer = _strip_initializer(declarator)
        name_match = _last_identifier(declarator_without_initializer)
        if name_match is None:
            continue
        name = name_match.group(0)
        name_offset = source_code.find(name, start_offset)
        pointer_suffix = " *" if "*" in declarator_without_initializer[: name_match.start()] else ""
        declarations.append(
            Declaration(
                kind="variable",
                name=name,
                type_name=f"{type_name}{pointer_suffix}",
                storage_specifiers=tuple(storage_specifiers),
                qualifiers=tuple(qualifiers),
                line=_line_number(source_code, name_offset),
                column=_column_number(source_code, name_offset),
                raw={
                    "source": cleaned,
                    "statement": cleaned,
                    "declarator": declarator.strip(),
                    "scope_depth": _scope_depth(source_code, start_offset),
                },
                signedness=infer_signedness(type_name),
            )
        )
    return declarations


def _split_declaration_prefix(body: str) -> Tuple[str, str]:
    words = body.split()
    if len(words) < 2:
        return "", ""

    prefix_words = []
    index = 0
    type_seen = False
    while index < len(words):
        word = words[index]
        clean_word = word.strip("*(),;")
        if clean_word in _STORAGE_SPECIFIERS or clean_word in _QUALIFIERS:
            prefix_words.append(word)
            index += 1
            continue
        if clean_word in _BUILTIN_TYPE_WORDS:
            prefix_words.append(word)
            type_seen = True
            index += 1
            continue
        if clean_word in {"struct", "union", "enum"} and index + 1 < len(words):
            prefix_words.extend(words[index : index + 2])
            type_seen = True
            index += 2
            continue
        if not type_seen and index < len(words) - 1:
            prefix_words.append(word)
            type_seen = True
            index += 1
            continue
        break

    if not prefix_words or index >= len(words):
        return "", ""
    return " ".join(prefix_words), " ".join(words[index:])


def _iter_semicolon_statements(source_code: str):
    for match in re.finditer(r";", source_code):
        start = max(
            source_code.rfind(";", 0, match.start()),
            source_code.rfind("{", 0, match.start()),
            source_code.rfind("}", 0, match.start()),
        ) + 1
        yield start, match.end(), source_code[start : match.end()]


def _span_is_consumed(start: int, end: int, consumed_spans: set) -> bool:
    return any(start >= consumed_start and end <= consumed_end for consumed_start, consumed_end in consumed_spans)


def _looks_like_type_specifier(specifiers: str, typedef_names: set) -> bool:
    words = specifiers.split()
    if not words:
        return False
    if any(word in _TYPE_PREFIX_WORDS for word in words):
        return True
    return words[0] in typedef_names or words[0] not in _CONTROL_KEYWORDS


def _split_specifiers(specifiers: str) -> Tuple[List[str], List[str], str]:
    storage_specifiers = []
    qualifiers = []
    type_words = []
    for word in specifiers.split():
        if word in _STORAGE_SPECIFIERS:
            storage_specifiers.append(word)
        elif word in _QUALIFIERS:
            qualifiers.append(word)
        else:
            type_words.append(word)
    return storage_specifiers, qualifiers, " ".join(type_words).strip()


def _strip_initializer(declarator: str) -> str:
    current = []
    depth = 0
    for char in declarator:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(depth - 1, 0)
        if char == "=" and depth == 0:
            break
        current.append(char)
    return "".join(current).strip()


def _last_identifier(text: str):
    matches = list(_IDENTIFIER_PATTERN.finditer(text))
    if not matches:
        return None
    return matches[-1]


def _collect_values(values):
    if not values:
        return []
    if isinstance(values, (list, tuple)):
        return [str(item) for item in values]
    return [str(values)]


def _type_name(node: Any) -> Optional[str]:
    if node is None:
        return None
    if hasattr(node, "declname") and getattr(node, "declname", None):
        return getattr(node, "declname", None)
    if hasattr(node, "names"):
        names = getattr(node, "names", [])
        if isinstance(names, (list, tuple)):
            return " ".join(str(item) for item in names)
        return str(names)
    if hasattr(node, "name"):
        return str(getattr(node, "name"))
    return type(node).__name__


def _coord_value(node: Any, attr: str):
    coord = getattr(node, "coord", None)
    if coord is None:
        return None
    return getattr(coord, attr, None)


def _strip_comments(text: str) -> str:
    text = _COMMENT_LINE_PATTERN.sub("", text)
    return _BLOCK_COMMENT_PATTERN.sub("", text)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _line_number(source_code: str, offset: int) -> int:
    if offset < 0:
        return 1
    return source_code.count("\n", 0, offset) + 1


def _column_number(source_code: str, offset: int) -> int:
    if offset < 0:
        return 0
    line_start = source_code.rfind("\n", 0, offset)
    return offset - line_start


def _scope_depth(source_code: str, offset: int) -> int:
    if offset < 0:
        return 0
    return max(source_code.count("{", 0, offset) - source_code.count("}", 0, offset), 0)
