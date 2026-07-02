import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from analyzer.declaration_model import Declaration


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
        if isinstance(node, str):
            self._extract_declarations_from_text(node)

    def _visit_mapping(self, node: Dict[str, Any]):
        for value in node.values():
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                self.visit(value)
            elif hasattr(value, "__dict__"):
                self.visit(value)
            else:
                self.visit(value)

    def _visit_object(self, node: Any):
        node_name = getattr(node, "kind", None) or getattr(node, "type", None) or type(node).__name__
        if node_name in {"VarDecl", "FunctionDecl", "ParmDecl", "RecordDecl", "FieldDecl", "Typedef", "Decl"}:
            declaration = self._build_declaration(node, node_name)
            if declaration is not None:
                self.declarations.append(declaration.to_dict() if hasattr(declaration, "to_dict") else declaration)
        if node_name == "CallExpr":
            self.calls.append({"name": getattr(node, "name", None)})
        for attr in getattr(node, "__dict__", {}).values():
            if isinstance(attr, (dict, list)):
                self.visit(attr)
            elif hasattr(attr, "__dict__"):
                self.visit(attr)

    def _extract_declarations_from_text(self, text: str):
        if not text or not isinstance(text, str):
            return
        for match in re.finditer(r"\btypedef\b(?P<rest>.*?);", text, re.S):
            rest = match.group("rest").strip()
            if "char" in rest:
                alias = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*$", rest)
                if alias:
                    self.declarations.append(
                        Declaration(
                            kind="typedef",
                            name=alias.group(1),
                            type_name="unsigned char" if "unsigned" in rest else "char",
                            signedness="unsigned" if "unsigned" in rest else "plain",
                            raw={"source": rest},
                        ).to_dict()
                    )
        for match in re.finditer(r"\b(struct|union)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}", text, re.S):
            body = match.group(3)
            for field_match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(\d+)", body):
                self.declarations.append(
                    Declaration(
                        kind="field",
                        name=field_match.group(1),
                        type_name="int",
                        is_bit_field=True,
                        bit_width=field_match.group(2),
                        raw={"source": body},
                    ).to_dict()
                )
        working_text = re.sub(r"\btypedef\b.*?;", "", text, flags=re.S)
        for match in re.finditer(r"\b(?P<qualifiers>(?:const|volatile|restrict)\s+)*(?P<type>(?:signed|unsigned)\s+char|char|int|[A-Za-z_][A-Za-z0-9_]*)\s*(?P<pointer>\*?)(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?=;|=|,)", working_text):
            name = match.group("name")
            type_name = match.group("type")
            qualifiers = []
            if match.group("qualifiers"):
                qualifiers = [item.strip() for item in match.group("qualifiers").split() if item.strip()]
            signedness = "signed" if type_name.startswith("signed") else "unsigned" if type_name.startswith("unsigned") else "plain" if type_name == "char" else None
            self.declarations.append(
                Declaration(
                    kind="variable",
                    name=name,
                    type_name=type_name if not match.group("pointer") else f"{type_name} *",
                    signedness=signedness,
                    qualifiers=tuple(qualifiers),
                    raw={"source": match.group(0)},
                ).to_dict()
            )

    def _build_declaration(self, node: Any, node_name: str) -> Optional[Declaration]:
        if node_name == "Typedef":
            return Declaration(
                kind="typedef",
                name=getattr(node, "name", None),
                type_name=self._type_name(getattr(node, "type", None)),
                storage_specifiers=tuple(self._collect_storage(getattr(node, "storage", []))),
                qualifiers=tuple(self._collect_qualifiers(getattr(node, "quals", []))),
                line=getattr(node, "coord", None).line if getattr(node, "coord", None) is not None else None,
                column=getattr(node, "coord", None).column if getattr(node, "coord", None) is not None else None,
                raw={"node_name": node_name},
            )

        if node_name in {"VarDecl", "FieldDecl", "Decl"}:
            declaration_kind = "field" if node_name == "FieldDecl" else "variable"
            decl_name = getattr(node, "name", None)
            type_node = getattr(node, "type", None)
            bit_width = getattr(node, "bitsize", None)
            is_bit_field = bit_width is not None
            bit_width_value = None
            if bit_width is not None:
                bit_width_value = getattr(bit_width, "value", None)
            return Declaration(
                kind=declaration_kind,
                name=decl_name,
                type_name=self._type_name(type_node),
                storage_specifiers=tuple(self._collect_storage(getattr(node, "storage", []))),
                qualifiers=tuple(self._collect_qualifiers(getattr(node, "quals", []))),
                is_bit_field=is_bit_field,
                bit_width=bit_width_value,
                line=getattr(node, "coord", None).line if getattr(node, "coord", None) is not None else None,
                column=getattr(node, "coord", None).column if getattr(node, "coord", None) is not None else None,
                raw={"node_name": node_name},
            )

        if node_name == "FunctionDecl":
            return Declaration(
                kind="function",
                name=getattr(node, "name", None),
                type_name=self._type_name(getattr(node, "type", None)),
                storage_specifiers=tuple(self._collect_storage(getattr(node, "storage", []))),
                qualifiers=tuple(self._collect_qualifiers(getattr(node, "quals", []))),
                line=getattr(node, "coord", None).line if getattr(node, "coord", None) is not None else None,
                column=getattr(node, "coord", None).column if getattr(node, "coord", None) is not None else None,
                raw={"node_name": node_name},
            )

        if node_name == "ParmDecl":
            return Declaration(
                kind="parameter",
                name=getattr(node, "name", None),
                type_name=self._type_name(getattr(node, "type", None)),
                storage_specifiers=tuple(self._collect_storage(getattr(node, "storage", []))),
                qualifiers=tuple(self._collect_qualifiers(getattr(node, "quals", []))),
                line=getattr(node, "coord", None).line if getattr(node, "coord", None) is not None else None,
                column=getattr(node, "coord", None).column if getattr(node, "coord", None) is not None else None,
                raw={"node_name": node_name},
            )

        return None

    def _collect_storage(self, storage):
        if not storage:
            return []
        if isinstance(storage, (list, tuple)):
            return [str(item) for item in storage]
        return [str(storage)]

    def _collect_qualifiers(self, quals):
        if not quals:
            return []
        if isinstance(quals, (list, tuple)):
            return [str(item) for item in quals]
        return [str(quals)]

    def _type_name(self, node: Any) -> Optional[str]:
        if node is None:
            return None
        if hasattr(node, "declname") and getattr(node, "declname", None):
            return getattr(node, "declname", None)
        if hasattr(node, "names"):
            names = getattr(node, "names", [])
            if isinstance(names, (list, tuple)):
                return " ".join(str(item) for item in names)
            return str(names)
        if hasattr(node, "name"):
            return str(getattr(node, "name"))
        return type(node).__name__

    def find_calls(self, name: str):
        return [call for call in self.calls if call.get("name") == name]

    def find_declarations(self):
        return list(self.declarations)
