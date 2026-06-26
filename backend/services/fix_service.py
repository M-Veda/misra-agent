class FixService:
    """Applies reviewed patches with line-aware context checks."""

    def apply_patches(self, original_code, patches):
        code = original_code
        for patch in sorted(patches, key=lambda item: item.line_number, reverse=True):
            code = self.apply_single_patch(code, patch)
            patch.applied = True
        return code

    def apply_single_patch(self, code, patch):
        if patch.original_code is None:
            raise ValueError(f"Patch {patch.patch_id} has no original code context.")

        original = patch.original_code
        replacement = patch.replacement_code
        if original == "":
            raise ValueError(f"Patch {patch.patch_id} has empty original code context.")

        line_replaced = self._replace_at_line(code, patch.line_number, original, replacement)
        if line_replaced is not None:
            return line_replaced

        occurrence_count = code.count(original)
        if occurrence_count == 1:
            return code.replace(original, replacement, 1)

        if occurrence_count == 0:
            raise ValueError(f"Patch {patch.patch_id} context was not found in the source code.")

        raise ValueError(f"Patch {patch.patch_id} context is ambiguous and matched {occurrence_count} locations.")

    def _replace_at_line(self, code, line_number, original, replacement):
        lines = code.splitlines(keepends=True)
        index = line_number - 1
        if index < 0 or index >= len(lines):
            return None

        original_lines = original.splitlines(keepends=True)
        span = max(len(original_lines), 1)
        candidate = "".join(lines[index:index + span])

        if self._same_source(candidate, original):
            lines[index:index + span] = [self._preserve_line_ending(replacement, candidate)]
            return "".join(lines)

        current_line = lines[index]
        if self._same_source(current_line, original):
            lines[index:index + 1] = [self._preserve_line_ending(replacement, current_line)]
            return "".join(lines)

        return None

    @staticmethod
    def _same_source(left, right):
        return left.replace("\r\n", "\n").rstrip("\n") == right.replace("\r\n", "\n").rstrip("\n")

    @staticmethod
    def _preserve_line_ending(replacement, original_segment):
        if replacement == "":
            return replacement
        if replacement.endswith(("\n", "\r\n")):
            return replacement
        if original_segment.endswith("\r\n"):
            return replacement + "\r\n"
        if original_segment.endswith("\n"):
            return replacement + "\n"
        return replacement
