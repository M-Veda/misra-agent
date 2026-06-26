import re


def find_matches(pattern, code, flags=0):
    return list(re.finditer(pattern, code, flags))


def find_lines(pattern, code, flags=0):
    matches = []

    for match in re.finditer(pattern, code, flags):
        line = code.count("\n", 0, match.start()) + 1
        matches.append((match, line))

    return matches