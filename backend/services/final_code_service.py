from services.patch_service import PatchService


class FinalCodeService:
    def __init__(self):
        self.patch_service = PatchService()

    def generate(self, original_code, patches, session=None):
        if session is not None:
            for patch in patches:
                self.patch_service.enqueue_patch(session, patch)
        return self.patch_service.apply_patches(original_code, patches)
