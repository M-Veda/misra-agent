import re


class SymbolTableBuilder:
    def build(self, analysis_context):
        declarations = getattr(analysis_context, "get_declarations", None)
        if callable(declarations):
            symbols = {}
            for declaration in declarations():
                if declaration.name:
                    symbols[declaration.name] = {
                        "kind": declaration.kind,
                        "line": declaration.line,
                        "storage_specifiers": list(declaration.storage_specifiers),
                        "qualifiers": list(declaration.qualifiers),
                        "type_name": declaration.type_name,
                        "is_bit_field": declaration.is_bit_field,
                        "bit_width": declaration.bit_width,
                    }
            if symbols:
                return symbols

        source = analysis_context.source_code or ""
        symbols = {}
        pattern = re.compile(r"\b(?:int|char|float|double|short|long|void)\s+(?:\*\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*(?=(?:=|;))")
        for match in pattern.finditer(source):
            name = match.group(1)
            symbols[name] = {"kind": "variable", "line": source[match.start():match.end()]}
        return symbols