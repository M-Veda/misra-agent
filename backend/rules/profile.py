FAST = {
    "text",
}

SEMANTIC = {
    "text",
    "semantic",
}

FULL = {
    "text",
    "ast",
    "semantic",
}


def profile_capabilities(profile):

    profile = profile.lower()

    if profile == "fast":
        return FAST

    if profile == "semantic":
        return SEMANTIC

    return FULL