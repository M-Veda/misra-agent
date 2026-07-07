"""
Query layer for function analysis.

MISRA function rules should interact with function
information through this module instead of directly
accessing parser or analysis internals.
"""

from __future__ import annotations

from rules.function_analysis import (
    FunctionAnalysis,
    all_function_names,
    first_declaration,
    first_definition,
    lookup_declarations,
    lookup_definitions,
)


class FunctionQuery:
    """
    High-level query interface over FunctionAnalysis.

    This class provides a stable API for rule
    implementations. As the parser and semantic
    analysis become more sophisticated (e.g. Clang AST),
    the rule implementations can remain unchanged.
    """

    def __init__(
        self,
        analysis: FunctionAnalysis,
    ):
        self.analysis = analysis
        self.table = analysis.table

    # -----------------------------------------------------
    # Existence
    # -----------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:

        return (
            self.table.declared(name)
            or self.table.defined(name)
        )

    def declared(
        self,
        name: str,
    ) -> bool:

        return self.table.declared(name)

    def defined(
        self,
        name: str,
    ) -> bool:

        return self.table.defined(name)

    # -----------------------------------------------------
    # Lookup
    # -----------------------------------------------------

    def declarations(
        self,
        name: str,
    ):

        return lookup_declarations(
            self.table,
            name,
        )

    def definitions(
        self,
        name: str,
    ):

        return lookup_definitions(
            self.table,
            name,
        )

    def declaration(
        self,
        name: str,
    ):

        return first_declaration(
            self.table,
            name,
        )

    def definition(
        self,
        name: str,
    ):

        return first_definition(
            self.table,
            name,
        )

    # -----------------------------------------------------
    # Counts
    # -----------------------------------------------------

    def declaration_count(
        self,
        name: str,
    ) -> int:

        return self.table.declaration_count(
            name,
        )

    def definition_count(
        self,
        name: str,
    ) -> int:

        return self.table.definition_count(
            name,
        )

    # -----------------------------------------------------
    # Analysis Results
    # -----------------------------------------------------

    @property
    def duplicate_definitions(
        self,
    ):

        return self.analysis.duplicate_definitions

    @property
    def prototype_mismatches(
        self,
    ):

        return self.analysis.prototype_mismatches

    # -----------------------------------------------------
    # Enumeration
    # -----------------------------------------------------

    def names(
        self,
    ):

        return self.table.names()

    def __iter__(
        self,
    ):

        return iter(
            self.names(),
        )

    def __contains__(
        self,
        name: str,
    ):

        return self.exists(
            name,
        )

    def __len__(
        self,
    ):

        return len(
            self.names(),
        )
