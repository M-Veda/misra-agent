import re

from autofix.base_fixer import BaseFixer
from autofix.fix_result import FixResult


class Rule81Fixer(BaseFixer):

    RULE_ID = "8.1"

    def apply(
        self,
        violation,
        source,
    ):

        fixed = re.sub(
            r"\(\s*\)",
            "(void)",
            source,
            count=1,
        )

        return FixResult(
            success=True,
            original=source,
            modified=fixed,
            message="Inserted explicit void parameter list.",
        )