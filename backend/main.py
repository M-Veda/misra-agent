from analyzer import run_cppcheck
from fixer import fix_common_issues
from validator import validate_code
import os
import requests
import re

INPUT_FILE = "../input/sample.c"
OUTPUT_FILE = "../fixed_code/fixed_sample.c"

# Read source code
with open(INPUT_FILE, "r") as file:
    source_code = file.read()

print("======== ORIGINAL CODE ========\n")
print(source_code)

# Analyze original code
report = run_cppcheck(INPUT_FILE)

print("\n======== STATIC ANALYSIS REPORT ========\n")
print(report)

# Fix issues
fixed_code = fix_common_issues(source_code)

# =====================================
# AUTOMATIC MEMORY DEALLOCATION FIX
# =====================================

if "malloc(" in fixed_code and "free(ptr)" not in fixed_code:

    fixed_code = re.sub(
        r'\breturn\s+0\s*;',
        """
if(ptr != NULL)
{
    free(ptr);
    ptr = NULL;
}

return 0;
""",
        fixed_code
    )

print("\n======== FIXED CODE ========\n")
print(fixed_code)

# Save fixed code
with open(OUTPUT_FILE, "w") as file:
    file.write(fixed_code)

print(f"\nFixed code saved to: {OUTPUT_FILE}")

# Validate fixed code
is_valid, validation_report = validate_code(OUTPUT_FILE)

print("\n======== VALIDATION RESULT ========\n")

if is_valid:
    print("SUCCESS: Code validated successfully.")
else:
    print(validation_report)