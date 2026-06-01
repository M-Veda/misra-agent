from analyzer import run_cppcheck

def analyzer_tool(file_path):

    report = run_cppcheck(file_path)

    return {
        "tool": "analyzer",
        "report": report
    }