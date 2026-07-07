from autofix.fix_registry import FixRegistry


class FixEngine:

    def __init__(self):

        self.registry = FixRegistry()

    def apply(self, violations, source):

        current = source

        applied = []

        for violation in violations:

            fixer = self.registry.get(
                violation.rule_id
            )

            if fixer is None:
                continue

            result = fixer.apply(
                violation,
                current,
            )

            if result.success:

                current = result.modified

                violation.applied = True

                applied.append(
                    violation.rule_id
                )

        return current, applied