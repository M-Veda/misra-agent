def calculate_compliance_score(initial_violations, remaining_violations):
    if initial_violations <= 0:
        return 100

    resolved = max(initial_violations - remaining_violations, 0)
    return int(round((resolved / initial_violations) * 100))
