from services.patch_service import PatchService
from utils.logger import logger


class FinalCodeService:
    """
    Generates the final corrected source code by applying all
    approved patches in review order.
    """

    def __init__(self):
        self.patch_service = PatchService()

    def generate(
        self,
        original_code,
        patches,
        session=None,
    ):
        """
        Apply approved patches to the original source code.

        Parameters
        ----------
        original_code : str
            Original uploaded source code.

        patches : list[Patch]
            Patch objects generated during review.

        session : dict | None
            Active review session.
        """

        if not patches:
            logger.info("No patches available. Returning original source.")
            return original_code

        if session is not None:

            for patch in patches:

                if getattr(
                    patch,
                    "status",
                    "queued",
                ) == "queued":

                    self.patch_service.enqueue_patch(
                        session,
                        patch,
                    )

        logger.info(
            "Generating final code using %d patch(es).",
            len(patches),
        )

        final_code = self.patch_service.apply_patches(
            original_code,
            patches,
        )

        if session is not None:

            session["generated"] = True

            session["generated_patch_count"] = len(
                patches,
            )

            session["final_code_ready"] = True

        logger.info("Final code generation completed.")

        return final_code