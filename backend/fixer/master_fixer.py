from datetime import datetime

from fixer.array_fixer import fix_arrays
from fixer.declaration_fixer import fix_declarations
from fixer.function_fixer import fix_functions
from fixer.expression_fixer import fix_expressions
from fixer.formatting import format_code
from fixer.loop_fixer import fix_loops
from fixer.memory_fixer import fix_memory
from fixer.pointer_fixer import fix_pointers
from utils.logger import logger


class MasterFixer:
    """
    Master orchestrator for all automatic MISRA fixers.

    Every fixer receives the latest version of the source code and
    returns the updated source.

    Individual fixer failures do NOT stop the remaining pipeline.
    """

    def __init__(self):
        self.pipeline = [
            ("Declaration Fixer", fix_declarations),
            ("Function Fixer", fix_functions),
            ("Expression Fixer", fix_expressions),
            ("Pointer Fixer", fix_pointers),
            ("Array Fixer", fix_arrays),
            ("Memory Fixer", fix_memory),
            ("Loop Fixer", fix_loops),
            ("Formatting", format_code),
        ]

    def fix(self, code):
        logger.info("Automatic repair pipeline started.")

        start = datetime.now()

        executed = []

        current_code = code

        for name, fixer in self.pipeline:
            try:
                previous = current_code

                current_code = fixer(current_code)

                executed.append(
                    {
                        "fixer": name,
                        "status": "success",
                        "changed": previous != current_code,
                    }
                )

                logger.info("%s completed.", name)

            except Exception:
                logger.exception("%s failed.", name)

                executed.append(
                    {
                        "fixer": name,
                        "status": "failed",
                        "changed": False,
                    }
                )

        duration = (
            datetime.now() - start
        ).total_seconds()

        logger.info(
            "Repair pipeline finished in %.3f seconds.",
            duration,
        )

        self.last_execution = {
            "duration_seconds": duration,
            "steps": executed,
            "successful_steps": sum(
                1
                for step in executed
                if step["status"] == "success"
            ),
            "failed_steps": sum(
                1
                for step in executed
                if step["status"] == "failed"
            ),
        }

        return current_code

    def execution_summary(self):
        """
        Returns metadata about the most recent repair execution.
        """

        return getattr(
            self,
            "last_execution",
            {},
        )