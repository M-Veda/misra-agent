class TypeAnalyzer:
    def analyze(self, analysis_context):
        source = analysis_context.source_code or ""
        types = []
        for line in source.splitlines():
            if line.strip().startswith("int"):
                types.append({"name": line.strip().split()[1].split("=")[0].split("*")[0].strip(), "type": "int"})
        return types