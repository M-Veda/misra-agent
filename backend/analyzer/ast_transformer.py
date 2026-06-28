class ASTTransformer:
    def transform(self, analysis_context, patch):
        if patch.metadata.get("ast_replacement"):
            return patch.metadata["ast_replacement"]
        return patch.replacement_code
