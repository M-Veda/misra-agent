from threading import RLock
from copy import deepcopy

from utils.logger import logger


class SessionService:
    """
    In-memory session store for interactive review sessions.
    """

    _sessions = {}
    _lock = RLock()

    def save(self, session_id, session):
        with self._lock:
            self._sessions[session_id] = session

        logger.info("Session %s saved.", session_id)

    def get(self, session_id):
        with self._lock:
            return self._sessions.get(session_id)

    def require(self, session_id):
        session = self.get(session_id)

        if session is None:
            raise KeyError(
                f"Unknown review session: {session_id}"
            )

        return session

    def exists(self, session_id):
        with self._lock:
            return session_id in self._sessions

    def delete(self, session_id):
        with self._lock:

            if session_id in self._sessions:
                del self._sessions[session_id]

                logger.info(
                    "Deleted session %s",
                    session_id,
                )

                return True

        return False

    def update(self, session_id, session):
        self.save(session_id, session)

    def clear(self):
        """
        Remove every active session.
        """

        with self._lock:
            self._sessions.clear()

        logger.info("All review sessions cleared.")

    def count(self):
        """
        Returns number of active sessions.
        """

        with self._lock:
            return len(self._sessions)

    def ids(self):
        """
        Returns all active session ids.
        """

        with self._lock:
            return list(self._sessions.keys())

    def all(self):
        """
        Returns all active sessions.
        """

        with self._lock:
            return list(self._sessions.values())

    def snapshot(self):
        """
        Returns a deep copy of every session.
        Useful for debugging and testing.
        """

        with self._lock:
            return deepcopy(self._sessions)