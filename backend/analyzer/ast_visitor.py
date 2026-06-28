from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ASTVisitor:
    ast: Any = None
    declarations: List[Dict[str, Any]] = field(default_factory=list)
    calls: List[Dict[str, Any]] = field(default_factory=list)

    def visit(self, node: Any):
        if node is None:
            return
        if isinstance(node, dict):
            self._visit_mapping(node)
            return
        if hasattr(node, "__dict__"):
            self._visit_object(node)

    def _visit_mapping(self, node: Dict[str, Any]):
        for value in node.values():
            if isinstance(value, (dict, list)):
                self.visit(value)
            elif hasattr(value, "__dict__"):
                self.visit(value)

    def _visit_object(self, node: Any):
        node_name = getattr(node, "kind", None) or getattr(node, "type", None) or type(node).__name__
        if node_name in {"VarDecl", "FunctionDecl", "ParmDecl", "RecordDecl"}:
            self.declarations.append({"kind": node_name, "name": getattr(node, "name", None)})
        if node_name == "CallExpr":
            self.calls.append({"name": getattr(node, "name", None)})
        for attr in getattr(node, "__dict__", {}).values():
            if isinstance(attr, (dict, list)):
                self.visit(attr)
            elif hasattr(attr, "__dict__"):
                self.visit(attr)

    def find_calls(self, name: str):
        return [call for call in self.calls if call.get("name") == name]

    def find_declarations(self):
        return list(self.declarations)
