from validator.validator_engine import run_validation


class ValidationService:
    def validate(self, file_path):
        return run_validation(file_path)
