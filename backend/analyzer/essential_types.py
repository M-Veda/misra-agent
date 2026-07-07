"""
MISRA C:2012 Essential Type Model.

This module classifies C types into MISRA essential types.
It is shared by Chapter 10, 11, 12, 13 and 18 rules.
"""

from dataclasses import dataclass

from analyzer.type_system import (
    CType,
    parse_type,
)

@dataclass(slots=True)
class EssentialType:
    """
    Represents one MISRA essential type.
    """

    name: str

    category: str

    signed: bool | None = None

    width: int | None = None

    pointee: str | None = None

    qualifiers: tuple[str, ...] = ()


#
# Built-in essential types
#

BOOLEAN = EssentialType(
    "bool",
    "boolean",
)

CHAR = EssentialType(
    "char",
    "character",
)

SIGNED = EssentialType(
    "signed",
    "signed",
)

UNSIGNED = EssentialType(
    "unsigned",
    "unsigned",
)

FLOAT = EssentialType(
    "float",
    "floating",
)

ENUM = EssentialType(
    "enum",
    "enum",
)

POINTER = EssentialType(
    "pointer",
    "pointer",
)

UNKNOWN = EssentialType(
    "unknown",
    "unknown",
)
def classify_type(type_name):
    """
    Convert a C declaration into a MISRA EssentialType.

    Uses the parsed CType representation rather than
    string matching.
    """

    ctype = parse_type(type_name)

    #
    # Pointer
    #
    if ctype.is_pointer:

        return EssentialType(
            name="pointer",
            category="pointer",
            pointee=ctype.base_type,
            qualifiers=ctype.qualifiers,
        )

    #
    # Boolean
    #
    if (
        ctype.base_type == "_Bool"
        or ctype.base_type == "bool"
    ):
        return BOOLEAN

    #
    # Enum
    #
    if ctype.enum:
        return ENUM

    #
    # Floating
    #
    if ctype.floating:
        return FLOAT

    #
    # Character
    #
    if ctype.base_type == "char":

        return CHAR

    #
    # Unsigned
    #
    if ctype.signed is False:

        return UNSIGNED

    #
    # Signed
    #
    if ctype.signed is True:

        return SIGNED

    return UNKNOWN

def compatible(
    left,
    right,
):
    """
    Returns True if two essential types are
    compatible.
    """

    if left.category == right.category:
        return True

    #
    # Floating family
    #
    if (
        left.category == "floating"
        and right.category == "floating"
    ):
        return True

    #
    # Signed family
    #
    if (
        left.category == "signed"
        and right.category == "signed"
    ):
        return True

    #
    # Unsigned family
    #
    if (
        left.category == "unsigned"
        and right.category == "unsigned"
    ):
        return True

    return False


def pointer_compatible(
    left,
    right,
):
    """
    Compare two pointer essential types.
    """

    if (
        left.category != "pointer"
        or
        right.category != "pointer"
    ):
        return False

    return (
        left.pointee == right.pointee
        and
        left.qualifiers == right.qualifiers
    )


def same_object_type(
    left_type,
    right_type,
):
    """
    True when both parsed C types refer
    to the same object type.
    """

    left = parse_type(
        left_type
    )

    right = parse_type(
        right_type
    )

    return (
        left.base_type == right.base_type
        and
        left.pointer_depth
        == right.pointer_depth
    )

def same_qualifiers(
    left_type,
    right_type,
):
    """
    Compare const/volatile/restrict qualifiers.
    """

    left = parse_type(
        left_type
    )

    right = parse_type(
        right_type
    )

    return (
        left.qualifiers
        == right.qualifiers
    )