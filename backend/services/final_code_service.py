from services.fix_service import FixService


class FinalCodeService:
    def __init__(self):
        self.fix_service = FixService()

    def generate(self, original_code, patches):
        return self.fix_service.apply_patches(original_code, patches)
