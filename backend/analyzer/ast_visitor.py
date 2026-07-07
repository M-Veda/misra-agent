from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from analyzer.declaration_model import (
    Declaration,
    extract_declarations_from_source,
)


@dataclass(slots=True)
class FunctionInfo:
    """
    Represents one discovered function.

    This object is intended to become the common semantic model used
    throughout the analyzer. Rule modules should consume this object
    instead of reparsing source code.
    """

    name: str

    return_type: str = ""

    parameters: List[str] = field(default_factory=list)

    storage_specifiers: List[str] = field(default_factory=list)

    qualifiers: List[str] = field(default_factory=list)

    line: Optional[int] = None

    column: Optional[int] = None

    calls: List[str] = field(default_factory=list)

    called_by: List[str] = field(default_factory=list)

    local_variables: List[str] = field(default_factory=list)

    return_statements: List[Dict[str, Any]] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def parameter_count(self) -> int:
        return len(self.parameters)

    @property
    def is_recursive(self) -> bool:
        return self.name in self.calls


@dataclass(slots=True)
class ASTVisitor:
    """
    Generic AST visitor.

    Collects

        • declarations

        • function information

        • function calls

        • identifiers

        • loops

        • conditionals

    The visitor intentionally exposes lightweight semantic information
    so rule modules can avoid reparsing source text.
    """

    ast: Any = None

    declarations: List[Declaration] = field(default_factory=list)

    functions: Dict[str, FunctionInfo] = field(default_factory=dict)

    calls: List[Dict[str, Any]] = field(default_factory=list)

    identifiers: List[str] = field(default_factory=list)

    loops: List[Dict[str, Any]] = field(default_factory=list)

    conditionals: List[Dict[str, Any]] = field(default_factory=list)

    current_function: Optional[str] = None

    def visit(self, node: Any):

        if node is None:
            return

        if isinstance(node, dict):
            self._visit_mapping(node)
            return

        if isinstance(node, str):
            self._extract_declarations_from_text(node)
            return

        if hasattr(node, "__dict__"):
            self._visit_object(node)

    def _visit_mapping(self, node):

        for value in node.values():

            if value is None:
                continue

            if isinstance(value, list):

                for item in value:
                    self.visit(item)

            else:
                self.visit(value)

    def _extract_declarations_from_text(
    self,
    source: str,
):
        """
    Build semantic information directly from C source text.

    This is the normal entry point used by AnalysisContext.
    """

        self.declarations = extract_declarations_from_source(
        source
    )

        for declaration in self.declarations:

            if (
            declaration.kind == "function"
            or declaration.type_name.endswith(")")
        ):
                self._ensure_function(
                declaration
            )

    def _ensure_function(
        self,
        declaration: Declaration,
    ) -> FunctionInfo:
        """
        Return an existing FunctionInfo or create one.
        """

        function = self.functions.get(
            declaration.name,
        )

        if function is None:

            raw = declaration.raw or {}

            parameter_text = (
                raw.get("parameters", "")
                if isinstance(raw, dict)
                else ""
            )

            parameters = [
                parameter.strip()
                for parameter in parameter_text.split(",")
                if parameter.strip()
                and parameter.strip() != "void"
            ]

            function = FunctionInfo(
                name=declaration.name,
                return_type=declaration.type_name or "",
                parameters=parameters,
                storage_specifiers=list(
                    declaration.storage_specifiers
                ),
                qualifiers=list(
                    declaration.qualifiers
                ),
                line=declaration.line,
                column=declaration.column,
            )

            self.functions[
                declaration.name
            ] = function

        return function
    
    def _record_function_call(
        self,
        node,
    ):
        """
        Record one function call.
        """

        function_name = (
            getattr(node, "name", None)
            or getattr(node, "spelling", None)
            or getattr(node, "displayname", None)
        )

        if not function_name:
            return

        call = {
            "name": function_name,
            "line": getattr(node, "line", None),
            "column": getattr(node, "column", None),
            "arguments": len(
                getattr(node, "arguments", [])
                or []
            ),
            "node": node,
        }

        self.calls.append(call)

        if self.current_function:

            function = self.functions.get(
                self.current_function
            )

            if (
                function is not None
                and function_name
                not in function.calls
            ):
                function.calls.append(
                    function_name
                )


    def _record_identifier(
        self,
        node,
    ):
        """
        Record identifiers encountered while traversing.
        """

        name = (
            getattr(node, "name", None)
            or getattr(node, "spelling", None)
        )

        if (
            name
            and name not in self.identifiers
        ):
            self.identifiers.append(name)


    def _record_loop(
        self,
        node,
        kind,
    ):
        self.loops.append(
            {
                "kind": kind,
                "line": getattr(
                    node,
                    "line",
                    None,
                ),
                "column": getattr(
                    node,
                    "column",
                    None,
                ),
                "node": node,
            }
        )


    def _record_conditional(
        self,
        node,
        kind,
    ):
        self.conditionals.append(
            {
                "kind": kind,
                "line": getattr(
                    node,
                    "line",
                    None,
                ),
                "column": getattr(
                    node,
                    "column",
                    None,
                ),
                "node": node,
            }
        )

    def _visit_object(
        self,
        node: Any,
    ):
        """
        Visit one AST object and collect semantic information.
        """

        node_kind = (
            getattr(node, "kind", None)
            or getattr(node, "type", None)
            or type(node).__name__
        )

        #
        # Declarations
        #
        if node_kind in {
            "VarDecl",
            "ParmDecl",
            "FieldDecl",
            "RecordDecl",
            "Typedef",
            "Decl",
            "FunctionDecl",
        }:

            declaration = Declaration.from_ast_node(
                node,
                node_kind,
            )

            if declaration is not None:

                self.declarations.append(
                    declaration
                )

                if node_kind == "FunctionDecl":

                    function = self._ensure_function(
                        declaration,
                    )

                    previous = self.current_function

                    self.current_function = (
                        function.name
                    )

                    for value in getattr(
                        node,
                        "__dict__",
                        {},
                    ).values():

                        if isinstance(value, list):

                            for child in value:
                                self.visit(child)

                        else:
                            self.visit(value)

                    self.current_function = previous

                    return

        #
        # Function calls
        #
        if node_kind == "CallExpr":

            self._record_function_call(
                node,
            )

        #
        # Identifier references
        #
        elif node_kind in {
            "DeclRefExpr",
            "Identifier",
        }:

            self._record_identifier(
                node,
            )

        #
        # Loops
        #
        elif node_kind == "ForStmt":

            self._record_loop(
                node,
                "for",
            )

        elif node_kind == "WhileStmt":

            self._record_loop(
                node,
                "while",
            )

        elif node_kind == "DoStmt":

            self._record_loop(
                node,
                "do",
            )

        #
        # Conditionals
        #
        elif node_kind == "IfStmt":

            self._record_conditional(
                node,
                "if",
            )

        elif node_kind == "SwitchStmt":

            self._record_conditional(
                node,
                "switch",
            )

        #
        # Continue recursion
        #
        for value in getattr(
            node,
            "__dict__",
            {},
        ).values():

            if isinstance(value, list):

                for child in value:
                    self.visit(child)

            else:

                self.visit(value)

    # ---------------------------------------------------------
    # Query Helpers
    # ---------------------------------------------------------

    def find_function(
        self,
        name: str,
    ) -> Optional[FunctionInfo]:
        """
        Return a function by name.
        """

        return self.functions.get(name)


    def find_identifier(
        self,
        name: str,
    ) -> bool:
        """
        Returns True if an identifier exists.
        """

        return name in self.identifiers


    def find_loops(
        self,
        kind: Optional[str] = None,
    ):
        """
        Return collected loops.

        If kind is specified ("for", "while", "do"),
        only loops of that kind are returned.
        """

        if kind is None:
            return self.loops

        return [
            loop
            for loop in self.loops
            if loop["kind"] == kind
        ]


    def find_conditionals(
        self,
        kind: Optional[str] = None,
    ):
        """
        Return collected conditionals.

        If kind is specified ("if", "switch"),
        only matching conditionals are returned.
        """

        if kind is None:
            return self.conditionals

        return [
            conditional
            for conditional in self.conditionals
            if conditional["kind"] == kind
        ]


    # ---------------------------------------------------------
    # Call Graph
    # ---------------------------------------------------------

    def build_call_graph(self):
        """
        Build caller -> callee graph and populate
        reverse call relationships.
        """

        graph = {}

        #
        # Reset reverse edges.
        #
        for function in self.functions.values():

            function.called_by.clear()

        #
        # Build graph.
        #
        for name, function in self.functions.items():

            callees = set(function.calls)

            graph[name] = callees

        #
        # Populate reverse edges.
        #
        for caller, callees in graph.items():

            for callee in callees:

                target = self.functions.get(callee)

                if target is None:
                    continue

                if caller not in target.called_by:

                    target.called_by.append(
                        caller
                    )

        return graph
    
    def callers(
        self,
        function_name,
    ):
        """
        Return every function calling the specified
        function.
        """

        function = self.functions.get(
            function_name
        )

        if function is None:
            return []

        return list(function.called_by)


    def callees(
        self,
        function_name,
    ):
        """
        Return every function called by the specified
        function.
        """

        function = self.functions.get(
            function_name
        )

        if function is None:
            return []

        return list(function.calls)
    
    def leaf_functions(self):
        """
        Return functions that call no other functions.
        """

        return [

            function

            for function in self.functions.values()

            if not function.calls

        ]


    def root_functions(self):
        """
        Return functions that are never called by
        another discovered function.
        """

        return [

            function

            for function in self.functions.values()

            if not function.called_by

        ]


    def recursive_functions(self):
        """
        Return all recursive functions.

        Detects both direct recursion and indirect recursion
        using a depth-first search on the call graph.
        """

        graph = self.build_call_graph()

        recursive = []

        for function in self.functions.values():

            if self._is_recursive(
                function.name,
                graph,
            ):
                recursive.append(function)

        return recursive
    
    def _is_recursive(
        self,
        start,
        graph,
    ):
        """
        Returns True if a path exists from a function
        back to itself.
        """

        visited = set()

        return self._dfs(
            start,
            start,
            graph,
            visited,
        )


    def _dfs(
        self,
        start,
        current,
        graph,
        visited,
    ):

        if current in visited:
            return False

        visited.add(current)

        for neighbour in graph.get(current, ()):

            if neighbour == start:
                return True

            if self._dfs(
                start,
                neighbour,
                graph,
                visited,
            ):
                return True

        return False


    # ---------------------------------------------------------
    # Convenience Properties
    # ---------------------------------------------------------

    @property
    def function_count(self):

        return len(self.functions)


    @property
    def declaration_count(self):

        return len(self.declarations)


    @property
    def call_count(self):

        return len(self.calls)


    @property
    def identifier_count(self):

        return len(self.identifiers)


    @property
    def loop_count(self):

        return len(self.loops)


    @property
    def conditional_count(self):

        return len(self.conditionals)