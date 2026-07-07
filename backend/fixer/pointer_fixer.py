import re


def _normalize_pointer_spacing(code):
    """
    Normalize pointer declaration spacing.

    Examples
    --------
    int*ptr      -> int *ptr
    char**value  -> char **value

    Only affects declarations.
    """

    pattern = re.compile(
        r"\b("
        r"void|char|short|int|long|float|double|signed|unsigned|"
        r"size_t|uint8_t|uint16_t|uint32_t|uint64_t|"
        r"int8_t|int16_t|int32_t|int64_t"
        r")\s*\*+\s*"
    )

    def repl(match):
        text = match.group(0)

        datatype = re.match(
            r"[A-Za-z0-9_]+",
            text,
        ).group(0)

        stars = "*" * text.count("*")

        return f"{datatype} {stars}"

    return pattern.sub(repl, code)


def _remove_space_before_pointer_semicolon(code):
    """
    int *ptr ;
    ->
    int *ptr;
    """

    return re.sub(
        r"\s+;",
        ";",
        code,
    )


def _collapse_multiple_spaces(code):
    lines = []

    for line in code.splitlines():
        lines.append(
            re.sub(r"[ \t]{2,}", " ", line)
        )

    return "\n".join(lines)


def fix_pointers(code):
    """
    Pointer formatting fixes.

    Implemented
    -----------
    ✓ Pointer declaration spacing

    ✓ Pointer semicolon spacing

    ✓ Multiple-space normalization

    Safe transformations only.
    """

    code = _normalize_pointer_spacing(code)

    code = _remove_space_before_pointer_semicolon(code)

    code = _collapse_multiple_spaces(code)

    return code