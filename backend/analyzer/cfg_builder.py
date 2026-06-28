from dataclasses import dataclass, field
from typing import Any, List, Set, Tuple


@dataclass(slots=True)
class CFG:
    nodes: Set[str] = field(default_factory=set)
    edges: List[Tuple[str, str]] = field(default_factory=list)


class CFGBuilder:
    def build(self, analysis_context):
        cfg = CFG()
        if analysis_context.ast is None:
            return cfg
        cfg.nodes.add("entry")
        cfg.nodes.add("exit")
        cfg.edges.append(("entry", "exit"))
        return cfg
