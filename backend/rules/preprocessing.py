from rules.base_rule import BaseRule


class RuleGroup(BaseRule):
    """
    Category rule container.
    Individual MISRA rule classes for this category
    will be added here.
    """

    def get_rules(self):
        return []