from hashlib import sha256

from cache.cache_store import CacheStore


class AnalysisCache:

    def __init__(self):
        self._cache = CacheStore.load()

    def key(self, code):
        return sha256(code.encode("utf-8")).hexdigest()

    def get(self, code):
        return self._cache.get(self.key(code))

    def put(self, code, context):
        self._cache[self.key(code)] = context
        CacheStore.save(self._cache)

    def clear(self):
        self._cache.clear()
        CacheStore.save(self._cache)