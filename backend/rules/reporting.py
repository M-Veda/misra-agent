from collections import defaultdict


class RuleReport:
    """
    Aggregates rule execution results.
    """

    def __init__(self):
        self.chapter_counts = defaultdict(int)
        self.severity_counts = defaultdict(int)
        self.rule_counts = defaultdict(int)

    def add(
    self,
    violation,
):

        self.chapter_counts[
        violation.rule_id.split(".")[0]
    ] += 1

        self.severity_counts[
        violation.severity
    ] += 1

        self.rule_counts[
        violation.rule_id
    ] += 1
        
    def summary(
    self,
):

        return {
        "chapters": dict(
            self.chapter_counts
        ),
        "severity": dict(
            self.severity_counts
        ),
        "rules": dict(
            self.rule_counts
        ),
    }
