from dataclasses import dataclass, field
from typing import Any, Dict, List

from analyzer.declaration_model import Declaration, extract_declarations_from_source


@dataclass(slots=True)
class ASTVisitor:
    ast: Any = None
    declarations: List[Declaration] = field(default_factory=list)
    calls: List[Dict[str, Any]] = field(default_factory=list)

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

    def _visit_mapping(self, node: Dict[str, Any]):
        for value in node.values():
            if value is None:
                continue
            if isinstance(value, list):
                for item in value:
                    self.visit(item)
                continue
            self.visit(value)

    def _visit_object(self, node: Any):
        node_name = getattr(node, "kind", None) or getattr(node, "type", None) or type(node).__name__
        if node_name in {"VarDecl", "FunctionDecl", "ParmDecl", "RecordDecl", "FieldDecl", "Typedef", "Decl"}:
            declaration = Declaration.from_ast_node(node, node_name)
            if declaration is not None:
                self.declarations.append(declaration)
        if node_name == "CallExpr":
            self.calls.append({"name": getattr(node, "name", None)})
        for attr in getattr(node, "__dict__", {}).values():
            if isinstance(attr, list):
                for item in attr:
                    self.visit(item)
            else:
                self.visit(attr)

    def _extract_declarations_from_text(self, text: str):
        self.declarations.extend(extract_declarations_from_source(text))

    def find_calls(self, name: str):
        return [call for call in self.calls if call.get("name") == name]

    def find_declarations(self):
        return [declaration.to_dict() if isinstance(declaration, Declaration) else declaration for declaration in self.declarations]
