from analyzer.symbol_table import SymbolTableBuilder


class SymbolService:
    def __init__(self):
        self.builder = SymbolTableBuilder()

    def build(self, analysis_context):
        return self.builder.build(analysis_context)