from collections import defaultdict
from time import perf_counter


class RuleProfiler:
    """
    Records rule execution times.
    """

    def __init__(self):

        self.timings = defaultdict(float)

    def start(self):

        return perf_counter()

    def stop(
        self,
        rule_id,
        started,
    ):

        self.timings[
            rule_id
        ] += (
            perf_counter()
            - started
        )

    def summary(self):

        return dict(
            sorted(
                self.timings.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
