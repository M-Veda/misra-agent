from rules.base_rule import BaseRule


class SampleDiscoveryRule(BaseRule):
    RULE_ID = "99.1"
    TITLE = "Sample discovery rule"
    CHAPTER = "99"
    CATEGORY = "Synthetic"
    SEVERITY = "Required"
    DESCRIPTION = "Sample rule used for discovery tests."
    RATIONALE = "Ensures plugin discovery works."
    CAPABILITIES = ("text",)

    def check(self, code, file_path):
        return []
