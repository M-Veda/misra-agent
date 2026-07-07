"""
Semantic analysis utilities for MISRA function rules.

This module builds reusable semantic information from
parsed functions. Rule implementations should rely on
this analysis instead of directly scanning source code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rules.function_parser import FunctionInfo, iter_functions


# =========================================================
# Function Symbol Table
# =========================================================


@dataclass(slots=True)
class FunctionTable:
    """
    Stores every declaration and definition found
    within a translation unit.
    """

    declarations: dict[str, list[FunctionInfo]]

    definitions: dict[str, list[FunctionInfo]]

    def declared(self, name: str) -> bool:
        return name in self.declarations

    def defined(self, name: str) -> bool:
        return name in self.definitions

    def declaration_count(self, name: str) -> int:
        return len(
            self.declarations.get(name, [])
        )

    def definition_count(self, name: str) -> int:
        return len(
            self.definitions.get(name, [])
        )

    def names(self):
        """
        Returns every discovered function name.
        """

        return sorted(
            set(self.declarations)
            | set(self.definitions)
        )

# =========================================================
# Symbol Collection
# =========================================================


def build_function_table(
    code: str,
) -> FunctionTable:
    """
    Build the function symbol table.
    """

    declarations: dict[str, list[FunctionInfo]] = {}

    definitions: dict[str, list[FunctionInfo]] = {}

    for function in iter_functions(code):

        if function.has_body:

            definitions.setdefault(
                function.name,
                [],
            ).append(function)

        else:

            declarations.setdefault(
                function.name,
                [],
            ).append(function)

    return FunctionTable(
        declarations=declarations,
        definitions=definitions,
    )


# =========================================================
# Signature Utilities
# =========================================================


def normalize_parameter_list(
    parameters: str,
) -> str:
    """
    Normalize parameter spacing.
    """

    return re.sub(
        r"\s+",
        " ",
        parameters.strip(),
    )


def parameter_tokens(
    parameters: str,
) -> list[str]:
    """
    Convert a parameter list into normalized tokens.
    """

    parameters = parameters.strip()

    if not parameters:

        return []

    if parameters == "void":

        return []

    return [
        re.sub(
            r"\s+",
            " ",
            parameter.strip(),
        )
        for parameter in parameters.split(",")
        if parameter.strip()
    ]


def signature_string(
    function: FunctionInfo,
) -> str:
    """
    Canonical textual function signature.
    """

    params = ",".join(
        parameter_tokens(
            function.parameters,
        )
    )

    return (
        f"{function.normalized_return_type} "
        f"{function.name}"
        f"({params})"
    )


def same_signature(
    first: FunctionInfo,
    second: FunctionInfo,
) -> bool:

    return (
        signature_string(first)
        == signature_string(second)
    )


def compatible_signature(
    first: FunctionInfo,
    second: FunctionInfo,
) -> bool:
    """
    Current implementation performs textual comparison.

    Future AST versions will perform semantic comparison.
    """

    return same_signature(
        first,
        second,
    )


# =========================================================
# Lookup Helpers
# =========================================================


def lookup_declarations(
    table: FunctionTable,
    name: str,
):

    return table.declarations.get(
        name,
        [],
    )


def lookup_definitions(
    table: FunctionTable,
    name: str,
):

    return table.definitions.get(
        name,
        [],
    )


def first_declaration(
    table: FunctionTable,
    name: str,
):

    declarations = lookup_declarations(
        table,
        name,
    )

    return (
        declarations[0]
        if declarations
        else None
    )


def first_definition(
    table: FunctionTable,
    name: str,
):

    definitions = lookup_definitions(
        table,
        name,
    )

    return (
        definitions[0]
        if definitions
        else None
    )


def all_function_names(
    table: FunctionTable,
):

    return sorted(
        set(table.declarations)
        | set(table.definitions)
    )


# =========================================================
# Function Analysis
# =========================================================


@dataclass(slots=True)
class FunctionAnalysis:
    """
    Reusable semantic information shared by
    all MISRA function rules.
    """

    table: FunctionTable

    duplicate_definitions: dict[
        str,
        list[FunctionInfo],
    ]

    prototype_mismatches: list[
        tuple[
            FunctionInfo,
            FunctionInfo,
        ]
    ]


def analyze_functions(
    code: str,
) -> FunctionAnalysis:
    """
    Perform semantic analysis over one translation unit.
    """

    table = build_function_table(code)

    duplicate_definitions = {}

    prototype_mismatches = []

    for name in all_function_names(table):

        definitions = lookup_definitions(
            table,
            name,
        )

        declarations = lookup_declarations(
            table,
            name,
        )

        if len(definitions) > 1:

            duplicate_definitions[name] = definitions

        if declarations and definitions:

            declaration = declarations[0]

            definition = definitions[0]

            if not compatible_signature(
                declaration,
                definition,
            ):

                prototype_mismatches.append(
                    (
                        declaration,
                        definition,
                    )
                )

    return FunctionAnalysis(
        table=table,
        duplicate_definitions=duplicate_definitions,
        prototype_mismatches=prototype_mismatches,
    )
