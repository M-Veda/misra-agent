import re


class SymbolTableBuilder:
    def build(self, analysis_context):
        source = analysis_context.source_code or ""
        symbols = {}
        pattern = re.compile(r"\b(?:int|char|float|double|short|long|void)\s+(?:\*\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*(?=(?:=|;))")
        for match in pattern.finditer(source):
            name = match.group(1)
            symbols[name] = {"kind": "variable", "line": source[match.start():match.end()]}
        return symbols