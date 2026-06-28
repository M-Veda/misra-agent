from abc import ABC, abstractmethod


class PatchStrategy(ABC):
    name = "base"

    @abstractmethod
    def apply(self, code, patch):
        raise NotImplementedError


class PatchExecutionResult(dict):
    pass
