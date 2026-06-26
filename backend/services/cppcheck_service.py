from analyzer.cppcheck_runner import run_cppcheck_analysis


class CppcheckService:

    def analyze(self, file_path):

        return run_cppcheck_analysis(file_path)