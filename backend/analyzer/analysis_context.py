"""
Shared semantic analysis context.

The AnalysisContext performs source analysis once and
provides reusable semantic information to all MISRA rules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from analyzer.ast_visitor import ASTVisitor
from analyzer.initialization_analysis import (
    build_initialization_tracker,
)

@dataclass(slots=True)
class AnalysisContext:
    """
    Shared analysis state for one translation unit.
    """

    code: str

    file_path: str = ""

    #
    # Parsed representations
    #
    ast: Any = None

    visitor: Optional[ASTVisitor] = None

    #
    # Semantic tables
    #
    declarations: list = field(default_factory=list)

    functions: Dict[str, Any] = field(default_factory=dict)

    declaration_table: Dict[str, Any] = field(default_factory=dict)

    parsed_types: Dict[str, Any] = field(default_factory=dict)

    symbol_table: Dict[str, Any] = field(default_factory=dict)

    call_graph: Dict[str, set] = field(default_factory=dict)

    identifiers: list = field(default_factory=list)

    loops: list = field(default_factory=list)

    conditionals: list = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    initialization_tracker: Any = None

    def build(self):
        """
        Build semantic information.
        """

        self.visitor = ASTVisitor()

        #
        # Current implementation starts from source text.
        #
        self.visitor.visit(
            self.code
        )

        self.declarations = (
            self.visitor.declarations
        )

        #
        # Fast declaration lookup.
        #
        self.declaration_table = {
            declaration.name: declaration
            for declaration in self.declarations
            if getattr(declaration, "name", None)
        }

        from analyzer.type_system import (
            parse_type,
        )

        self.parsed_types = {
            declaration.name: parse_type(
                declaration.type_name
            )
            for declaration in self.declarations
            if declaration.name
        }

        self.symbol_table = {
    declaration.name: {
        "declaration": declaration,
        "ctype": self.parsed_types[
            declaration.name
        ],
        "initialized": False,
        "kind": declaration.kind,
        "storage_specifiers": list(
            declaration.storage_specifiers
        ),
        "qualifiers": list(
            declaration.qualifiers
        ),
    }
    for declaration in self.declarations
    if declaration.name
}

        self.functions = (
            self.visitor.functions
        )

        self.call_graph = (
            self.visitor.build_call_graph()
        )

        self.identifiers = (
            self.visitor.identifiers
        )

        self.loops = (
            self.visitor.loops
        )

        self.conditionals = (
            self.visitor.conditionals
        )

        self.initialization_tracker = (
    build_initialization_tracker(
        self.code
    )
)

        return self
    

    
    @property
    def function_count(self):
        return len(self.functions)


    @property
    def declaration_count(self):
        return len(self.declarations)


    @property
    def identifier_count(self):
        return len(self.identifiers)


    @property
    def loop_count(self):
        return len(self.loops)


    @property
    def conditional_count(self):
        return len(self.conditionals)
    
    def lookup(self, name):
        """
        Return symbol information by identifier.
        """

        return self.symbol_table.get(name)


    def lookup_type(self, name):
        """
        Return parsed CType.
        """

        symbol = self.lookup(name)

        if symbol is None:
            return None

        return symbol["ctype"]


    def lookup_declaration(self, name):
        """
        Return declaration object.
        """

        symbol = self.lookup(name)

        if symbol is None:
            return None

        return symbol["declaration"]