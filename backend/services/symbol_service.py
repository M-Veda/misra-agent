from analyzer.symbol_table import SymbolTableBuilder


class SymbolService:

    def __init__(self):

        self.builder = SymbolTableBuilder()

    def build(self, ast):

        return self.builder.build(ast)