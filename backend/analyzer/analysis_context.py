from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
