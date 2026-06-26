from threading import RLock


class SessionService:
    _sessions = {}
    _lock = RLock()

    def save(self, session_id, session):
        with self._lock:
            self._sessions[session_id] = session

    def get(self, session_id):
        with self._lock:
            return self._sessions.get(session_id)

    def require(self, session_id):
        session = self.get(session_id)
        if session is None:
            raise KeyError(f"Unknown review session: {session_id}")
        return session

    def exists(self, session_id):
        with self._lock:
            return session_id in self._sessions

    def delete(self, session_id):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def update(self, session_id, session):
        self.save(session_id, session)
