from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "fixed_code"
REPORT_DIR = PROJECT_ROOT / "reports"

CPP_STANDARD = "c99"
MISRA_VERSION = "MISRA C:2012"

ENABLE_AI = True
ENABLE_CPPCHECK = True
ENABLE_CLANG = False

RULE_ENGINE_CONFIG = {
    "enabled_rules": None,
    "disabled_rules": [],
    "enabled_chapters": None,
    "disabled_chapters": [],
    "enabled_categories": None,
    "disabled_categories": [],
    "minimum_priority": None,
}


def ensure_runtime_directories():
    for directory in (INPUT_DIR, OUTPUT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)