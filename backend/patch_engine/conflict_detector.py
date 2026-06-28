from typing import List, Optional


class PatchConflictDetector:
    def __init__(self):
        self._strategy_conflicts = {"regex_patch", "ast_patch"}

    def detect_conflicts(self, incoming_patches, applied_patches=None):
        applied_patches = applied_patches or []
        conflicts = []
        for patch in incoming_patches:
            if patch.status in {"applied", "rolled_back", "conflicted"}:
                conflicts.append(f"Conflict: patch {patch.patch_id} is already in a terminal state.")
                continue

            for applied_patch in applied_patches:
                if applied_patch.file_path != patch.file_path:
                    continue

                if self._same_patch(patch, applied_patch):
                    conflicts.append(f"Conflict: duplicate patch target for {patch.patch_id}.")
                    continue

                if self._ranges_overlap(patch, applied_patch):
                    conflicts.append(f"Conflict: overlapping patch range for {patch.patch_id}.")
                    continue

                if self._is_multiline_patch(patch) and self._is_multiline_patch(applied_patch):
                    if self._ranges_overlap(patch, applied_patch):
                        conflicts.append(f"Conflict: multiline patch conflict for {patch.patch_id}.")
                        continue

                if self._is_conflicting_strategy(patch, applied_patch):
                    conflicts.append(f"Conflict: conflicting {patch.strategy} patch for {patch.patch_id}.")
                    continue

        return conflicts

    def _same_patch(self, patch, applied_patch):
        return (
            patch.file_path == applied_patch.file_path
            and patch.line_number == applied_patch.line_number
            and patch.original_code == applied_patch.original_code
            and patch.strategy == applied_patch.strategy
        )

    def _ranges_overlap(self, patch, applied_patch):
        patch_range = self._range_for_patch(patch)
        applied_range = self._range_for_patch(applied_patch)
        return not (patch_range[1] < applied_range[0] or applied_range[1] < patch_range[0])

    def _range_for_patch(self, patch):
        line_number = max(1, patch.line_number)
        line_count = max(1, len(patch.original_code.splitlines()) if patch.original_code else 1)
        return (line_number, line_number + line_count - 1)

    def _is_multiline_patch(self, patch):
        return bool(patch.original_code and "\n" in patch.original_code)

    def _is_conflicting_strategy(self, patch, applied_patch):
        if patch.strategy in self._strategy_conflicts and applied_patch.strategy in self._strategy_conflicts:
            return self._ranges_overlap(patch, applied_patch)
        return False
