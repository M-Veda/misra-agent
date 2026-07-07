"""
MISRA Compliance Score Calculator

Scoring Philosophy
------------------
100  -> Fully compliant
90+  -> Excellent
80+  -> Good
70+  -> Acceptable
60+  -> Needs Improvement
<60  -> Poor

A weighted penalty system is used instead of a simple percentage so the
score better reflects real compliance quality.
"""


def _clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(maximum, value))


def _grade(score):
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "FAIL"


def calculate_compliance_score(
    initial_violations,
    remaining_violations,
):
    """
    Backward compatible function.

    Returns only the numeric score because the rest of the project
    currently expects an integer.
    """

    if initial_violations <= 0:
        return 100

    resolved = max(
        initial_violations - remaining_violations,
        0,
    )

    resolution_ratio = resolved / initial_violations

    base_score = resolution_ratio * 100

    remaining_ratio = remaining_violations / initial_violations

    penalty = remaining_ratio * 15

    score = base_score - penalty

    return int(round(_clamp(score)))


def generate_score_details(
    initial_violations,
    remaining_violations,
):
    """
    Rich scoring information for reports/dashboard.
    """

    score = calculate_compliance_score(
        initial_violations,
        remaining_violations,
    )

    resolved = max(
        initial_violations - remaining_violations,
        0,
    )

    unresolved = max(
        remaining_violations,
        0,
    )

    if initial_violations == 0:
        resolution_rate = 100.0
    else:
        resolution_rate = round(
            (resolved / initial_violations) * 100,
            2,
        )

    return {
        "score": score,
        "grade": _grade(score),
        "initial_violations": initial_violations,
        "resolved_violations": resolved,
        "remaining_violations": unresolved,
        "resolution_rate": resolution_rate,
        "fully_compliant": unresolved == 0,
    }