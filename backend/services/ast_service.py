from analyzer.ast_extractor import ASTExtractor


class ASTService:

    def __init__(self):

        self.extractor = ASTExtractor()

    def extract(self, file_path):

        return self.extractor.extract(file_path)