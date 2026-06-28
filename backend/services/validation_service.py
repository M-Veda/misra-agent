from validator.validator_engine import run_validation


class ValidationService:
    def validate(self, file_path, patches=None, session=None):
        result = run_validation(file_path)
        if patches:
            result["patch_summary"] = {
                "applied": sum(1 for patch in patches if getattr(patch, "applied", False)),
                "conflicted": sum(1 for patch in patches if getattr(patch, "status", "") == "conflicted"),
                "queued": sum(1 for patch in patches if getattr(patch, "status", "") == "queued"),
            }
        if session is not None:
            result["patch_history"] = session.get("patch_history", [])
        return result
