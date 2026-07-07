from collections import defaultdict


class RuleDependencyGraph:
    """
    Stores rule dependencies.
    """

    def __init__(self):

        self._dependencies = defaultdict(set)

    def add(
        self,
        rule_id,
        *depends_on,
    ):

        self._dependencies[
            rule_id
        ].update(depends_on)

    def dependencies(
        self,
        rule_id,
    ):

        return sorted(
            self._dependencies.get(
                rule_id,
                (),
            )
        )

    def all(self):

        return dict(
            self._dependencies
        )
