from typing import List, Optional


class PatchQueue:
    def __init__(self):
        self._queue: List[str] = []
        self._order: dict = {}

    def enqueue(self, patch) -> None:
        if patch.patch_id in self._order:
            return
        self._queue.append(patch.patch_id)
        self._order[patch.patch_id] = len(self._queue) - 1

    def dequeue(self):
        if not self._queue:
            return None
        patch_id = self._queue.pop(0)
        self._order.pop(patch_id, None)
        return patch_id

    def size(self) -> int:
        return len(self._queue)

    def contains(self, patch_id: str) -> bool:
        return patch_id in self._order

    def ordered_patches(self, patches):
        if not patches:
            return []

        strategy_priority = {
            "text_patch": 0,
            "regex_patch": 1,
            "ast_patch": 2,
            "ai_patch": 3,
            "manual_patch": 4,
            "rule_suggestion": 5,
            "user_edit": 6,
        }
        explicit_positions = {patch.patch_id: index for index, patch in enumerate(patches)}

        def sort_key(patch):
            queue_position = self._order.get(patch.patch_id, explicit_positions.get(patch.patch_id, len(self._queue) + 1))
            return (
                queue_position,
                patch.line_number,
                patch.file_path,
                strategy_priority.get(patch.strategy, 99),
                patch.patch_id,
            )

        return sorted(patches, key=sort_key)

    def snapshot(self):
        return list(self._queue)
