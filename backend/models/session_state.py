from enum import Enum


class SessionState(str, Enum):
    """
    Represents the lifecycle of a MISRA review session.
    """

    IDLE = "idle"

    ANALYZING = "analyzing"

    REVIEWING = "reviewing"

    BUILDING = "building"

    VALIDATING = "validating"

    FINISHED = "finished"

    @classmethod
    def values(cls):
        """
        Returns all valid session states.
        """

        return [state.value for state in cls]

    @classmethod
    def from_string(cls, value):
        """
        Safely convert a string into a SessionState.
        """

        if isinstance(value, cls):
            return value

        value = str(value).strip().lower()

        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(
                f"Unknown session state '{value}'. "
                f"Expected one of: {', '.join(cls.values())}"
            ) from exc

    @property
    def is_active(self):
        """
        Returns True while the session
        is still being processed.
        """

        return self in (
            SessionState.ANALYZING,
            SessionState.REVIEWING,
            SessionState.BUILDING,
            SessionState.VALIDATING,
        )

    @property
    def is_finished(self):
        """
        Returns True when the workflow
        has completed.
        """

        return self == SessionState.FINISHED

    @property
    def can_accept_decisions(self):
        """
        Decisions are accepted only during
        interactive review.
        """

        return self == SessionState.REVIEWING

    @property
    def can_generate_output(self):
        """
        Output generation starts after
        review completion.
        """

        return self in (
            SessionState.BUILDING,
            SessionState.VALIDATING,
            SessionState.FINISHED,
        )

    def __str__(self):
        return self.value