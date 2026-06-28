from analyzer.clang_parser import ClangParser


class ClangService:
    def __init__(self):
        self.parser = ClangParser()

    def parse(self, file_path):
        return self.parser.parse(file_path)