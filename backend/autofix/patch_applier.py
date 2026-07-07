from autofix.patch import Patch


class PatchApplier:

    @staticmethod
    def apply(source, patches):

        patches = sorted(
            patches,
            key=lambda p: p.start,
            reverse=True,
        )

        result = source

        for patch in patches:

            result = (
                result[:patch.start]
                + patch.replacement
                + result[patch.end:]
            )

        return result