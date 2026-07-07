import re
from collections import Counter


class SymbolTableBuilder:
    """
    Builds a lightweight symbol table.

    Responsibilities
    ----------------
    • Collect declarations
    • Store symbol metadata
    • Infer categories
    • Produce dashboard statistics

    This is intentionally lightweight and does not attempt to
    replace a real compiler symbol table.
    """

    def build(self, analysis_context):

        declarations = getattr(
            analysis_context,
            "get_declarations",
            None,
        )

        if callable(declarations):

            symbols = {}

            statistics = Counter()

            for declaration in declarations():

                if not declaration.name:
                    continue

                symbol = {
                    "name": declaration.name,
                    "kind": declaration.kind,
                    "line": declaration.line,
                    "type_name": declaration.type_name,
                    "storage_specifiers": list(
                        declaration.storage_specifiers
                    ),
                    "qualifiers": list(
                        declaration.qualifiers
                    ),
                    "signedness": declaration.signedness,
                    "is_bit_field": declaration.is_bit_field,
                    "bit_width": declaration.bit_width,
                    "is_pointer": "*" in (
                        declaration.type_name or ""
                    ),
                    "initialized": False,
                    "category": self._category(
                        declaration.type_name
                    ),
                    "scope": "global",
                }

                symbols[
                    declaration.name
                ] = symbol

                statistics[
                    symbol["category"]
                ] += 1

            symbols["__statistics__"] = {
                "total_symbols": len(
                    symbols
                ),
                "variables": statistics[
                    "variable"
                ],
                "functions": statistics[
                    "function"
                ],
                "typedefs": statistics[
                    "typedef"
                ],
                "structures": statistics[
                    "struct"
                ],
                "enums": statistics[
                    "enum"
                ],
                "pointers": statistics[
                    "pointer"
                ],
            }

            if len(symbols) > 1:
                return symbols

        return self._fallback(
            analysis_context
        )

    def _fallback(
        self,
        analysis_context,
    ):
        """
        Regex-based fallback when declaration
        extraction is unavailable.
        """

        source = (
            analysis_context.source_code
            or ""
        )

        symbols = {}

        pattern = re.compile(
            r"\b(?:"
            r"int|char|float|double|"
            r"short|long|void|"
            r"unsigned|signed"
            r")\s+"
            r"(?:\*\s*)?"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s*(?=(?:=|;|\())"
        )

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            for match in pattern.finditer(line):

                name = match.group(1)

                symbols[name] = {
                    "name": name,
                    "kind": (
                        "function"
                        if "(" in line
                        else "variable"
                    ),
                    "line": line_number,
                    "type_name": (
                        line.split()[0]
                        if line.split()
                        else ""
                    ),
                    "storage_specifiers": [],
                    "qualifiers": [],
                    "signedness": None,
                    "is_bit_field": False,
                    "bit_width": None,
                    "is_pointer": "*" in line,
                    "initialized": False,
                    "category": (
                        "function"
                        if "(" in line
                        else "variable"
                    ),
                    "scope": "unknown",
                }

        symbols["__statistics__"] = {
            "total_symbols": max(
                len(symbols) - 1,
                0,
            )
        }

        return symbols

    def _category(
        self,
        type_name,
    ):
        """
        Classifies declaration category.
        """

        t = (
            type_name
            or ""
        ).lower()

        if "*" in t:
            return "pointer"

        if t.startswith("struct"):
            return "struct"

        if t.startswith("enum"):
            return "enum"

        if "typedef" in t:
            return "typedef"

        if "function" in t:
            return "function"

        return "variable"
    
    def lookup(
    self,
    symbols,
    name,
):
        """
    Return one symbol by name.
    """

        return symbols.get(name)


    def exists(
    self,
    symbols,
    name,
):
        return name in symbols


    def all_symbols(
    self,
    symbols,
):
        return [
        symbol
        for name, symbol in symbols.items()
        if not name.startswith("__")
    ]