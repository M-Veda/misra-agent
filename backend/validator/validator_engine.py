from analyzer.cppcheck_runner import run_cppcheck_analysis


def run_validation(file_path):
    report = run_cppcheck_analysis(file_path)
    issues = [line for line in report.splitlines() if line.strip()]

    if not issues:
        return {
            "is_valid": True,
            "report": "No issues found.",
            "issues": [],
        }

    return {
        "is_valid": False,
        "report": report,
        "issues": issues,
    }
