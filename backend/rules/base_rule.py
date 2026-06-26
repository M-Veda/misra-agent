from abc import ABC, abstractmethod


class BaseRule(ABC):

    RULE_ID = ""
    TITLE = ""
    CATEGORY = ""
    SEVERITY = ""
    DESCRIPTION = ""

    @abstractmethod
    def check(self, code: str, file_path: str):
        pass

    @abstractmethod
    def suggest_fix(self, violation):
        pass

    @property
    def id(self):
        return self.RULE_ID

    @property
    def title(self):
        return self.TITLE

    @property
    def category(self):
        return self.CATEGORY

    @property
    def severity(self):
        return self.SEVERITY

    @property
    def description(self):
        return self.DESCRIPTION
    
    def register(self):

        from rules.registry import RULE_REGISTRY

        RULE_REGISTRY.append(self)