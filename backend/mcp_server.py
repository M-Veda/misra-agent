from tools.analyzer_tool import analyzer_tool
from tools.fixer_tool import fixer_tool
from tools.validator_tool import validator_tool
from tools.report_tool import report_tool

INPUT_FILE = "../input/sample.c"
OUTPUT_FILE = "../fixed_code/fixed_sample.c"

def run_agent():

    print("\n======== MCP AGENT STARTED ========\n")

    # STEP 1 — Analyze
    analysis_result = analyzer_tool(INPUT_FILE)

    print("======== ANALYZER TOOL OUTPUT ========\n")
    print(analysis_result["report"])

    # STEP 2 — Read original code
    with open(INPUT_FILE, "r") as file:
        source_code = file.read()

    # STEP 3 — Fix code
    fix_result = fixer_tool(source_code)

    fixed_code = fix_result["fixed_code"]

    print("\n======== FIXER TOOL OUTPUT ========\n")
    print(fixed_code)

    # STEP 4 — Save fixed code
    with open(OUTPUT_FILE, "w") as file:
        file.write(fixed_code)

    print(f"\nFixed code saved to: {OUTPUT_FILE}")

    # STEP 5 — Validate
    validation_result = validator_tool(OUTPUT_FILE)

    print("\n======== VALIDATOR TOOL OUTPUT ========\n")

    if validation_result["is_valid"]:
        print("SUCCESS: Code validated successfully.")
    else:
        print(validation_result["report"])

    # STEP 6 — Generate report
    final_report = {
        "analysis": analysis_result["report"],
        "validation": validation_result["report"],
        "is_valid": validation_result["is_valid"]
    }

    report_result = report_tool(final_report)

    print("\n======== REPORT TOOL OUTPUT ========\n")
    print(report_result["status"])

    print("\n======== MCP AGENT COMPLETED ========\n")

if __name__ == "__main__":
    run_agent()