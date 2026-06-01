import json

def report_tool(report_data):

    with open("../reports/report.json", "w") as file:
        json.dump(report_data, file, indent=4)

    return {
        "tool": "report_generator",
        "status": "Report Generated"
    }