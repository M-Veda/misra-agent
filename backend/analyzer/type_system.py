"""
C type system for semantic analysis.

Provides canonical parsing of C declarations for
MISRA C:2012 analysis.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class CType:
    """
    Canonical representation of one C type.
    """

    original: str

    base_type: str

    pointer_depth: int = 0

    array: bool = False

    array_size: str | None = None

    qualifiers: tuple[str, ...] = ()

    storage: tuple[str, ...] = ()

    signed: bool | None = None

    floating: bool = False

    enum: bool = False

    struct: bool = False

    union: bool = False

    function_pointer: bool = False

    typedef: bool = False

    metadata: dict = field(default_factory=dict)

    @property
    def is_pointer(self):
        return self.pointer_depth > 0

    @property
    def is_scalar(self):
        return (
            not self.array
            and not self.struct
            and not self.union
        )

    @property
    def is_object_pointer(self):
        return (
            self.pointer_depth > 0
            and not self.function_pointer
        )
    

def parse_type(type_name):
    """
    Parse a C declaration into CType.
    """

    if not type_name:

        return CType(
            original="",
            base_type="unknown",
        )

    text = " ".join(
        type_name.split()
    )

    qualifiers = []

    storage = []

    pointer_depth = text.count("*")

    array = "[" in text

    array_size = None

    if array:

        left = text.find("[")

        right = text.find("]")

        if (
            left != -1
            and right != -1
            and right > left + 1
        ):
            array_size = text[
                left + 1:right
            ].strip()

    for qualifier in (
        "const",
        "volatile",
        "restrict",
    ):

        if qualifier in text:

            qualifiers.append(
                qualifier
            )

            text = text.replace(
                qualifier,
                "",
            )

    for specifier in (
        "static",
        "extern",
        "register",
        "auto",
    ):

        if specifier in text:

            storage.append(
                specifier
            )

            text = text.replace(
                specifier,
                "",
            )

    text = (
        text.replace("*", "")
        .strip()
    )

    floating = (
        "float" in text
        or "double" in text
    )

    signed = None

    if "unsigned" in text:

        signed = False

    elif (
        "signed" in text
        or "int" in text
        or "short" in text
        or "long" in text
    ):

        signed = True

    return CType(
        original=type_name,
        base_type=text,
        pointer_depth=pointer_depth,
        array=array,
        array_size=array_size,
        qualifiers=tuple(
            qualifiers
        ),
        storage=tuple(
            storage
        ),
        signed=signed,
        floating=floating,
        enum="enum" in text,
        struct="struct" in text,
        union="union" in text,
        function_pointer="(*)" in type_name,
    )


def compatible(
    left,
    right,
):
    """
    Compare two parsed C types.
    """

    if (
        left.pointer_depth
        != right.pointer_depth
    ):
        return False

    if (
        left.base_type
        != right.base_type
    ):
        return False

    if (
        left.qualifiers
        != right.qualifiers
    ):
        return False

    return True

def same_pointer_type(
    left,
    right,
):
    """
    Compare two parsed pointer types.
    """

    if not (
        left.is_pointer
        and right.is_pointer
    ):
        return False

    return (
        left.pointer_depth
        == right.pointer_depth
        and left.base_type
        == right.base_type
        and left.qualifiers
        == right.qualifiers
    )

def assignment_compatible(
    destination,
    source,
):
    """
    Determine whether one CType can be
    assigned to another.

    This helper will become the backbone of
    MISRA Chapters 10, 11, 12 and 18.
    """

    #
    # Exact match.
    #
    if compatible(
        destination,
        source,
    ):
        return True

    #
    # Pointer compatibility.
    #
    if same_pointer_type(
        destination,
        source,
    ):
        return True

    return False