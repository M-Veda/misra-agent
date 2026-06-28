import re
from abc import ABC, abstractmethod


class PatchStrategy(ABC):
    name = "base"

    @abstractmethod
    def apply(self, code, patch):
        raise NotImplementedError


class TextPatchStrategy(PatchStrategy):
    name = "text_patch"

    def apply(self, code, patch):
        original = patch.original_code
        replacement = patch.replacement_code
        if not original:
            raise ValueError("Patch has empty original code context.")
        if original == replacement:
            return code
        if code.count(original) == 0:
            raise ValueError("Text patch context was not found in the source code.")
        if code.count(original) > 1:
            raise ValueError("Text patch context is ambiguous and matched multiple locations.")
        return code.replace(original, replacement, 1)


class RegexPatchStrategy(PatchStrategy):
    name = "regex_patch"

    def apply(self, code, patch):
        pattern = patch.metadata.get("regex_pattern")
        replacement = patch.metadata.get("regex_replacement", patch.replacement_code)
        if not pattern:
            raise ValueError("Regex patch requires regex_pattern metadata.")
        try:
            return re.sub(pattern, replacement, code, count=1)
        except re.error as exc:
            raise ValueError(f"Invalid regex patch pattern: {exc}") from exc


class ASTPatchStrategy(PatchStrategy):
    name = "ast_patch"

    def apply(self, code, patch):
        if patch.metadata.get("ast_replacement"):
            return patch.metadata["ast_replacement"]
        if patch.replacement_code:
            return patch.replacement_code
        raise ValueError("AST patch requires explicit ast_replacement metadata.")


class AIPatchStrategy(PatchStrategy):
    name = "ai_patch"

    def apply(self, code, patch):
        if patch.replacement_code:
            return patch.replacement_code
        raise ValueError("AI patch requires replacement_code.")


class ManualPatchStrategy(PatchStrategy):
    name = "manual_patch"

    def apply(self, code, patch):
        if patch.replacement_code:
            return patch.replacement_code
        raise ValueError("Manual patch requires replacement_code.")


class PatchStrategyRegistry:
    def __init__(self):
        self._strategies = {
            TextPatchStrategy.name: TextPatchStrategy(),
            RegexPatchStrategy.name: RegexPatchStrategy(),
            ASTPatchStrategy.name: ASTPatchStrategy(),
            AIPatchStrategy.name: AIPatchStrategy(),
            ManualPatchStrategy.name: ManualPatchStrategy(),
        }

    def get(self, strategy_name):
        return self._strategies.get(strategy_name, TextPatchStrategy())
