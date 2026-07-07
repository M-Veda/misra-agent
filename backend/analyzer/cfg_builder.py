from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass(slots=True)
class CFGNode:
    """
    Represents a node in the Control Flow Graph.
    """

    node_id: str
    node_type: str
    label: str = ""
    line: Optional[int] = None


@dataclass(slots=True)
class CFG:
    """
    Lightweight Control Flow Graph.

    This implementation provides a simple graph structure that can be
    extended later with real AST-based control-flow generation.
    """

    nodes: Set[str] = field(default_factory=set)

    edges: List[Tuple[str, str]] = field(default_factory=list)

    node_metadata: Dict[str, CFGNode] = field(default_factory=dict)

    statistics: Dict[str, int] = field(default_factory=dict)


class CFGBuilder:
    """
    Builds a lightweight CFG.

    Current capabilities
    --------------------
    ✓ Entry node

    ✓ Exit node

    ✓ Loop nodes

    ✓ Conditional nodes

    ✓ Metadata

    ✓ Statistics

    This intentionally avoids pretending to build a full compiler-grade
    CFG while still giving the project meaningful structural analysis.
    """

    def build(self, analysis_context):

        cfg = CFG()

        if analysis_context is None:
            return cfg

        if getattr(analysis_context, "ast", None) is None:
            return cfg

        self._add_node(
            cfg,
            "entry",
            "ENTRY",
            "Program Entry",
        )

        visitor = getattr(
            analysis_context,
            "visitor",
            None,
        )

        if visitor is not None:

            for index, loop in enumerate(
                getattr(visitor, "loops", []),
                start=1,
            ):
                self._add_node(
                    cfg,
                    f"loop_{index}",
                    "LOOP",
                    loop.get("type", "Loop"),
                )

            for index, condition in enumerate(
                getattr(visitor, "conditionals", []),
                start=1,
            ):
                self._add_node(
                    cfg,
                    f"cond_{index}",
                    "CONDITIONAL",
                    condition.get("type", "Conditional"),
                )

        self._add_node(
            cfg,
            "exit",
            "EXIT",
            "Program Exit",
        )

        self._connect_nodes(cfg)

        cfg.statistics = {
            "total_nodes": len(cfg.nodes),
            "total_edges": len(cfg.edges),
            "loops": len(
                getattr(visitor, "loops", [])
            )
            if visitor
            else 0,
            "conditionals": len(
                getattr(visitor, "conditionals", [])
            )
            if visitor
            else 0,
        }

        return cfg

    def _add_node(
        self,
        cfg,
        node_id,
        node_type,
        label,
        line=None,
    ):

        cfg.nodes.add(node_id)

        cfg.node_metadata[node_id] = CFGNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            line=line,
        )

    def _connect_nodes(self, cfg):
        """
        Creates a simple sequential graph.

        entry
            ↓
        node1
            ↓
        node2
            ↓
        ...
            ↓
        exit
        """

        ordered = []

        if "entry" in cfg.nodes:
            ordered.append("entry")

        ordered.extend(
            sorted(
                node
                for node in cfg.nodes
                if node not in {"entry", "exit"}
            )
        )

        if "exit" in cfg.nodes:
            ordered.append("exit")

        for index in range(len(ordered) - 1):
            cfg.edges.append(
                (
                    ordered[index],
                    ordered[index + 1],
                )
            )