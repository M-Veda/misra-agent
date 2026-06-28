from analyzer.cfg_builder import CFGBuilder


class FlowAnalyzer:
    def __init__(self):
        self.cfg_builder = CFGBuilder()

    def analyze(self, analysis_context):
        if analysis_context is None:
            return self.cfg_builder.build(type("Ctx", (), {"ast": None})())
        return self.cfg_builder.build(analysis_context)