"""
Expression semantic analysis.

Provides reusable expression classification for
MISRA Chapter 10, 11, 12 and 13.
"""

import re

from analyzer.essential_types import (
    classify_type,
    UNKNOWN,
)

_IDENTIFIER = re.compile(
    r"\b[A-Za-z_][A-Za-z0-9_]*\b"
)

_INTEGER = re.compile(
    r"\b\d+[uUlL]*\b"
)

_FLOAT = re.compile(
    r"\b\d+\.\d+[fFlL]?\b"
)


def expression_type(
    expression,
    declaration_table=None,
):
    """
    Determine the essential type of a simple expression.

    Returns an EssentialType object.
    """

    expression = expression.strip()

    #
    # Integer literal
    #
    if _INTEGER.fullmatch(expression):
        return classify_type("int")

    #
    # Floating literal
    #
    if _FLOAT.fullmatch(expression):
        return classify_type("float")

    #
    # Variable
    #
    if (
        declaration_table
        and expression in declaration_table
    ):
        return classify_type(
            declaration_table[
                expression
            ].type_name
        )

    return UNKNOWN

def same_essential_type(
    left_expression,
    right_expression,
    declaration_table,
):
    """
    Compare two expressions using the Essential
    Type Model.
    """

    left = expression_type(
        left_expression,
        declaration_table,
    )

    right = expression_type(
        right_expression,
        declaration_table,
    )

    return left.category == right.category

def expression_category(
    expression,
    declaration_table=None,
):
    """
    Returns the essential type category.

    Examples
    --------
    signed
    unsigned
    floating
    character
    boolean
    pointer
    unknown
    """

    return expression_type(
        expression,
        declaration_table,
    ).category