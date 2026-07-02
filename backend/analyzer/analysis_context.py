from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from analyzer.declaration_model import Declaration


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

    def get_declarations(self, kind: Optional[str] = None):
        if kind is None:
            return list(self.declarations)
        return [decl for decl in self.declarations if decl.kind == kind]
