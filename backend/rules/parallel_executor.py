from concurrent.futures import ThreadPoolExecutor, as_completed


class ParallelExecutor:

    def __init__(self, workers=None):
        self.workers = workers

    def execute(self, jobs):

        results = []

        with ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:

            futures = [
                executor.submit(job)
                for job in jobs
            ]

            for future in as_completed(futures):
                results.append(
                    future.result()
                )

        return results