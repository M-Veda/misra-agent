from abc import ABC, abstractmethod

from autofix.fix_result import FixResult


class BaseFixer(ABC):

    RULE_ID = ""

    @abstractmethod
    def apply(
        self,
        violation,
        source,
    ) -> FixResult:
        ...