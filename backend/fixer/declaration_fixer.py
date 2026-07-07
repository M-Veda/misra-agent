import re


def _ensure_void_parameter_lists(code):
    """
    MISRA C Rule 8.2

    Converts

        int main()

    into

        int main(void)

    for empty parameter lists.
    """

    pattern = re.compile(
        r"\b([A-Za-z_][A-Za-z0-9_\s\*]+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*\)"
    )

    return pattern.sub(
        lambda m: f"{m.group(1)} {m.group(2)}(void)",
        code,
    )


def _remove_duplicate_semicolons(code):
    """
    Cleans accidental duplicate semicolons.
    """

    return re.sub(r";{2,}", ";", code)


def _normalize_blank_lines(code):
    """
    Prevent excessive blank lines.
    """

    return re.sub(
        r"\n{3,}",
        "\n\n",
        code,
    )


def _trim_trailing_spaces(code):
    """
    Remove trailing whitespace.
    """

    lines = [
        line.rstrip()
        for line in code.splitlines()
    ]

    return "\n".join(lines)


def fix_declarations(code):
    """
    Declaration-related automatic fixes.

    Current capabilities
    --------------------
    ✓ Empty function parameter lists

    ✓ Duplicate semicolons

    ✓ Excess blank lines

    ✓ Trailing whitespace

    Designed so future declaration fixers can simply be appended here.
    """

    original = code

    code = _ensure_void_parameter_lists(code)

    code = _remove_duplicate_semicolons(code)

    code = _normalize_blank_lines(code)

    code = _trim_trailing_spaces(code)

    return code