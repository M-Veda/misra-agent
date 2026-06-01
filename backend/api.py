from fastapi import FastAPI, UploadFile, File
import shutil

from tools.analyzer_tool import analyzer_tool
from tools.fixer_tool import fixer_tool
from tools.validator_tool import validator_tool
from tools.report_tool import report_tool

app = FastAPI()

INPUT_FILE = "../input/uploaded.c"
OUTPUT_FILE = "../fixed_code/fixed_uploaded.c"

@app.get("/")
def home():

    return {
        "message": "MISRA AI Agent Running"
    }

@app.post("/analyze")
async def analyze_code(file: UploadFile = File(...)):

    # Save uploaded file
    with open(INPUT_FILE, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run analyzer
    analysis_result = analyzer_tool(INPUT_FILE)

    # Read source code
    with open(INPUT_FILE, "r") as f:
        source_code = f.read()

    # Fix code
    fix_result = fixer_tool(source_code)

    fixed_code = fix_result["fixed_code"]

    # Save fixed code
    with open(OUTPUT_FILE, "w") as f:
        f.write(fixed_code)

    # Validate
    validation_result = validator_tool(OUTPUT_FILE)

    # Calculate compliance score
    violations = analysis_result["report"].splitlines()

    initial_violations = len(violations)

    if validation_result["is_valid"]:
        remaining_violations = 0
    else:
        remaining_violations = len(
            validation_result["report"].splitlines()
        )

    fixed_violations = initial_violations - remaining_violations

    score = int(
        (fixed_violations / initial_violations) * 100
    ) if initial_violations > 0 else 100

    # Generate report
    final_report = {
        "analysis": analysis_result["report"],
        "validation": validation_result["report"],
        "is_valid": validation_result["is_valid"],
        "compliance_score": score
    }

    report_tool(final_report)

    return {
        "analysis_report": analysis_result["report"],
        "fixed_code": fixed_code,
        "validation_result": validation_result,
        "compliance_score": score,
        "original_code": source_code
    }