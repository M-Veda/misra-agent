import pickle
from pathlib import Path


class CacheStore:

    CACHE_FILE = Path(".misra_cache.pkl")

    @classmethod
    def load(cls):
        if cls.CACHE_FILE.exists():
            try:
                with open(cls.CACHE_FILE, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return {}
        return {}

    @classmethod
    def save(cls, cache):
        try:
            with open(cls.CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
        except Exception:
            pass