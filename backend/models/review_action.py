from enum import Enum


class ReviewAction(str, Enum):
    """
    Review actions available during the
    interactive MISRA review workflow.
    """

    ACCEPT = "accept"

    REJECT = "reject"

    EDIT = "edit"

    SKIP = "skip"

    @classmethod
    def values(cls):
        """
        Returns all supported action values.
        """

        return [action.value for action in cls]

    @classmethod
    def from_string(cls, value):
        """
        Safely converts a string into a ReviewAction.
        """

        if isinstance(value, cls):
            return value

        value = str(value).strip().lower()

        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported review action: '{value}'. "
                f"Expected one of: {', '.join(cls.values())}"
            ) from exc

    @property
    def requires_patch(self):
        """
        ACCEPT and EDIT create patches.
        """

        return self in (
            ReviewAction.ACCEPT,
            ReviewAction.EDIT,
        )

    @property
    def is_terminal(self):
        """
        Every decision completes review
        of one violation.
        """

        return True

    def __str__(self):
        return self.value