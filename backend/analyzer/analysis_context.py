from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from analyzer.declaration_model import Declaration, extract_declarations_from_source


@dataclass(slots=True)
class AnalysisContext:
    file_path: str
    source_code: str
    available: bool = False
    ast: Any = None
    parse_error: Optional[str] = None
    symbol_table: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    type_information: List[Dict[str, Any]] = field(default_factory=list)
    cfg: Any = None
    visitor: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    declarations: List[Declaration] = field(default_factory=list)
    typedefs: Dict[str, Declaration] = field(default_factory=dict)
    storage_classes: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    qualifiers: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    signedness: Dict[str, Optional[str]] = field(default_factory=dict)

    def __post_init__(self):
        if self.declarations:
            self.declarations = [Declaration.from_mapping(declaration) for declaration in self.declarations]
        self.refresh_indexes()

    def get_declarations(self, kind: Optional[str] = None):
        self.ensure_declarations()
        if kind is None:
            return list(self.declarations)
        return [decl for decl in self.declarations if decl.kind == kind]

    def set_declarations(self, declarations: List[Any]):
        self.declarations = [Declaration.from_mapping(declaration) for declaration in declarations or []]
        self.refresh_indexes()

    def ensure_declarations(self):
        if self.declarations or not self.available or not self.source_code:
            return
        self.declarations = extract_declarations_from_source(self.source_code)
        self.refresh_indexes()

    def refresh_indexes(self):
        self.typedefs = {}
        self.storage_classes = {}
        self.qualifiers = {}
        self.signedness = {}

        for declaration in self.declarations:
            if not declaration.name:
                continue
            if declaration.kind == "typedef":
                self.typedefs[declaration.name] = declaration
            self.storage_classes[declaration.name] = declaration.storage_specifiers
            self.qualifiers[declaration.name] = declaration.qualifiers
            self.signedness[declaration.name] = declaration.signedness
