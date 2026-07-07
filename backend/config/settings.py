from pathlib import Path

# ------------------------------------------------------------------
# Project Paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_ROOT = PROJECT_ROOT / "backend"

INPUT_DIR = PROJECT_ROOT / "input"

OUTPUT_DIR = PROJECT_ROOT / "fixed_code"

REPORT_DIR = PROJECT_ROOT / "reports"

LOG_DIR = PROJECT_ROOT / "logs"

TEMP_DIR = PROJECT_ROOT / "temp"

# ------------------------------------------------------------------
# MISRA Configuration
# ------------------------------------------------------------------

CPP_STANDARD = "c99"

MISRA_VERSION = "MISRA C:2012"

# ------------------------------------------------------------------
# Feature Flags
# ------------------------------------------------------------------

ENABLE_AI = True

ENABLE_CPPCHECK = True

ENABLE_CLANG = False

DEBUG_MODE = False

SAVE_INTERMEDIATE_FILES = False

# ------------------------------------------------------------------
# Rule Engine Configuration
# ------------------------------------------------------------------

RULE_ENGINE_CONFIG = {
    "enabled_rules": None,
    "disabled_rules": [],
    "enabled_chapters": None,
    "disabled_chapters": [],
    "enabled_categories": None,
    "disabled_categories": [],
    "minimum_priority": None,
}

# ------------------------------------------------------------------
# Application Defaults
# ------------------------------------------------------------------

DEFAULT_CONFIDENCE = 1.0

DEFAULT_ENCODING = "utf-8"

SUPPORTED_SOURCE_EXTENSIONS = (
    ".c",
)

MAX_UPLOAD_SIZE_MB = 10

# ------------------------------------------------------------------
# Runtime Helpers
# ------------------------------------------------------------------


def ensure_runtime_directories():
    """
    Create all runtime folders if missing.
    """

    for directory in (
        INPUT_DIR,
        OUTPUT_DIR,
        REPORT_DIR,
        LOG_DIR,
        TEMP_DIR,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )