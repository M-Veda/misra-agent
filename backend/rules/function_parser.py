"""
Function parser utilities for the MISRA C:2012 rule engine.

This module is responsible only for discovering function
declarations and definitions from source code.

Higher-level semantic analysis belongs in:
    - function_analysis.py
    - function_query.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


# ---------------------------------------------------------
# Regular Expressions
# ---------------------------------------------------------

_FUNCTION_PATTERN = re.compile(
    r"""
    ^
    \s*
    (?P<return_type>
        (?:static|extern|inline|const|volatile|
         unsigned|signed|short|long|
         void|char|int|float|double|
         struct\s+\w+|union\s+\w+|enum\s+\w+
        )
        (?:\s+[A-Za-z_]\w*)*
        (?:\s*\*)*
    )
    \s+
    (?P<name>[A-Za-z_]\w*)
    \s*
    \(
        (?P<parameters>[^)]*)
    \)
    \s*
    (?P<body>\{|;)
    """,
    re.MULTILINE | re.VERBOSE,
)

_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
_CALL_PATTERN = re.compile(
    r"\b([A-Za-z_]\w*)\s*\("
)


# ---------------------------------------------------------
# Parameter Model
# ---------------------------------------------------------


@dataclass(slots=True)
class ParameterInfo:
    """
    Represents one function parameter.

    Example
    -------
    const unsigned int *ptr

        qualifiers = ["const"]
        type_name = "unsigned int"
        pointer_level = 1
        name = "ptr"
    """

    name: str

    type_name: str

    qualifiers: list[str]

    storage_classes: list[str]

    pointer_level: int = 0

    is_array: bool = False

    is_variadic: bool = False

    is_function_pointer: bool = False

    array_dimensions: list[str] | None = None

    raw: str = ""

    @property
    def is_pointer(self) -> bool:
        return self.pointer_level > 0

    @property
    def is_const(self) -> bool:
        return "const" in self.qualifiers

    @property
    def is_register(self):

        return (
            "register"
            in self.storage_classes
        )

    @property
    def is_volatile(self) -> bool:
        return "volatile" in self.qualifiers

    @property
    def normalized_type(self) -> str:
        return " ".join(
            self.type_name.split()
        ).strip()

    def __str__(self):

        return self.raw or self.name

    @property
    def array_rank(self):
        """
        Number of array dimensions.
        """

        return len(
            self.array_dimensions or []
        )


    @property
    def is_scalar(self):
        """
        True if parameter is neither pointer,
        array nor function pointer.
        """

        return (
            not self.is_pointer
            and not self.is_array
            and not self.is_function_pointer
        )

# ---------------------------------------------------------
# Function Model
# ---------------------------------------------------------


@dataclass(slots=True)
class FunctionInfo:
    """
    Represents one parsed function declaration or definition.
    """

    name: str
    return_type: str
    parameters: str
    line: int
    has_body: bool
    calls: list[str] | None = None
    parsed_parameters: list[ParameterInfo] | None = None


    @property
    def parameter_count(self) -> int:
        params = self.parameters.strip()

        if not params or params == "void":
            return 0

        return len(
            [
                parameter
                for parameter in params.split(",")
                if parameter.strip()
            ]
        )

    @property
    def is_definition(self) -> bool:
        return self.has_body

    @property
    def is_declaration(self) -> bool:
        return not self.has_body

    @property
    def is_static(self) -> bool:
        return self.return_type.startswith("static")

    @property
    def normalized_return_type(self) -> str:
        return re.sub(
            r"\s+",
            " ",
            self.return_type.strip(),
        )
    
    @property
    def has_parameters(self) -> bool:
        """
        Returns True if the function has one or more parameters.
        """

        return self.parameter_count > 0

    @property
    def is_void(self) -> bool:
        """
        Returns True if the function returns void.
        """

        return (
            self.return_type.strip()
            == "void"
        )
    
    @property
    def parameter_names(self):

        if not self.parsed_parameters:
            return []

        return [
            parameter.name
            for parameter in self.parsed_parameters
        ]


    @property
    def variadic(self):

        if not self.parsed_parameters:
            return False

        return any(
            parameter.is_variadic
            for parameter in self.parsed_parameters
        )


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------


def _line_number(code: str, index: int) -> int:
    """
    Convert a character index into a 1-based source line.
    """

    return code.count("\n", 0, index) + 1


def extract_function_calls(body: str):
    """
    Extract function calls from a function body.

    This is a lightweight implementation.
    Future versions will use the Clang AST.
    """

    keywords = {
        "if",
        "for",
        "while",
        "switch",
        "return",
        "sizeof",
    }

    calls = []

    for match in _CALL_PATTERN.finditer(body):

        name = match.group(1)

        if name in keywords:
            continue

        calls.append(name)

    return calls


# ---------------------------------------------------------
# Public Parser API
# ---------------------------------------------------------


def iter_functions(code: str) -> Iterable[FunctionInfo]:
    """
    Iterate over every function declaration and definition.
    """

    for match in _FUNCTION_PATTERN.finditer(code):

        yield FunctionInfo(
            name=match.group("name"),
            return_type=match.group("return_type").strip(),
            parameters=match.group("parameters").strip(),

            parsed_parameters=parse_parameter_list(
                match.group("parameters")
            ),
            line=_line_number(
                code,
                match.start(),
            ),
            has_body=(
                match.group("body") == "{"
            ),
        )


def find_function(
    code: str,
    name: str,
):
    """
    Return the first matching function.
    """

    for function in iter_functions(code):

        if function.name == name:
            return function

    return None


def function_names(code: str):
    """
    Return all discovered function names.
    """

    return [
        function.name
        for function in iter_functions(code)
    ]


def function_count(code: str) -> int:
    """
    Return the number of discovered functions.
    """

    return sum(
        1
        for _ in iter_functions(code)
    )


def has_function(
    code: str,
    name: str,
) -> bool:
    """
    Returns True if a function exists.
    """

    return find_function(
        code,
        name,
    ) is not None

# ---------------------------------------------------------
# Parameter Parsing Helpers
# ---------------------------------------------------------

_QUALIFIERS = {
    "const",
    "volatile",
    "restrict",
}

_STORAGE_CLASSES = {
    "register",
}

_BUILTIN_TYPES = {
    "void",
    "char",
    "short",
    "int",
    "long",
    "float",
    "double",
    "signed",
    "unsigned",
    "_Bool",
    "bool",
}


def _normalize_spaces(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.strip(),
    )


def _pointer_level(parameter: str) -> int:
    """
    Count pointer indirections.

    Examples
    --------
    int *a      -> 1
    int **a     -> 2
    char ***p   -> 3
    """

    return parameter.count("*")


def _is_array(parameter: str) -> bool:
    return "[" in parameter and "]" in parameter


def _is_variadic(parameter: str) -> bool:
    return parameter.strip() == "..."

_ARRAY_DIMENSION_PATTERN = re.compile(
    r"\[([^\]]*)\]"
)


def _array_dimensions(parameter: str):
    """
    Extract array dimensions.

    int a[10][20]

    ->

    ["10", "20"]
    """

    return _ARRAY_DIMENSION_PATTERN.findall(
        parameter
    )

def _is_function_pointer(parameter: str):
    """
    Detect function-pointer parameters.

    int (*callback)(int)
    """

    return (
        "(*" in parameter
        and ")(" in parameter
    )

def _split_parameter_tokens(parameter: str):
    """
    Split a parameter into lexical tokens.

    Example

    const unsigned int *ptr

    ->
    ["const","unsigned","int","ptr"]
    """

    parameter = (
        parameter
        .replace("*", " ")
        .replace("[", " ")
        .replace("]", " ")
    )

    return [
        token
        for token in parameter.split()
        if token
    ]

def _extract_parameter_name(tokens):
    """
    Extract the parameter identifier.

    Example

    ["const","char","name"]

    ->

    "name"
    """

    if not tokens:
        return ""

    return tokens[-1]

def _extract_qualifiers(tokens):
    return [
        token
        for token in tokens
        if token in _QUALIFIERS
    ]

def _extract_type(tokens):
    """
    Build the canonical parameter type.

    Examples
    --------
        ["const","unsigned","int","ptr"]
            -> "unsigned int"

        ["struct","Node","next"]
            -> "struct Node"

        ["enum","Color","c"]
            -> "enum Color"
    """

    if len(tokens) <= 1:
        return ""

    result = []

    index = 0

    while index < len(tokens) - 1:

        token = tokens[index]

        if token in _QUALIFIERS:
            index += 1
            continue

        if token in _STORAGE_CLASSES:
            index += 1
            continue

        if token in {"struct", "union", "enum"}:

            if index + 1 < len(tokens) - 1:

                result.append(
                    token + " " + tokens[index + 1]
                )

                index += 2

                continue

        result.append(token)

        index += 1

    return " ".join(result).strip()

def _extract_storage_classes(tokens):

    return [
        token
        for token in tokens
        if token in _STORAGE_CLASSES
    ]

def parse_parameter(parameter: str) -> ParameterInfo:
    """
    Parse a single parameter into a ParameterInfo object.

    Examples
    --------
        int a
        const char *name
        unsigned long value
        int buffer[]
        ...
    """

    parameter = _normalize_spaces(parameter)

    if not parameter:
        return ParameterInfo(
    name="",
    type_name="",
    qualifiers=[],
    storage_classes=[],
    raw="",
)

    if _is_variadic(parameter):
        return ParameterInfo(
    name="...",
    type_name="...",
    qualifiers=[],
    storage_classes=[],
    is_variadic=True,
    raw=parameter,
)

    tokens = _split_parameter_tokens(parameter)

    name = _extract_parameter_name(tokens)

    qualifiers = _extract_qualifiers(tokens)

    type_name = _extract_type(tokens)

    return ParameterInfo(
        name=name,
        type_name=type_name,
        qualifiers=qualifiers,
        storage_classes=_extract_storage_classes(tokens),
        pointer_level=_pointer_level(parameter),
        is_array=_is_array(parameter),
        is_variadic=False,
        is_function_pointer=_is_function_pointer(parameter),
        array_dimensions=_array_dimensions(parameter),
        raw=parameter,
    )

def parse_parameter_list(parameter_string: str) -> list[ParameterInfo]:
    """
    Parse an entire parameter list.

    Example
    -------
        int a, const char *b

    becomes

        [
            ParameterInfo(...),
            ParameterInfo(...)
        ]
    """

    parameter_string = parameter_string.strip()

    if not parameter_string:
        return []

    if parameter_string == "void":
        return []

    parameters = []

    current = []

    depth = 0

    for char in parameter_string:

        if char == "(":
            depth += 1

        elif char == ")":
            depth -= 1

        if char == "," and depth == 0:

            text = "".join(current).strip()

            if text:
                parameters.append(
                    parse_parameter(text)
                )

            current = []

            continue

        current.append(char)

    text = "".join(current).strip()

    if text:

        parameters.append(
            parse_parameter(text)
        )

    return parameters
