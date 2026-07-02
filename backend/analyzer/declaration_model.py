from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(slots=True)
class Declaration:
    kind: str
    name: Optional[str] = None
    type_name: Optional[str] = None
    storage_specifiers: Tuple[str, ...] = field(default_factory=tuple)
    qualifiers: Tuple[str, ...] = field(default_factory=tuple)
    typedef_name: Optional[str] = None
    is_bit_field: bool = False
    bit_width: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None
    signedness: Optional[str] = None
    alias_of: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "type_name": self.type_name,
            "storage_specifiers": list(self.storage_specifiers),
            "qualifiers": list(self.qualifiers),
            "typedef_name": self.typedef_name,
            "is_bit_field": self.is_bit_field,
            "bit_width": self.bit_width,
            "line": self.line,
            "column": self.column,
            "signedness": self.signedness,
            "alias_of": self.alias_of,
        }
