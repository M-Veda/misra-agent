# MISRA Rule Regression Tests

Each rule folder contains:

- bad.c        -> must produce at least one violation
- good.c       -> must produce zero violations
- expected.json

A rule test is considered valid only if:

bad.c  -> violations >= 1
good.c -> violations == 0

When adding new rules:

1. Create rule_x_y/
2. Add bad.c
3. Add good.c
4. Add expected.json
5. Run:

python backend/tools/validate_rule_tests.py

6. Run:

python backend/tests/rules/test_runner.py