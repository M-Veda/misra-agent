from validator import validate_code

def validator_tool(file_path):

    is_valid, report = validate_code(file_path)

    return {
        "tool": "validator",
        "is_valid": is_valid,
        "report": report
    }