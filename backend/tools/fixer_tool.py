from fixer import fix_common_issues

def fixer_tool(code):

    fixed_code = fix_common_issues(code)

    return {
        "tool": "fixer",
        "fixed_code": fixed_code
    }