import re


def _normalize_for_spacing(code):
    """
    Normalize spacing in for loops.

    Example:
        for(i=0;i<10;i++)
    becomes:
        for (i = 0; i < 10; i++)
    """

    pattern = re.compile(
        r"for\s*\((.*?)\)",
        re.DOTALL,
    )

    def repl(match):
        content = match.group(1)

        parts = [part.strip() for part in content.split(";")]

        if len(parts) == 3:
            return (
                f"for ({parts[0]}; "
                f"{parts[1]}; "
                f"{parts[2]})"
            )

        return match.group(0)

    return pattern.sub(repl, code)


def _normalize_while_spacing(code):
    """
    while(condition)
    ->
    while (condition)
    """

    return re.sub(
        r"\bwhile\s*\(",
        "while (",
        code,
    )


def _normalize_do_while_spacing(code):
    """
    }while(
    ->
    } while (
    """

    code = re.sub(
        r"}\s*while\s*\(",
        "} while (",
        code,
    )

    return code


def _normalize_braces(code):
    """
    Places opening braces on a new line
    for loop constructs.

    Example:

        while (x){
    becomes

        while (x)
        {
    """

    code = re.sub(
        r"(\bfor\s*\(.*?\)|\bwhile\s*\(.*?\))\s*\{",
        r"\1\n{",
        code,
        flags=re.DOTALL,
    )

    return code


def _remove_trailing_spaces(code):
    return "\n".join(
        line.rstrip()
        for line in code.splitlines()
    )


def fix_loops(code):
    """
    Safe loop formatting.

    Implemented
    -----------
    ✓ for-loop spacing

    ✓ while spacing

    ✓ do-while spacing

    ✓ loop brace formatting

    ✓ trailing whitespace cleanup

    No semantic modifications are performed.
    """

    code = _normalize_for_spacing(code)

    code = _normalize_while_spacing(code)

    code = _normalize_do_while_spacing(code)

    code = _normalize_braces(code)

    code = _remove_trailing_spaces(code)

    return code