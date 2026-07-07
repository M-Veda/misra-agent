import re


def _remove_spaces_inside_parentheses(code):
    """
    (  x + y  )  ->  (x + y)
    """

    code = re.sub(r"\(\s+", "(", code)
    code = re.sub(r"\s+\)", ")", code)

    return code


def _normalize_operator_spacing(code):
    """
    Normalizes spacing around common operators.

    Example:
        a=10+5;

    becomes:
        a = 10 + 5;
    """

    operators = [
        r"\+",
        "-",
        r"\*",
        "/",
        "%",
        "=",
        "==",
        "!=",
        "<=",
        ">=",
        "<",
        ">",
        r"\+=",
        "-=",
        r"\*=",
        "/=",
        "%=",
        "&&",
        r"\|\|",
    ]

    for op in operators:
        code = re.sub(
            rf"\s*({op})\s*",
            r" \1 ",
            code,
        )

    code = re.sub(r"[ \t]{2,}", " ", code)

    return code


def _remove_space_before_semicolon(code):
    """
    value = x ;
    ->
    value = x;
    """

    return re.sub(
        r"\s+;",
        ";",
        code,
    )


def _remove_space_after_open_bracket(code):
    """
    func( value )
    ->
    func(value)
    """

    code = re.sub(r"\(\s+", "(", code)
    code = re.sub(r"\s+\)", ")", code)

    return code


def _trim_lines(code):
    return "\n".join(
        line.rstrip()
        for line in code.splitlines()
    )


def fix_expressions(code):
    """
    Safe expression cleanup.

    Current capabilities
    --------------------
    ✓ Parenthesis spacing
    ✓ Operator spacing
    ✓ Semicolon spacing
    ✓ Trailing whitespace

    NOTE:
    No semantic transformations are performed.
    """

    code = _remove_spaces_inside_parentheses(code)

    code = _normalize_operator_spacing(code)

    code = _remove_space_before_semicolon(code)

    code = _remove_space_after_open_bracket(code)

    code = _trim_lines(code)

    return code