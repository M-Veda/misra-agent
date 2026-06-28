from analyzer.ast_extractor import ASTExtractor


class ASTService:
    def __init__(self):
        self.extractor = ASTExtractor()

    def extract(self, file_path):
        return self.extractor.extract(file_path)

    def extract_from_source(self, source_code):
        return self.extractor.extract_from_source(source_code)