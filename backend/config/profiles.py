"""
Predefined analysis profiles.
"""

FULL_PROFILE = {
    "name": "full",
    "description": "Execute every enabled MISRA rule.",
    "enabled_categories": None,
}

FAST_PROFILE = {
    "name": "fast",
    "description": "Skip expensive semantic rules.",
    "enabled_capabilities": (
        "text",
    ),
}

SEMANTIC_PROFILE = {
    "name": "semantic",
    "description": "Execute only semantic rules.",
    "enabled_capabilities": (
        "semantic",
        "ast",
        "hybrid",
    ),
}

PROFILES = {
    "full": FULL_PROFILE,
    "fast": FAST_PROFILE,
    "semantic": SEMANTIC_PROFILE,
}