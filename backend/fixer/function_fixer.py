import re


def _add_void_to_empty_functions(code):
    """
    Converts empty parameter lists to (void).

    Example:
        int foo()
    becomes:
        int foo(void)
    """

    pattern = re.compile(
        r"\b([A-Za-z_][A-Za-z0-9_\s\*]+?)\s+([A-Za-z_][A-Za-z0-9_]*)\(\s*\)"
    )

    return pattern.sub(
        lambda m: f"{m.group(1)} {m.group(2)}(void)",
        code,
    )


def _remove_spaces_before_parentheses(code):
    """
    Converts

        main ()

    to

        main()
    """

    return re.sub(
        r"([A-Za-z_][A-Za-z0-9_]*)\s+\(",
        r"\1(",
        code,
    )


def _normalize_function_braces(code):
    """
    Ensures opening brace starts on next line.

    Example:

        int foo(void){
    becomes

        int foo(void)
        {
    """

    pattern = re.compile(
        r"(\)\s*)\{"
    )

    return pattern.sub(
        ")\n{",
        code,
    )


def _remove_extra_spaces(code):
    lines = []

    for line in code.splitlines():
        lines.append(line.rstrip())

    return "\n".join(lines)


def fix_functions(code):
    """
    Function-level automatic fixes.

    Implemented:
        ✓ Empty parameter lists
        ✓ Function spacing
        ✓ Brace normalization
        ✓ Trailing whitespace cleanup
    """

    code = _add_void_to_empty_functions(code)

    code = _remove_spaces_before_parentheses(code)

    code = _normalize_function_braces(code)

    code = _remove_extra_spaces(code)

    return code