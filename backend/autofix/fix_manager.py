from autofix.fix_engine import FixEngine


class FixManager:

    def __init__(self):

        self.engine = FixEngine()

    def apply_to_source(
        self,
        source,
        violations,
    ):

        fixed_source, applied = self.engine.apply(
            violations,
            source,
        )

        return {
            "source": fixed_source,
            "applied": applied,
            "count": len(applied),
        }